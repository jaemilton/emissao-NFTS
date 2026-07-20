# Plano de Implementação - Gerador de Arquivos NFTS

Este plano descreve a implementação de um sistema Python para ler arquivos Excel com dados de ISS e gerar arquivos .txt no layout NFTS especificado.

## Estrutura do Projeto

```
emissao-NFTS/
├── src/
│   ├── __init__.py
│   ├── excel_reader.py      # Módulo para leitura do Excel
│   ├── layout_generator.py  # Módulo para geração do layout NFTS
│   ├── validator.py         # Módulo para validação dos arquivos gerados
│   └── main.py              # Script principal de orquestração
├── logs/                     # Diretório para logs de erro
├── output/                   # Diretório para arquivos .txt gerados
├── .env                      # Variáveis de ambiente (não versionado)
├── .env.example             # Template de variáveis de ambiente
├── .gitignore                # Arquivos ignorados pelo Git
├── requirements.txt          # Dependências do projeto
└── README.md                 # Documentação de uso
```

## Módulos

### 1. excel_reader.py
**Responsabilidade**: Ler e extrair tabelas do arquivo Excel

**Funções principais**:
- `read_excel_file(file_path)`: Carrega o arquivo .xlsx usando openpyxl
- `find_table_headers(worksheet)`: Localiza cabeçalhos de tabelas (a partir da linha 10, colunas B-R)
- `extract_table_data(worksheet, start_row)`: Extrai dados de uma tabela até encontrar coluna B vazia
- `detect_all_tables(worksheet)`: Identifica todas as tabelas no arquivo (busca cabeçalhos até 10 linhas após fim da tabela anterior)
- `convert_excel_date(serial_date)`: Converte datas seriais do Excel para formato AAAAMMDD

**Lógica de detecção de tabelas**:
- Procurar cabeçalho específico com 18 colunas (CONTRATO a STATUS)
- Tabelas iniciam na linha onde cabeçalho é encontrado
- Tabelas terminam quando coluna B está vazia
- Buscar próxima tabela até 10 linhas após o fim da anterior

### 2. layout_generator.py
**Responsabilidade**: Gerar registros no layout NFTS

**Funções principais**:
- `generate_header_record(table_data)`: Gera registro tipo 1 (Cabeçalho)
  - Tipo: "1" (fixo)
  - Versão: "001" (fixo)
  - Inscrição Municipal: (deve ser lido do arquivo .env da variável INSCRICAO_MUNICIPAL_SUJEITO_PASSIVO)
  - Data Início: menor data da coluna "DT EMISSÃO" (AAAAMMDD)
  - Data Fim: maior data da coluna "DT EMISSÃO" (AAAAMMDD)

- `generate_detail_record(row_data)`: Gera registro tipo 4 (Detalhe)
  - Mapear colunas do Excel para campos do layout
  - Formatar valores numéricos (15 posições, zeros à esquerda)
  - Truncar campos textuais quando necessário
  - Lógica especial para endereço (50 chars + complemento)
  - Lógica especial para discriminação (adicionar INVOICE se tiver letras)

- `generate_footer_record(detail_count, total_value)`: Gera registro tipo 9 (Rodapé)
  - Tipo: "9" (fixo)
  - Quantidade de registros tipo 4
  - Soma dos valores dos serviços
  - Deduções: zeros (fixo)

- `format_numeric_value(value, length)`: Formata valores numéricos com zeros à esquerda
- `format_text_value(value, length)`: Formata valores textuais alinhados à esquerda
- `format_percentage(value)`: Converte porcentagem (5,00% → 0500)
- `format_service_code(code)`: Converte código serviço (1.01 → 0101)

**Mapeamento de campos**:
- INVOICE → Número do documento (zeros se tiver letras)
- DT EMISSÃO → Data prestação (AAAAMMDD)
- MOEDA NACIONAL → Valor serviços (formato numérico)
- CODIGO SERVIÇOS LEI 116 → Código subitem (formato 4 dígitos)
- % ISS → Alíquota (formato 4 dígitos)
- FORNECEDOR → Nome/Razão Social
- ENDEREÇO → Endereço (50 chars) + Complemento (30 chars)
- DESCRIÇÃO SERVIÇOS → Discriminação (+ INVOICE se aplicável)

### 3. validator.py
**Responsabilidade**: Validar arquivos .txt gerados contra layout

**Funções principais**:
- `validate_file_layout(file_path, layout_spec)`: Valida arquivo completo
- `validate_header_record(record)`: Valida registro tipo 1
  - Verifica tamanho (30 caracteres)
  - Verifica tipo de registro
  - Valida formato de datas

- `validate_detail_record(record)`: Valida registro tipo 4
  - Verifica tamanho mínimo (442 + tamanho discriminação)
  - Valida campos numéricos
  - Valida campos textuais
  - Verifica alinhamento correto

- `validate_footer_record(record)`: Valida registro tipo 9
  - Verifica tamanho (40 caracteres)
  - Valida contagem de registros
  - Valida soma de valores

- `validate_field_lengths(record, spec)`: Valida tamanho de cada campo
- `validate_numeric_format(value)`: Verifica se valor é numérico válido

### 4. main.py
**Responsabilidade**: Orquestrar o processo completo

**Fluxo principal**:
1. Carregar arquivo Excel
2. Detectar todas as tabelas
3. Para cada tabela:
   - Extrair dados
   - Calcular datas de início/fim do período
   - Gerar registro cabeçalho
   - Gerar registros detalhe (um por linha)
   - Gerar registro rodapé
   - Criar arquivo .txt com nome baseado em período (ex: NFTS_20260511_20260511.txt)
   - Validar arquivo gerado
   - Registrar erros em log se houver
4. Gerar relatório final de processamento

**Tratamento de erros**:
- Criar arquivo de log em logs/processamento_YYYYMMDD_HHMMSS.log
- Registrar tabelas com erro e continuar processando outras
- Registrar erros de validação específicos

## Dependências

```
openpyxl>=3.1.0
python-dotenv>=1.0.0
```

## Casos de Teste

1. **Leitura de Excel**: Ler arquivo com múltiplas tabelas
2. **Conversão de datas**: Datas seriais Excel → AAAAMMDD
3. **Formatação numérica**: R$ 168870,20 → 000000016887024
4. **Formatação porcentagem**: 5,00% → 0500
5. **Truncamento de texto**: Endereço > 50 chars → endereço + complemento
6. **Validação de layout**: Verificar tamanhos e formatos
7. **Geração de arquivo**: Criar .txt completo com todos os registros

## Ordenamento de Implementação

1. Configurar estrutura de diretórios e requirements.txt
2. Implementar excel_reader.py (leitura e extração de tabelas)
3. Implementar layout_generator.py (geração de registros)
4. Implementar validator.py (validação)
5. Implementar main.py (orquestração)
6. Testar com arquivo de exemplo
7. Ajustar conforme necessário

## Status da Implementação

**Concluído** ✓

### Funcionalidades Implementadas

1. **Leitura de Excel**
   - Detecção automática de tabelas com base em cabeçalhos
   - Extração de dados até coluna B vazia
   - Busca de múltiplas tabelas (até 10 linhas após fim da anterior)
   - Normalização de cabeçalhos (remoção de espaços e quebras de linha)
   - Leitura de valores calculados (data_only=True)

2. **Geração de Layout NFTS**
   - Registro tipo 1 (Cabeçalho) com datas dinâmicas (min/max DT EMISSÃO)
   - Registro tipo 4 (Detalhe) com mapeamento completo de campos
   - Registro tipo 9 (Rodapé) com soma automática de valores
   - Formatação numérica brasileira (vírgula decimal, ponto milhar)
   - Tratamento especial para INVOICE com letras (zeros)
   - Adição de INVOICE na discriminação quando aplicável
   - Campo "Tipo do endereço" vazio (espaços)
   - Campo "Data de Fim do Período" com maior data da tabela

3. **Validação**
   - Validação de tamanho de registros
   - Validação de campos numéricos
   - Validação de formato de datas
   - Validação de soma total no rodapé

4. **Configuração**
   - Variável de ambiente para Inscrição Municipal
   - Validação obrigatória (8 dígitos numéricos)
   - Arquivo .env.example como template
   - .gitignore configurado para arquivos sensíveis

### Correções Realizadas Durante Implementação

- Normalização de cabeçalhos do Excel (espaços/quebras de linha)
- Formatação de data sem hora (AAAAMMDD)
- Normalização de texto (quebras de linha → espaços)
- Ajuste de tamanho mínimo de registro detalhe
- Correção de posição do campo de data na validação
- Tratamento de formato brasileiro para valores numéricos
- Correção da soma total no rodapé (soma de valores já formatados)
- Remoção de quebras de linha extras entre registros
- Adição de vírgula e espaço antes do INVOICE na descrição

### Arquivos Gerados

- `src/excel_reader.py` - Leitura e extração de tabelas
- `src/layout_generator.py` - Geração de registros NFTS
- `src/validator.py` - Validação de arquivos gerados
- `src/main.py` - Orquestração do processo
- `requirements.txt` - Dependências
- `.env.example` - Template de configuração
- `.gitignore` - Exclusões do Git
- `README.md` - Documentação de uso
