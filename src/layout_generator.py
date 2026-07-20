from typing import Dict, Any, List
import re
from dotenv import load_dotenv
import os

# Carregar variáveis de ambiente
load_dotenv()


class LayoutGenerator:
    """Classe para gerar registros no layout NFTS."""
    
    def __init__(self):
        inscricao = os.getenv("INSCRICAO_MUNICIPAL_SUJEITO_PASSIVO")
        
        if not inscricao:
            raise ValueError(
                "A variável de ambiente INSCRICAO_MUNICIPAL_SUJEITO_PASSIVO não está definida. "
                "Por favor, defina esta variável no arquivo .env."
            )
        
        if not inscricao.isdigit() or len(inscricao) != 8:
            raise ValueError(
                f"A variável de ambiente INSCRICAO_MUNICIPAL_SUJEITO_PASSIVO deve conter exatamente 8 dígitos numéricos. "
                f"Valor atual: '{inscricao}'"
            )
        
        self.inscricao_municipal = inscricao
        self.versao_arquivo = "001"
    
    def format_numeric_value(self, value: Any, length: int) -> str:
        """
        Formata valores numéricos com zeros à esquerda.
        Exemplo: R$ 168870,20 → 000000016887024
        """
        if value is None:
            return "0" * length
        
        try:
            # Remover caracteres não numéricos
            if isinstance(value, str):
                value = re.sub(r'[^\d.,]', '', value)
                # Substituir vírgula por ponto para conversão
                value = value.replace(',', '.')
            
            # Converter para float e remover decimais
            numeric_value = float(value)
            # Multiplicar por 100 para remover casas decimais
            int_value = int(round(numeric_value * 100))
            
            # Formatar com zeros à esquerda
            return str(int_value).zfill(length)
        except:
            return "0" * length
    
    def normalize_text(self, value: Any) -> str:
        """
        Normaliza texto removendo quebras de linha e espaços extras.
        Substitui quebras de linha por espaços.
        """
        if value is None:
            return ""
        
        text = str(value)
        # Substituir quebras de linha por espaços
        text = text.replace('\r\n', ' ').replace('\n', ' ').replace('\r', ' ')
        # Remover espaços múltiplos
        text = ' '.join(text.split())
        return text.strip()
    
    def format_text_value(self, value: Any, length: int) -> str:
        """
        Formata valores textuais alinhados à esquerda com espaços à direita.
        """
        if value is None:
            return " " * length
        
        text = self.normalize_text(value)
        # Truncar se necessário
        if len(text) > length:
            text = text[:length]
        # Preencher com espaços à direita
        return text.ljust(length)
    
    def format_percentage(self, value: Any) -> str:
        """
        Converte porcentagem para formato de 4 dígitos.
        Exemplo: 5,00% → 0500
        """
        if value is None:
            return "0000"
        
        try:
            if isinstance(value, str):
                # Remover % e converter
                value = value.replace('%', '').replace(',', '.').strip()
            
            numeric_value = float(value)
            
            # Se o valor for menor que 1, assumir que está em formato decimal (0,02 = 2%)
            # e multiplicar por 100 para converter para porcentagem
            if numeric_value < 1:
                numeric_value = numeric_value * 100
            
            # Multiplicar por 100 para remover casas decimais
            int_value = int(round(numeric_value * 100))
            return str(int_value).zfill(4)
        except:
            return "0000"
    
    def format_service_code(self, code: Any) -> str:
        """
        Converte código de serviço para formato de 4 dígitos.
        Exemplo: 1.01 → 0101
        """
        if code is None:
            return "0000"
        
        try:
            # Remover pontos
            code_str = str(code).replace('.', '').strip()
            # Preencher com zeros à esquerda
            return code_str.zfill(4)
        except:
            return "0000"
    
    def format_service_code_tomado(self, code: Any) -> str:
        """
        Formata código do serviço tomado para 5 dígitos com zeros à esquerda.
        Se tiver mais de 5 caracteres, truncar e logar warning.
        Exemplo: 2800 → 02800, 123456 → 12345 (truncado)
        """
        if code is None:
            return "00000"
        
        # Converter para string e remover caracteres não numéricos
        code_str = str(code)
        code_str = re.sub(r'[^\d]', '', code_str)
        
        # Se for maior que 5, truncar e logar warning
        if len(code_str) > 5:
            import warnings
            warnings.warn(f"Código do Serviço truncado de {code_str} para {code_str[:5]} (máximo 5 caracteres)")
            code_str = code_str[:5]
        
        # Preencher com zeros à esquerda para ter exatamente 5 caracteres
        return code_str.zfill(5)
    
    def has_letters(self, value: Any) -> bool:
        """Verifica se uma string contém letras."""
        if value is None:
            return False
        return any(c.isalpha() for c in str(value))
    
    def generate_header_record(self, table_data: List[Dict[str, Any]]) -> str:
        """
        Gera registro tipo 1 (Cabeçalho).
        """
        from datetime import datetime
        
        # Encontrar menor e maior data de emissão
        dates_formatted = []
        for row in table_data:
            dt_emissao = row.get("DT EMISSAO")
            if dt_emissao:
                if isinstance(dt_emissao, datetime):
                    date_str = dt_emissao.strftime("%Y%m%d")
                    dates_formatted.append(date_str)
        
        if dates_formatted:
            data_inicio = min(dates_formatted)
            data_fim = max(dates_formatted)
        else:
            data_inicio = "20260511"
            data_fim = "20260511"
        
        # Montar registro
        record = (
            "1" +  # Tipo de registro
            self.versao_arquivo +  # Versão do arquivo
            self.inscricao_municipal +  # Inscrição Municipal
            data_inicio +  # Data de Início do Período
            data_fim  # Data de Fim do Período
        )
        
        # Adicionar CRLF
        return record + "\r\n"
    
    def generate_detail_record(self, row_data: Dict[str, Any]) -> str:
        """
        Gera registro tipo 4 (Detalhe).
        """
        # Extrair valores do Excel (usar chaves normalizadas - sem acentos, maiúsculas)
        invoice = row_data.get("INVOICE", "")
        dt_emissao = row_data.get("DT EMISSAO", "")
        moeda_nacional = row_data.get("MOEDA NACIONAL", 0)
        codigo_servico_excel = row_data.get("CODIGO SERVICO", "")
        codigo_servico_lei = row_data.get("CODIGO SERVICOS LEI 116", "")
        percent_iss = row_data.get("% ISS", 0)
        fornecedor = row_data.get("FORNECEDOR", "")
        endereco = row_data.get("ENDERECO", "")
        # Usar chave normalizada (sem espaços duplos)
        descricao_servicos = row_data.get("DESCRICAO SERVICOS CONF. EMAIL ENVIADO", "")
        
        # Número do documento (zeros se tiver letras)
        if self.has_letters(invoice):
            numero_documento = "0" * 12
        else:
            # Remover caracteres não numéricos
            invoice_clean = re.sub(r'[^\d]', '', str(invoice))
            # Se for maior que 12, truncar
            if len(invoice_clean) > 12:
                invoice_clean = invoice_clean[:12]
            # Preencher com zeros à esquerda para ter exatamente 12 caracteres
            numero_documento = invoice_clean.zfill(12)
        
        # Data da prestação - usar conversão do ExcelReader se for serial
        if dt_emissao:
            from datetime import datetime
            if isinstance(dt_emissao, datetime):
                data_prestacao = dt_emissao.strftime("%Y%m%d")
            else:
                # Tentar converter como número serial do Excel
                try:
                    # Se for número, converter usando lógica do Excel
                    if isinstance(dt_emissao, (int, float)):
                        dt = datetime.fromordinal(datetime(1900, 1, 1).toordinal() + int(dt_emissao) - 2)
                        data_prestacao = dt.strftime("%Y%m%d")
                    else:
                        # Se for string, remover hora e formatar
                        data_str = str(dt_emissao)
                        if ' ' in data_str:
                            data_str = data_str.split(' ')[0]
                        data_prestacao = data_str.replace('-', '').replace('/', '')
                        # Se tiver 7 dígitos (ex: 260511), adicionar ano 202
                        if len(data_prestacao) == 7 and data_prestao.isdigit():
                            data_prestacao = "202" + data_prestacao
                        # Se tiver 8 dígitos mas começar com 0 (ex: 0260430), adicionar 20
                        elif len(data_prestacao) == 7 and data_prestao.startswith('0'):
                            data_prestacao = "20" + data_prestacao[1:]
                except:
                    data_prestacao = "20260511"
        else:
            data_prestacao = "20260511"
        
        # Valor dos serviços
        valor_servicos = self.format_numeric_value(moeda_nacional, 15)
        
        # Valor das deduções (fixo zeros)
        valor_deducoes = "0" * 15
        
        # Código do serviço tomado (da coluna CÓDIGO DO SERVIÇO do Excel)
        codigo_servico_tomado = self.format_service_code_tomado(codigo_servico_excel)
        
        # Código do subitem
        codigo_subitem = self.format_service_code(codigo_servico_lei)
        
        # Alíquota
        aliquota = self.format_percentage(percent_iss)
        
        # Nome/Razão Social do prestador
        nome_prestador = self.format_text_value(fornecedor, 75)
        
        # Endereço (50 chars) + Complemento (30 chars)
        endereco_str = self.normalize_text(endereco) if endereco else ""
        if len(endereco_str) > 50:
            endereco_principal = endereco_str[:50]
            complemento = endereco_str[50:80]
        else:
            endereco_principal = endereco_str
            complemento = ""
        
        endereco_prestador = self.format_text_value(endereco_principal, 50)
        complemento_endereco = self.format_text_value(complemento, 30)
        
        # Discriminação dos serviços
        discriminacao = self.normalize_text(descricao_servicos) if descricao_servicos else ""
        if self.has_letters(invoice):
            discriminacao += f", INVOICE: {invoice}"
        
        # Garantir que tenha pelo menos 1 caractere (espaço)
        if not discriminacao or discriminacao.strip() == "":
            discriminacao = " "
        
        # Substituir quebras de linha por pipe conforme especificação
        discriminacao = discriminacao.replace('\r\n', '|').replace('\n', '|').replace('\r', '|')
        
        # Garantir que tenha pelo menos 1 caractere após substituição
        if not discriminacao or discriminacao.strip() == "":
            discriminacao = " "
        
        # Montar registro fixo
        record = (
            "4" +  # Tipo de registro (1)
            "01" +  # Tipo do documento (2)
            "0    " +  # Série do documento (5)
            numero_documento +  # Número do documento (12)
            data_prestacao +  # Data da prestação (8)
            "N" +  # Situação da NFTS (1)
            "T" +  # Tributação do serviço (1)
            valor_servicos +  # Valor dos serviços (15)
            valor_deducoes +  # Valor das deduções (15)
            codigo_servico_tomado +  # Código do serviço tomado (5)
            codigo_subitem +  # Código do subitem (4)
            aliquota +  # Alíquota (4)
            "1" +  # ISS Retido (1)
            "3" +  # Indicador de CPF/CNPJ do prestador (1)
            "0" * 14 +  # CPF ou CNPJ do prestador (14)
            "0" * 8 +  # Inscrição Municipal do prestador (8)
            nome_prestador +  # Nome/Razão Social (75)
            " " * 3 +  # Tipo do endereço (3) - vazio conforme especificação
            endereco_prestador +  # Endereço (50)
            " " * 10 +  # Número do endereço (10)
            complemento_endereco +  # Complemento (30)
            " " * 30 +  # Bairro (30)
            " " * 50 +  # Cidade (50)
            " " * 2 +  # UF (2)
            " " * 8 +  # CEP (8)
            " " * 75 +  # E-mail (75)
            "1" +  # Tipo de NFTS (1)
            "0" +  # Regime de tributação (1)
            " " * 8 +  # Data de pagamento (8)
            discriminacao  # Discriminação dos serviços (variável)
        )
        
        # Adicionar CRLF
        return record + "\r\n"
    
    def generate_footer_record(self, detail_count: int, total_value: str) -> str:
        """
        Gera registro tipo 9 (Rodapé).
        """
        # Número de linhas de detalhe
        num_linhas = str(detail_count).zfill(7)
        
        # Valor total dos serviços
        valor_total = total_value
        
        # Valor total das deduções (fixo zeros)
        valor_deducoes_total = "0" * 15
        
        # Montar registro
        record = (
            "9" +  # Tipo de registro
            num_linhas +  # Número de linhas de detalhe
            valor_total +  # Valor total dos serviços
            valor_deducoes_total  # Valor total das deduções
        )
        
        # Adicionar CRLF
        return record + "\r\n"
    
    def generate_file(self, table_data: List[Dict[str, Any]], output_path: str) -> tuple:
        """
        Gera arquivo completo com cabeçalho, detalhes e rodapé.
        Retorna (sucesso, mensagem, total_value)
        """
        try:
            with open(output_path, 'w', encoding='iso-8859-1', newline='') as f:
                # Gerar cabeçalho
                header = self.generate_header_record(table_data)
                f.write(header)
                
                # Gerar detalhes e calcular total
                total_value = 0
                for row in table_data:
                    detail = self.generate_detail_record(row)
                    f.write(detail)
                    # Extrair valor dos serviços do detalhe gerado (posições 30-44, 0-indexed)
                    valor_servicos = detail[30:45]
                    total_value += int(valor_servicos) if valor_servicos.isdigit() else 0
                
                # Gerar rodapé
                footer = self.generate_footer_record(len(table_data), str(total_value).zfill(15))
                f.write(footer)
            
            return True, f"Arquivo gerado com sucesso: {output_path}", str(total_value).zfill(15)
        except Exception as e:
            return False, f"Erro ao gerar arquivo: {str(e)}", "0" * 15
