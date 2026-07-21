import sys
import os
import argparse
from datetime import datetime
from typing import List, Dict, Any
import tkinter as tk
from tkinter import filedialog


def _ensure_src_in_path() -> None:
    """Garante que o diretório src esteja no PYTHONPATH."""
    src_dir = os.path.dirname(os.path.abspath(__file__))
    if src_dir not in sys.path:
        sys.path.insert(0, src_dir)


_ensure_src_in_path()

from excel_reader import ExcelReader
from layout_generator import LayoutGenerator, DEFAULT_DATE
from validator import Validator


class NFTSGenerator:
    """Classe principal para orquestrar a geração de arquivos NFTS."""
    
    def __init__(self, excel_path: str, output_dir: str = "output", log_dir: str = "logs"):
        self.excel_path = excel_path
        self.output_dir = output_dir
        self.log_dir = log_dir
        self.log_file = None
        
        # Criar diretórios se não existirem
        os.makedirs(self.output_dir, exist_ok=True)
        os.makedirs(self.log_dir, exist_ok=True)
        
        # Inicializar componentes
        self.excel_reader = ExcelReader(excel_path)
        self.layout_generator = LayoutGenerator()
        self.validator = Validator()
        
        # Estatísticas
        self.tables_processed = 0
        self.files_generated = 0
        self.files_validated = 0
        self.errors = []
    
    def setup_logging(self) -> None:
        """Configura arquivo de log."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        log_filename = f"processamento_{timestamp}.log"
        log_path = os.path.join(self.log_dir, log_filename)
        self.log_file = open(log_path, 'w', encoding='utf-8')
        self.log(f"Iniciando processamento em {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
        self.log(f"Arquivo Excel: {self.excel_path}")
    
    def log(self, message: str) -> None:
        """Registra mensagem no log e console."""
        timestamp = datetime.now().strftime("%H:%M:%S")
        log_message = f"[{timestamp}] {message}"
        print(log_message)
        if self.log_file:
            self.log_file.write(log_message + "\n")
            self.log_file.flush()
    
    def log_error(self, message: str) -> None:
        """Registra erro no log e console."""
        timestamp = datetime.now().strftime("%H:%M:%S")
        log_message = f"[{timestamp}] ERRO: {message}"
        print(log_message)
        if self.log_file:
            self.log_file.write(log_message + "\n")
            self.log_file.flush()
        self.errors.append(message)
    
    def close_logging(self) -> None:
        """Fecha arquivo de log."""
        if self.log_file:
            self.log(f"Processamento finalizado em {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
            self.log_file.close()
    
    def get_date_range_from_table(self, table_data: List[Dict[str, Any]]) -> tuple:
        """
        Extrai menor e maior data de emissão da tabela.
        Retorna (data_inicio, data_fim) no formato AAAAMMDD.
        """
        dates = []
        for row in table_data:
            dt_emissao = row.get("DT EMISSAO")
            if dt_emissao:
                # Converter data serial do Excel se necessário
                date_str = self.excel_reader.convert_excel_date(dt_emissao)
                if date_str:
                    dates.append(date_str)
        
        if dates:
            return min(dates), max(dates)
        else:
            return DEFAULT_DATE, DEFAULT_DATE  # Valores padrão
    
    def _load_excel(self) -> bool:
        """Carrega o arquivo Excel."""
        try:
            self.log("Carregando arquivo Excel...")
            self.excel_reader.read_excel_file()
            self.log("Arquivo Excel carregado com sucesso")
            return True
        except (FileNotFoundError, PermissionError, OSError) as e:
            self.log_error(f"Erro ao carregar arquivo Excel: {str(e)}")
            return False
        except Exception as e:
            self.log_error(f"Erro inesperado ao carregar Excel: {str(e)}")
            return False
    
    def _filter_table_data(self, table_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Filtra registros com coluna NFTS preenchida."""
        return [row for row in table_data if not row.get("NFTS")]
    
    def _process_table(self, idx: int, table_info: Dict[str, Any]) -> bool:
        """Processa uma única tabela e gera arquivo NFTS."""
        table_data = table_info['data']
        header_row = table_info['header_row']
        
        filtered_data = self._filter_table_data(table_data)
        
        self.log(f"\nProcessando tabela {idx} (linha {header_row})")
        self.log(f"  Total de registros na tabela: {len(table_data)}")
        self.log(f"  Registros com NFTS preenchida: {len(table_data) - len(filtered_data)}")
        self.log(f"  Registros para processar: {len(filtered_data)}")
        
        self.tables_processed += 1
        
        if not filtered_data:
            self.log(f"Tabela {idx} não possui registros para inserir (todos têm NFTS preenchida)")
            return False
        
        try:
            data_inicio, data_fim = self.get_date_range_from_table(filtered_data)
            filename = f"NFTS_{data_inicio}_{data_fim}.txt"
            output_path = os.path.join(self.output_dir, filename)
            
            self.log(f"Gerando arquivo: {filename}")
            success, message, total_value = self.layout_generator.generate_file(filtered_data, output_path)
            
            if not success:
                self.log_error(message)
                return False
            
            self.log(message)
            self.files_generated += 1
            
            self.log("Validando arquivo gerado...")
            is_valid, errors, warnings = self.validator.validate_file_layout(output_path)
            
            if is_valid:
                self.log(f"Arquivo validado com sucesso (Total: {total_value})")
                self.files_validated += 1
                return True
            else:
                self.log_error(f"Validação falhou: {', '.join(errors)}")
                for warning in warnings:
                    self.log(f"Aviso: {warning}")
                return False
                
        except Exception as e:
            self.log_error(f"Erro ao processar tabela {idx}: {str(e)}")
            return False
    
    def process(self) -> bool:
        """
        Processa o arquivo Excel e gera arquivos NFTS.
        Retorna True se processamento concluído com sucesso.
        """
        try:
            self.setup_logging()
            
            if not self._load_excel():
                return False
            
            self.log("Detectando tabelas...")
            tables = self.excel_reader.detect_all_tables()
            self.log(f"Encontradas {len(tables)} tabela(s)")
            
            if not tables:
                self.log_error("Nenhuma tabela encontrada no arquivo Excel")
                return False
            
            for idx, table_info in enumerate(tables, 1):
                self._process_table(idx, table_info)
            
            self.excel_reader.close()
            self.generate_final_report()
            
            return len(self.errors) == 0
            
        except Exception as e:
            self.log_error(f"Erro fatal no processamento: {str(e)}")
            return False
        finally:
            self.close_logging()
    
    def generate_final_report(self) -> None:
        """Gera relatório final do processamento."""
        self.log("\n" + "=" * 60)
        self.log("RELATÓRIO FINAL")
        self.log("=" * 60)
        self.log(f"Tabelas processadas: {self.tables_processed}")
        self.log(f"Arquivos gerados: {self.files_generated}")
        self.log(f"Arquivos validados: {self.files_validated}")
        self.log(f"Erros encontrados: {len(self.errors)}")
        
        if self.errors:
            self.log("\nErros:")
            for error in self.errors:
                self.log(f"  - {error}")
        
        self.log("=" * 60)


def select_excel_file():
    """Abre diálogo de seleção de arquivo Excel usando tkinter."""
    root = tk.Tk()
    root.withdraw()  # Ocultar janela principal
    
    # Forçar a janela a aparecer
    root.lift()
    root.attributes('-topmost', True)
    root.after_idle(root.attributes, '-topmost', False)
    
    file_path = filedialog.askopenfilename(
        title='Selecione o arquivo Excel',
        filetypes=[
            ('Arquivos Excel', '*.xlsx *.xls'),
            ('Todos os arquivos', '*.*')
        ]
    )
    
    root.destroy()
    return file_path


def main():
    """Função principal para execução via linha de comando."""
    parser = argparse.ArgumentParser(description="Gerador de arquivos NFTS a partir de Excel")
    parser.add_argument("excel_file", nargs='?', help="Caminho do arquivo Excel de entrada (opcional - abre diálogo se não fornecido)")
    parser.add_argument("--output", default="output", help="Diretório de saída (default: output)")
    parser.add_argument("--logs", default="logs", help="Diretório de logs (default: logs)")
    
    args = parser.parse_args()
    
    # Se nenhum arquivo for fornecido, abrir diálogo de seleção
    if not args.excel_file:
        print("Nenhum arquivo Excel especificado. Abrindo seletor de arquivo...")
        args.excel_file = select_excel_file()
        
        if not args.excel_file:
            print("Nenhum arquivo selecionado. Operação cancelada.")
            sys.exit(1)
    
    # Verificar se arquivo existe
    if not os.path.exists(args.excel_file):
        print(f"Erro: Arquivo não encontrado: {args.excel_file}")
        sys.exit(1)
    
    # Executar processamento
    generator = NFTSGenerator(args.excel_file, args.output, args.logs)
    success = generator.process()
    
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
