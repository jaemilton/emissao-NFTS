# Gerador de Arquivos NFTS

Sistema Python para ler arquivos Excel com dados de ISS e gerar arquivos .txt no layout NFTS (Nota Fiscal de Tomadores de Serviços) conforme especificação da Prefeitura de São Paulo.

## Estrutura do Projeto

```
emissao-NFTS/
├── src/
│   ├── __init__.py
│   ├── excel_reader.py      # Módulo para leitura do Excel
│   ├── layout_generator.py  # Módulo para geração do layout NFTS
│   ├── validator.py         # Módulo para validação dos arquivos gerados
│   └── main.py              # Script principal de orquestração
├── docs/                     # Documentação
│   ├── prompt.txt
│   ├── Layout_EnvioLote_NFTS-v1.md
│   └── plano-implementacao-nfts.md
├── logs/                     # Diretório para logs de erro
├── output/                   # Diretório para arquivos .txt gerados
├── .env                      # Variáveis de ambiente (crie a partir do .env.example)
├── .env.example              # Template de variáveis de ambiente
├── prepare.bat               # Script para configurar ambiente virtual (Windows)
├── run.bat                   # Script simplificado para execução (Windows)
├── requirements.txt          # Dependências do projeto
└── README.md                 # Este arquivo
```

## Instalação

### Método Rápido (Windows)

Execute o script `prepare.bat` para configurar automaticamente o ambiente virtual, instalar as dependências e criar o arquivo de configuração:

```bash
.\prepare.bat
```

Este script:
- Verifica se o ambiente virtual `.venv` já existe
- Se não existir, cria um novo ambiente virtual Python
- Instala todas as dependências do `requirements.txt`
- Verifica se o arquivo `.env` já existe
- Se não existir, cria o arquivo `.env` a partir do `.env.example`
- Ativa o ambiente virtual
- Exibe aviso para editar o arquivo `.env` com sua Inscrição Municipal

### Método Manual

1. Certifique-se de ter Python 3.7+ instalado
2. Crie um ambiente virtual:

```bash
python -m venv .venv
```

3. Ative o ambiente virtual:

```bash
# Windows
.venv\Scripts\activate

# Linux/Mac
source .venv/bin/activate
```

4. Instale as dependências:

```bash
pip install -r requirements.txt
```

5. Configure as variáveis de ambiente:

```bash
# Copie o arquivo de exemplo
copy .env.example .env

# Edite o arquivo .env e adicione sua Inscrição Municipal
# INSCRICAO_MUNICIPAL_SUJEITO_PASSIVO=12345678
```

## Uso

### Método Simplificado (Windows)

Execute o script `run.bat` para processar arquivos Excel:

```bash
# Com diálogo de seleção de arquivo (sem argumento)
.\run.bat

# Com arquivo específico (com argumento)
.\run.bat docs\ISS_IMPORTAÇÃO_03_06_2026.xlsx
```

Este script:
- Verifica se o ambiente virtual `.venv` já existe
- Se não existir, executa automaticamente o `prepare.bat` para configurar o ambiente
- Ativa automaticamente o ambiente virtual Python
- Se nenhum arquivo for especificado, abre um diálogo de seleção de arquivo Windows
- Processa o arquivo Excel selecionado
- Exibe mensagem de sucesso ou erro

### Via Linha de Comando

```bash
python src/main.py <arquivo_excel>
```

**Parâmetros:**
- `arquivo_excel`: Caminho do arquivo Excel de entrada (obrigatório)

**Exemplo:**

```bash
python src/main.py docs/ISS_IMPORTAÇÃO_03_06_2026.xlsx
```

### Como Módulo Python

```python
from src.main import NFTSGenerator

# Criar gerador
generator = NFTSGenerator(
    excel_path="docs/ISS_IMPORTAÇÃO_03_06_2026.xlsx",
    output_dir="output",
    log_dir="logs"
)

# Processar arquivo
success = generator.process()
```

## Formato do Arquivo Excel

O arquivo Excel deve conter tabelas com o seguinte cabeçalho (a partir da linha 10, colunas B-R):

| CONTRATO | CODIGO BACEN | FORNECEDOR | INVOICE | DT EMISSÃO | DESCRIÇÃO SERVIÇOS | MOEDA ESTRANGEIRA | TAXA | MOEDA | MOEDA NACIONAL | CODIGO SERVIÇOS LEI 116 | % ISS | ISS | NFTS | ENDEREÇO | OBSERVAÇÕES | STATUS |
|----------|--------------|------------|---------|------------|-------------------|-------------------|------|-------|----------------|-------------------------|-------|-----|------|-----------|-------------|--------|

**Regras de detecção de tabelas:**
- Tabelas iniciam onde o cabeçalho é encontrado
- Tabelas terminam quando a coluna B está vazia
- O sistema busca por novas tabelas até 10 linhas após o fim da tabela anterior

## Layout do Arquivo NFTS

O sistema gera arquivos .txt com três tipos de registros:

### Registro Tipo 1 - Cabeçalho
- Tipo de registro: 1
- Versão do arquivo: 001
- Inscrição Municipal: (número da inscrição municipal do sujeito passivo definido no arquivo .env)
- Data de Início do Período: (menor data da tabela)
- Data de Fim do Período: (maior data da tabela)

### Registro Tipo 4 - Detalhe
Gerado para cada linha da tabela Excel, incluindo:
- Tipo de documento: 01
- Número do documento (INVOICE)
- Data da prestação (DT EMISSÃO)
- Valor dos serviços (MOEDA NACIONAL)
- Código do serviço e subitem
- Alíquota (% ISS)
- Dados do prestador (FORNECEDOR, ENDEREÇO)
- Discriminação dos serviços

### Registro Tipo 9 - Rodapé
- Tipo de registro: 9
- Quantidade de registros tipo 4
- Valor total dos serviços
- Valor total das deduções (zeros)

## Validação

O sistema valida automaticamente cada arquivo gerado:
- Verifica tamanhos de campos
- Valida formatos numéricos
- Confirma datas no formato AAAAMMDD
- Verifica consistência entre rodapé e detalhes

## Logs

O sistema gera um arquivo de log para cada execução:
- Nome: `processamento_YYYYMMDD_HHMMSS.log`
- Localização: diretório `logs/`
- Conteúdo: timestamp de cada operação, erros e avisos

## Exemplo de Saída

```
[14:30:15] Iniciando processamento em 18/07/2026 14:30:15
[14:30:15] Arquivo Excel: docs/ISS_IMPORTAÇÃO_03_06_2026.xlsx
[14:30:16] Carregando arquivo Excel...
[14:30:16] Arquivo Excel carregado com sucesso
[14:30:16] Detectando tabelas...
[14:30:16] Encontradas 2 tabela(s)

[14:30:16] Processando tabela 1 (linha 10) com 5 registros
[14:30:16] Gerando arquivo: NFTS_20260511_20260511.txt
[14:30:16] Arquivo gerado com sucesso: output/NFTS_20260511_20260511.txt
[14:30:16] Validando arquivo gerado...
[14:30:16] Arquivo validado com sucesso (Total: 000000016887024)

[14:30:17] Processando tabela 2 (linha 25) com 3 registros
[14:30:17] Gerando arquivo: NFTS_20260601_20260615.txt
[14:30:17] Arquivo gerado com sucesso: output/NFTS_20260601_20260615.txt
[14:30:17] Validando arquivo gerado...
[14:30:17] Arquivo validado com sucesso (Total: 000000008500000)

============================================================
RELATÓRIO FINAL
============================================================
Tabelas processadas: 2
Arquivos gerados: 2
Arquivos validados: 2
Erros encontrados: 0
============================================================
```

## Tratamento de Erros

O sistema continua processando outras tabelas mesmo se uma tabela falhar:
- Erros são registrados no log
- Tabelas com erro são puladas
- Relatório final indica quantidade de erros

## Dependências

- `openpyxl>=3.1.0` - Leitura de arquivos Excel

## Documentação

- [Prompt original](docs/prompt.txt)
- [Especificação do layout NFTS](docs/Layout_EnvioLote_NFTS-v1.md)
- [Plano de implementação](docs/plano-implementacao-nfts.md)

## Notas

- Datas no Excel devem estar em formato serial ou datetime
- Valores monetários são convertidos para inteiros (multiplicados por 100)
- Campos textuais são truncados conforme especificação do layout
- Endereços com mais de 50 caracteres são divididos em endereço + complemento
- INVOICEs que contêm letras resultam em número de documento zerado
