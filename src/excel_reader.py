import openpyxl
from datetime import datetime
from typing import List, Dict, Any, Optional
import unicodedata
from difflib import SequenceMatcher


class ExcelReader:
    """Classe para ler e extrair tabelas de arquivos Excel."""
    
    # Lista de colunas esperadas (normalizadas - sem acentos, maiúsculo)
    EXPECTED_COLUMNS = [
        "CONTRATO",
        "CODIGO BACEN",
        "FORNECEDOR",
        "INVOICE",
        "DT EMISSAO",
        "DESCRICAO SERVICOS CONF. EMAIL ENVIADO",
        "MOEDA ESTRANGEIRA",
        "TAXA",
        "MOEDA",
        "MOEDA NACIONAL",
        "CODIGO SERVICO",
        "CODIGO SERVICOS LEI 116",
        "% ISS",
        "ISS",
        "NFTS",
        "ENDERECO",
        "OBSERVACOES",
        "STATUS"
    ]
    
    def __init__(self, file_path: str):
        self.file_path = file_path
        self.workbook = None
        self.worksheet = None
        
    def read_excel_file(self) -> None:
        """Carrega o arquivo Excel usando openpyxl com data_only=True para obter valores calculados."""
        self.workbook = openpyxl.load_workbook(self.file_path, data_only=True)
        self.worksheet = self.workbook.active
        
    def normalize_header(self, value: Any) -> str:
        """
        Normaliza valor de célula para comparação de cabeçalhos.
        Remove espaços, quebras de linha, acentos e converte para maiúsculo.
        """
        if value is None:
            return ""
        
        # Converter para string e remover quebras de linha
        text = str(value).replace('\r', ' ').replace('\n', ' ')
        
        # Remover acentos
        text = unicodedata.normalize('NFKD', text).encode('ASCII', 'ignore').decode('ASCII')
        
        # Converter para maiúsculo
        text = text.upper()
        
        # Remover espaços extras e normalizar
        text = ' '.join(text.split())
        
        return text.strip()
    
    def fuzzy_match(self, str1: str, str2: str, threshold: float = 0.7) -> bool:
        """
        Verifica se duas strings são similares usando fuzzy matching.
        Retorna True se a similaridade for maior que o threshold.
        """
        if not str1 or not str2:
            return False
        
        # Normalizar ambas as strings
        norm1 = self.normalize_header(str1)
        norm2 = self.normalize_header(str2)
        
        # Calcular similaridade usando SequenceMatcher
        similarity = SequenceMatcher(None, norm1, norm2).ratio()
        
        return similarity >= threshold
    
    def find_table_headers(self, start_row: int = 10) -> Optional[int]:
        """
        Localiza cabeçalhos de tabelas a partir de uma linha específica.
        Procura pelo cabeçalho específico com as colunas esperadas.
        """
        for row in range(start_row, self.worksheet.max_row + 1):
            headers_found = []
            for col in range(2, 19):  # Colunas B (2) a R (18)
                cell_value = self.worksheet.cell(row=row, column=col).value
                if cell_value:
                    headers_found.append(self.normalize_header(cell_value))
            
            # Verificar se encontrou pelo menos a maioria dos cabeçalhos usando fuzzy matching
            matches = 0
            for expected in self.EXPECTED_COLUMNS:
                # Verificar se algum cabeçalho encontrado faz fuzzy match com o esperado
                for found in headers_found:
                    if self.fuzzy_match(expected, found, threshold=0.7):
                        matches += 1
                        break
            
            if matches >= len(self.EXPECTED_COLUMNS) - 3:  # Tolerância de 3 diferenças (para CÓDIGO DO SERVIÇO opcional)
                return row
                
        return None
    
    def extract_table_data(self, start_row: int) -> List[Dict[str, Any]]:
        """
        Extrai dados de uma tabela começando na linha do cabeçalho.
        Retorna quando a coluna B estiver vazia.
        Usa fuzzy matching para mapear colunas encontradas para nomes esperados.
        """
        # Primeiro, extrair os cabeçalhos originais e normalizados
        headers_original = []
        headers_normalized = []
        for col in range(2, 19):  # Colunas B a R
            cell_value = self.worksheet.cell(row=start_row, column=col).value
            if cell_value:
                headers_original.append(str(cell_value))
                headers_normalized.append(self.normalize_header(cell_value))
            else:
                headers_original.append("")
                headers_normalized.append("")
        
        # Criar mapeamento usando fuzzy matching
        column_mapping = {}
        for idx, header_norm in enumerate(headers_normalized):
            if not header_norm:
                continue
            
            # Encontrar melhor correspondência com fuzzy matching
            best_match = None
            best_similarity = 0
            
            for expected in self.EXPECTED_COLUMNS:
                if self.fuzzy_match(header_norm, expected, threshold=0.6):
                    similarity = SequenceMatcher(None, header_norm, expected).ratio()
                    if similarity > best_similarity:
                        best_similarity = similarity
                        best_match = expected
            
            # Usar o nome esperado se houver match, senão usar o normalizado
            if best_match:
                column_mapping[idx] = best_match
            else:
                column_mapping[idx] = header_norm
        
        table_data = []
        
        # Extrair linhas de dados
        for row in range(start_row + 1, self.worksheet.max_row + 1):
            # Verificar se coluna B está vazia (fim da tabela)
            first_col_value = self.worksheet.cell(row=row, column=2).value
            if first_col_value is None or str(first_col_value).strip() == "":
                break
            
            # Extrair valores da linha usando o mapeamento de colunas
            row_data = {}
            for col_idx in range(2, 19):
                cell_value = self.worksheet.cell(row=row, column=col_idx).value
                # Usar o nome mapeado como chave
                mapped_name = column_mapping.get(col_idx - 2, "")
                if mapped_name:
                    row_data[mapped_name] = cell_value
            
            table_data.append(row_data)
        
        return table_data
    
    def detect_all_tables(self) -> List[Dict[str, Any]]:
        """
        Identifica todas as tabelas no arquivo.
        Busca cabeçalhos até 10 linhas após o fim da tabela anterior.
        """
        tables = []
        current_row = 10  # Começa a buscar a partir da linha 10
        
        while current_row <= self.worksheet.max_row:
            header_row = self.find_table_headers(current_row)
            
            if header_row is None:
                break
            
            # Extrair dados da tabela
            table_data = self.extract_table_data(header_row)
            
            if table_data:
                tables.append({
                    'header_row': header_row,
                    'data': table_data
                })
            
            # Buscar próxima tabela até 10 linhas após o fim desta
            current_row = header_row + len(table_data) + 1
            max_search_row = current_row + 10
            
            # Procurar próximo cabeçalho no intervalo
            next_header = None
            for search_row in range(current_row, min(max_search_row + 1, self.worksheet.max_row + 1)):
                if self.find_table_headers(search_row) == search_row:
                    next_header = search_row
                    break
            
            if next_header is None:
                break
            
            current_row = next_header
        
        return tables
    
    def convert_excel_date(self, serial_date) -> str:
        """
        Converte data serial do Excel para formato AAAAMMDD.
        """
        if serial_date is None:
            return ""
        
        try:
            if isinstance(serial_date, datetime):
                return serial_date.strftime("%Y%m%d")
            else:
                # Converter serial do Excel para datetime
                dt = datetime.fromordinal(datetime(1900, 1, 1).toordinal() + int(serial_date) - 2)
                return dt.strftime("%Y%m%d")
        except:
            return ""
    
    def close(self) -> None:
        """Fecha o arquivo Excel."""
        if self.workbook:
            self.workbook.close()
