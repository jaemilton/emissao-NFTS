import sys
import os
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from layout_generator import LayoutGenerator


class MockLayoutGenerator(LayoutGenerator):
    """Mock do LayoutGenerator para evitar carregar variáveis de ambiente."""
    
    def __init__(self):
        self.inscricao_municipal = "12345678"
        self.versao_arquivo = "001"


class TestFormatNumericValue(unittest.TestCase):
    def setUp(self):
        self.generator = MockLayoutGenerator()
    
    def test_format_currency(self):
        result = self.generator.format_numeric_value("R$ 168870,20", 15)
        self.assertEqual(result, "000000016887020")
    
    def test_format_decimal(self):
        result = self.generator.format_numeric_value(168870.20, 15)
        self.assertEqual(result, "000000016887020")
    
    def test_format_none(self):
        result = self.generator.format_numeric_value(None, 15)
        self.assertEqual(result, "0" * 15)
    
    def test_format_invalid(self):
        result = self.generator.format_numeric_value("abc", 15)
        self.assertEqual(result, "0" * 15)


class TestFormatPercentage(unittest.TestCase):
    def setUp(self):
        self.generator = MockLayoutGenerator()
    
    def test_format_percentage_string(self):
        result = self.generator.format_percentage("5,00%")
        self.assertEqual(result, "0500")
    
    def test_format_percentage_decimal(self):
        result = self.generator.format_percentage(0.02)
        self.assertEqual(result, "0200")
    
    def test_format_percentage_none(self):
        result = self.generator.format_percentage(None)
        self.assertEqual(result, "0000")


class TestFormatServiceCode(unittest.TestCase):
    def setUp(self):
        self.generator = MockLayoutGenerator()
    
    def test_format_service_code(self):
        result = self.generator.format_service_code("1.01")
        self.assertEqual(result, "0101")
    
    def test_format_service_code_none(self):
        result = self.generator.format_service_code(None)
        self.assertEqual(result, "0000")


class TestFormatServiceCodeTomado(unittest.TestCase):
    def setUp(self):
        self.generator = MockLayoutGenerator()
    
    def test_format_service_code_tomado(self):
        result = self.generator.format_service_code_tomado("2800")
        self.assertEqual(result, "02800")
    
    def test_format_service_code_tomado_none(self):
        result = self.generator.format_service_code_tomado(None)
        self.assertEqual(result, "00000")


class TestNormalizeText(unittest.TestCase):
    def setUp(self):
        self.generator = MockLayoutGenerator()
    
    def test_remove_accents(self):
        result = self.generator.normalize_text("SERVIÇOS DE PESQUISA E CONSULTORIA")
        self.assertEqual(result, "SERVICOS DE PESQUISA E CONSULTORIA")
    
    def test_remove_newlines(self):
        result = self.generator.normalize_text("Linha 1\nLinha 2")
        self.assertEqual(result, "Linha 1 Linha 2")
    
    def test_remove_multiple_spaces(self):
        result = self.generator.normalize_text("Texto    com    espaços")
        self.assertEqual(result, "Texto com espacos")
    
    def test_remove_special_chars(self):
        result = self.generator.normalize_text("Serviço #1 @ Empresa")
        self.assertEqual(result, "Servico #1 @ Empresa")


class TestFormatDate(unittest.TestCase):
    def setUp(self):
        self.generator = MockLayoutGenerator()
    
    def test_format_datetime(self):
        from datetime import datetime
        result = self.generator._format_date(datetime(2026, 5, 11))
        self.assertEqual(result, "20260511")
    
    def test_format_string(self):
        result = self.generator._format_date("2026-05-11")
        self.assertEqual(result, "20260511")
    
    def test_format_none(self):
        result = self.generator._format_date(None)
        self.assertEqual(result, "20260511")


if __name__ == "__main__":
    unittest.main()
