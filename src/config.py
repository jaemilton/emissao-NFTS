"""Configurações centralizadas para o gerador de NFTS."""

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

# Tolerância de diferenças na validação de cabeçalhos
HEADER_TOLERANCE = 3

# Colunas para filtrar registros a serem processados
FILTER_COLUMN = "NFTS"
