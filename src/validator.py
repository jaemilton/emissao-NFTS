from typing import List, Tuple, Dict, Any
import re
import sys
import os

# Adicionar diretório src ao path para importar constantes
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from layout_generator import (
    DATE_LENGTH, INSCRICAO_LENGTH, VERSION_LENGTH, SERVICE_VALUE_LENGTH,
    DEDUCTION_VALUE_LENGTH, DETAIL_VALUE_START, DETAIL_VALUE_END,
    DETAIL_DEDUCTION_START, DETAIL_DEDUCTION_END, DETAIL_SERVICE_CODE_START,
    DETAIL_SERVICE_CODE_END, DETAIL_SUBITEM_START, DETAIL_SUBITEM_END,
    DETAIL_ALIQUOTA_START, DETAIL_ALIQUOTA_END
)


class Validator:
    """Classe para validar arquivos .txt gerados contra layout NFTS."""
    
    def __init__(self):
        self.errors = []
        self.warnings = []
    
    def validate_file_layout(self, file_path: str) -> Tuple[bool, List[str], List[str]]:
        """
        Valida arquivo completo contra layout.
        Retorna (sucesso, erros, avisos).
        """
        self.errors = []
        self.warnings = []
        
        try:
            with open(file_path, 'r', encoding='iso-8859-1') as f:
                lines = f.readlines()
            
            if not lines:
                self.errors.append("Arquivo vazio")
                return False, self.errors, self.warnings
            
            # Validar primeiro registro (cabeçalho)
            if not self.validate_header_record(lines[0]):
                self.errors.append("Erro na validação do registro cabeçalho")
            
            # Validar registros de detalhe
            detail_count = 0
            total_value = 0
            for i, line in enumerate(lines[1:-1], 1):
                if line.strip():  # Ignorar linhas vazias
                    if not self.validate_detail_record(line):
                        self.errors.append(f"Erro na validação do registro detalhe linha {i+1}")
                    # Extrair valor dos serviços para validação do rodapé
                    valor_servicos = line[DETAIL_VALUE_START:DETAIL_VALUE_END]
                    if valor_servicos.isdigit():
                        total_value += int(valor_servicos)
                    detail_count += 1
            
            # Validar último registro (rodapé)
            if lines[-1].strip():
                if not self.validate_footer_record(lines[-1], detail_count, total_value):
                    self.errors.append("Erro na validação do registro rodapé")
            
            return len(self.errors) == 0, self.errors, self.warnings
            
        except Exception as e:
            self.errors.append(f"Erro ao ler arquivo: {str(e)}")
            return False, self.errors, self.warnings
    
    def validate_header_record(self, record: str) -> bool:
        """
        Valida registro tipo 1 (Cabeçalho).
        Tamanho esperado: 30 caracteres + CRLF
        """
        # Remover CRLF para validação
        record_clean = record.rstrip('\r\n')
        
        # Tamanho esperado: 1 + 3 + 8 + 8 + 8 = 28
        expected_size = 1 + VERSION_LENGTH + INSCRICAO_LENGTH + DATE_LENGTH + DATE_LENGTH
        
        # Validar tamanho
        if len(record_clean) != expected_size:
            self.errors.append(f"Cabeçalho: tamanho incorreto ({len(record_clean)} caracteres, esperado {expected_size})")
            return False
        
        # Validar tipo de registro
        if record_clean[0] != '1':
            self.errors.append("Cabeçalho: tipo de registro deve ser '1'")
            return False
        
        # Validar versão (deve ser numérica)
        versao_end = 1 + VERSION_LENGTH
        versao = record_clean[1:versao_end]
        if not versao.isdigit():
            self.errors.append("Cabeçalho: versão deve ser numérica")
            return False
        
        # Validar inscrição municipal (deve ser numérica)
        insc_start = versao_end
        insc_end = insc_start + INSCRICAO_LENGTH
        inscricao = record_clean[insc_start:insc_end]
        if not inscricao.isdigit():
            self.errors.append("Cabeçalho: inscrição municipal deve ser numérica")
            return False
        
        # Validar datas (deve ser AAAAMMDD)
        data_start = insc_end
        data_inicio = record_clean[data_start:data_start + DATE_LENGTH]
        data_fim = record_clean[data_start + DATE_LENGTH:data_start + 2 * DATE_LENGTH]
        
        if not self._validate_date_format(data_inicio):
            self.errors.append(f"Cabeçalho: data de início inválida ({data_inicio})")
            return False
        
        if not self._validate_date_format(data_fim):
            self.errors.append(f"Cabeçalho: data de fim inválida ({data_fim})")
            return False
        
        return True
    
    def validate_detail_record(self, record: str) -> bool:
        """
        Valida registro tipo 4 (Detalhe).
        Tamanho mínimo: 440 caracteres fixos + pelo menos 1 de discriminação = 441
        """
        record_clean = record.rstrip('\r\n')
        
        # Validar tamanho mínimo (440 campos fixos + pelo menos 1 caractere de discriminação)
        if len(record_clean) < 440:
            self.errors.append(f"Detalhe: tamanho abaixo do mínimo ({len(record_clean)} caracteres, mínimo 440)")
            return False
        
        # Validar tipo de registro
        if record_clean[0] != '4':
            self.errors.append("Detalhe: tipo de registro deve ser '4'")
            return False
        
        # Validar tipo do documento (posições 1-2, deve ser numérico)
        tipo_doc = record_clean[1:3]
        if not tipo_doc.isdigit():
            self.errors.append("Detalhe: tipo do documento deve ser numérico")
            return False
        
        # Validar número do documento
        numero_doc = record_clean[8:8 + 12]
        if not numero_doc.isdigit():
            self.errors.append("Detalhe: número do documento deve ser numérico")
            return False
        
        # Validar data de prestação
        data_prestacao = record_clean[20:20 + DATE_LENGTH]
        if not self._validate_date_format(data_prestacao):
            self.errors.append(f"Detalhe: data de prestação inválida ({data_prestacao})")
            return False
        
        # Validar valor dos serviços
        valor_servicos = record_clean[DETAIL_VALUE_START:DETAIL_VALUE_END]
        if not valor_servicos.isdigit():
            self.errors.append("Detalhe: valor dos serviços deve ser numérico")
            return False
        
        # Validar valor das deduções
        valor_deducoes = record_clean[DETAIL_DEDUCTION_START:DETAIL_DEDUCTION_END]
        if not valor_deducoes.isdigit():
            self.errors.append("Detalhe: valor das deduções deve ser numérico")
            return False
        
        # Validar código do serviço
        codigo_servico = record_clean[DETAIL_SERVICE_CODE_START:DETAIL_SERVICE_CODE_END]
        if not codigo_servico.isdigit():
            self.errors.append("Detalhe: código do serviço deve ser numérico")
            return False
        
        # Validar código do subitem
        codigo_subitem = record_clean[DETAIL_SUBITEM_START:DETAIL_SUBITEM_END]
        if not codigo_subitem.isdigit():
            self.errors.append("Detalhe: código do subitem deve ser numérico")
            return False
        
        # Validar alíquota
        aliquota = record_clean[DETAIL_ALIQUOTA_START:DETAIL_ALIQUOTA_END]
        if not aliquota.isdigit():
            self.errors.append("Detalhe: alíquota deve ser numérica")
            return False
        
        return True
    
    def validate_footer_record(self, record: str, expected_detail_count: int, expected_total_value: int) -> bool:
        """
        Valida registro tipo 9 (Rodapé).
        Tamanho esperado: 40 caracteres + CRLF
        """
        record_clean = record.rstrip('\r\n')
        
        # Tamanho esperado: 1 + 7 + 15 + 15 = 38
        expected_size = 1 + 7 + SERVICE_VALUE_LENGTH + DEDUCTION_VALUE_LENGTH
        
        # Validar tamanho
        if len(record_clean) != expected_size:
            self.errors.append(f"Rodapé: tamanho incorreto ({len(record_clean)} caracteres, esperado {expected_size})")
            return False
        
        # Validar tipo de registro
        if record_clean[0] != '9':
            self.errors.append("Rodapé: tipo de registro deve ser '9'")
            return False
        
        # Validar número de linhas de detalhe (posições 1-8)
        num_linhas = record_clean[1:8]
        if not num_linhas.isdigit():
            self.errors.append("Rodapé: número de linhas deve ser numérico")
            return False
        
        num_linhas_int = int(num_linhas)
        if num_linhas_int != expected_detail_count:
            self.errors.append(f"Rodapé: número de linhas incorreto ({num_linhas_int}, esperado {expected_detail_count})")
            return False
        
        # Validar valor total dos serviços (posições 8-23)
        valor_total = record_clean[8:23]
        if not valor_total.isdigit():
            self.errors.append("Rodapé: valor total deve ser numérico")
            return False
        
        valor_total_int = int(valor_total)
        if valor_total_int != expected_total_value:
            self.errors.append(f"Rodapé: valor total incorreto ({valor_total_int}, esperado {expected_total_value})")
            return False
        
        # Validar valor total das deduções (posições 23-38, deve ser numérico)
        valor_deducoes = record_clean[23:38]
        if not valor_deducoes.isdigit():
            self.errors.append("Rodapé: valor total das deduções deve ser numérico")
            return False
        
        return True
    
    def _validate_date_format(self, date_str: str) -> bool:
        """
        Valida formato de data AAAAMMDD.
        """
        if len(date_str) != 8:
            return False
        
        if not date_str.isdigit():
            return False
        
        try:
            year = int(date_str[0:4])
            month = int(date_str[4:6])
            day = int(date_str[6:8])
            
            if year < 1900 or year > 2100:
                return False
            if month < 1 or month > 12:
                return False
            if day < 1 or day > 31:
                return False
            
            return True
        except (ValueError, TypeError):
            return False
    
