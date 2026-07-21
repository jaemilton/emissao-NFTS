import sys
import os
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from excel_reader import ExcelReader


class TestNormalizeHeader(unittest.TestCase):
    def setUp(self):
        self.reader = ExcelReader("dummy.xlsx")
    
    def test_normalize_accent_uppercase(self):
        result = self.reader.normalize_header("Código do Serviço")
        self.assertEqual(result, "CODIGO DO SERVICO")
    
    def test_normalize_multiple_spaces(self):
        result = self.reader.normalize_header("  DT   EMISSÃO  ")
        self.assertEqual(result, "DT EMISSAO")
    
    def test_normalize_newlines(self):
        result = self.reader.normalize_header("DESCRIÇÃO\nSERVIÇOS")
        self.assertEqual(result, "DESCRICAO SERVICOS")
    
    def test_normalize_none(self):
        result = self.reader.normalize_header(None)
        self.assertEqual(result, "")


class TestFuzzyMatch(unittest.TestCase):
    def setUp(self):
        self.reader = ExcelReader("dummy.xlsx")
    
    def test_exact_match(self):
        result = self.reader.fuzzy_match("DT EMISSAO", "DT EMISSAO")
        self.assertTrue(result)
    
    def test_accent_insensitive(self):
        result = self.reader.fuzzy_match("DT EMISSÃO", "DT EMISSAO")
        self.assertTrue(result)
    
    def test_case_insensitive(self):
        result = self.reader.fuzzy_match("dt emissao", "DT EMISSAO")
        self.assertTrue(result)
    
    def test_different_strings(self):
        result = self.reader.fuzzy_match("FORNECEDOR", "INVOICE")
        self.assertFalse(result)


if __name__ == "__main__":
    unittest.main()
