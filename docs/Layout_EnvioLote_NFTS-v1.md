# Layout de Envio de Lote NFTS

## Fonte
- Documento original: [Layout_EnvioLote_NFTS-v1.pdf](Layout_EnvioLote_NFTS-v1.pdf)
- Arquivo gerado para uso posterior por IA.

## Objetivo
Este documento descreve o layout associado ao envio de lote de NFTS e organiza as informações de forma estruturada para interpretação, validação e processamento automatizado.

## Conteúdo resumido
- Trata-se de um layout formal para envio de lote.
- Define a estrutura do arquivo, os registros obrigatórios e os campos que compõem cada linha.
- Serve como referência para mapeamento, integração, validação e implementação de cargas.

## Observações gerais
- Todos os campos numéricos devem ser preenchidos alinhados à direita, sem ponto e sem vírgula, e com zeros à esquerda quando necessário.
- Todos os campos alfanuméricos devem ser preenchidos alinhados à esquerda, com espaços à direita quando necessário, exceto o campo de Discriminação dos Serviços.
- O PDF apresenta a estrutura do layout em duas seções: uma versão V.001 e outra V.002. As tabelas abaixo consolidam os campos e os textos extraídos do documento.

## Detalhes dos campos

### Registro tipo 1 – Cabeçalho

| Campo | Posição Inicial | Posição Final | Tamanho | Formato | Preenchimento Obrigatório (S/N) | Conteúdo |
|---|---:|---:|---:|---|---|---|
| Tipo de registro | 1 | 1 | 1 | Numérico | S | Deve ser preenchido com valor "1", indicando linha de<br>cabeçalho. |
| Versão do arquivo | 2 | 4 | 3 | Numérico | S | Indica a versão do layout a ser utilizada. Deve ser preenchido com o número da versão atual.<br>A versão atual é a 001 na seção V.001 e a 002 na seção V.002 do documento. |
| Inscrição Municipal do Sujeito Passivo | 5 | 12 | 8 | Numérico | S | Inscrição municipal do Tomador ou Intermediário a que se refere o arquivo.<br>Caso o tomador de serviços esteja declarando serviços tomados, preencha com o CCM do tomador.<br>Caso o intermediário dos serviços esteja declarando serviços intermediados, preencha com o CCM do intermediário.<br>O sistema considerará o conteúdo deste campo como o CCM do intermediário quando for informado um registro tipo 6.<br>Caso o registro 6 não seja informado, o sistema assumirá este campo como o CCM do tomador. |
| Data de Início do Período Transferido no Arquivo | 13 | 20 | 8 | AAAAMMDD | S | O arquivo de transferência deverá conter todos os documentos referentes a um período.<br>Informe neste campo a data inicial desse período no formato AAAAMMDD. |
| Data de Fim do Período Transferido no Arquivo | 21 | 28 | 8 | AAAAMMDD | S | O arquivo de transferência deverá conter todos os documentos referentes a um período.<br>Informe neste campo a data final desse período no formato AAAAMMDD. |
| Fim de Linha | 29 | 30 | 2 | ASCII(13)+ASCII(10) | S | Caractere de fim de linha<br>(Chr(13) + Chr(10)). |

### Registro tipo 4 – Detalhe

| Campo | Posição Inicial | Posição Final | Tamanho | Formato | Preenchimento Obrigatório (S/N) | Conteúdo |
|---|---:|---:|---:|---|---|---|
| Tipo de registro | 1 | 1 | 1 | Numérico | S | Deve ser preenchido com valor "4", indicando linha de<br>detalhe. |
| Tipo do documento | 2 | 3 | 2 | Numérico | S | Informe o tipo do documento emitido com 02 posições.<br>Tipos válidos: 01 - dispensado de emissão de documento fiscal;<br>02 - com emissão de documento fiscal autorizado pelo município;<br>03 - sem emissão de documento fiscal embora obrigado. |
| Série do Documento | 4 | 8 | 5 | Texto | N | Informe a Série do Documento com 05 posições.<br>Para ser informada a série, o campo número do documento também deverá ser fornecido. |
| Número do Documento | 9 | 20 | 12 | Numérico | N | Informe o Número do Documento com 12 posições.<br>Este campo será de preenchimento obrigatório apenas para o tipo de documento "Com emissão de documento fiscal autorizado pelo município". |
| Data da prestação dos serviços | 21 | 28 | 8 | AAAAMMDD | S | Informe a Data da prestação do serviço no formato<br>AAAAMMDD. |
| Situação da NFTS | 29 | 29 | 1 | Texto | S | Informe a situação da NFTS:<br>N - Normal<br>C - Cancelado. |
| Tributação do Serviço | 30 | 30 | 1 | Caractere | S | Informe a situação com 01 posição.<br>T - Operação normal<br>I - Imune<br>J - ISS Suspenso por Decisão Judicial. Neste caso, informar no campo Discriminação dos Serviços o número do processo judicial na 1ª instância. |
| Valor dos Serviços | 31 | 45 | 15 | Numérico | S | Informe o Valor dos Serviços com 15 posições.<br>Campo obrigatório caso a situação da NFTS seja diferente de "C" (Cancelado).<br>Exemplo: R$ 500,85 → 000000000050085;<br>R$ 500,00 → 000000000050000. |
| Valor das Deduções | 46 | 60 | 15 | Numérico | S | Informe o Valor das Deduções com 15 posições.<br>Exemplo: R$ 500,85 → 000000000050085;<br>R$ 500,00 → 000000000050000. |
| Código do Serviço Tomado ou Intermediado | 61 | 65 | 5 | Numérico | S | Informe o Código do Serviço da NFTS com 05 posições.<br>Este código deverá pertencer à lista de serviços e ser um valor menor que 09000. |
| Código do Subitem da Lista | 66 | 69 | 4 | Numérico | N | Informe o Código do Subitem da lista de serviços da Lei Complementar nº 116/2003 com 04 posições.<br>Exemplo:<br>1.01 - 0101<br>4.20 - 0420<br>12.09 – 1209<br>15.10 - 1510<br>(*) - Este campo será de preenchimento obrigatório nos casos em que um código de serviço corresponda a vários códigos de item/subitem.<br>Nos demais casos, caso seja fornecido será validado com o código de serviço fornecido. |
| Alíquota | 70 | 73 | 4 | Numérico | S | Informe o Valor da Alíquota com 4 posições.<br>Exemplo: 5,00% → 0500; 2,75% → 0275.<br>Observação: o conteúdo deste campo será ignorado caso a tributação ocorra no município. |
| ISS Retido | 74 | 74 | 1 | Numérico | S | 1 - ISS Retido pelo tomador;<br>2 - NFTS sem ISS Retido;<br>3 - ISS Retido pelo intermediário;<br>4 - ISS Retido pelo tomador (descumprimento do Art. 8º A, §1º, da Lei Complementar 116, de 31 de julho de 2003);<br>5 - ISS Retido pelo intermediário (descumprimento do Art. 8º A, §1º, da Lei Complementar 116, de 31 de julho de 2003). |
| Indicador de CPF/CNPJ do Prestador | 75 | 75 | 1 | Numérico | S | Este campo indica o tipo de dados que será fornecido no campo CNPJ/CPF do Prestador:<br>1 para CPF.<br>2 para CNPJ.<br>3 para Prestador estabelecido no exterior. |
| CPF ou CNPJ do Prestador | 76 | 89 | 14 | Numérico | S | Informe o CNPJ do prestador com 14 posições ou CPF do prestador com 11 posições.<br>Caso o campo 14 esteja preenchido com 3, preencha este campo com zeros. |
| Inscrição Municipal do Prestador | 90 | 97 | 8 | Numérico | N | Informe a Inscrição Municipal do Prestador, com 8 posições, exclusivamente para prestadores com CCM no município de São Paulo. |
| Nome/Razão Social do Prestador | 98 | 172 | 75 | Texto | N | Este campo será ignorado caso seja fornecido um CNPJ/CPF ou a inscrição municipal do prestador tenha sido informada. |
| Tipo do Endereço do Prestador | 173 | 175 | 3 | Texto | N | Se estes campos estiverem informados, serão considerados no caso de prestador sem inscrição municipal.<br>Os dados da Receita Federal serão utilizados apenas se estes dados não estiverem informados. |
| Endereço do Prestador | 176 | 225 | 50 | Texto | N | Informe o endereço do prestador. |
| Número do Endereço do Prestador | 226 | 235 | 10 | Texto | N | Informe o número do endereço do prestador. |
| Complemento do Endereço do Prestador | 236 | 265 | 30 | Texto | N | Informe o complemento do endereço do prestador. |
| Bairro do Prestador | 266 | 295 | 30 | Texto | N | Informe o bairro do prestador. |
| Cidade do Prestador | 296 | 345 | 50 | Texto | N | Informe a cidade do prestador. |
| UF do Prestador | 346 | 347 | 2 | Texto | N | Informe a unidade da federação do prestador. |
| CEP do Prestador | 348 | 355 | 8 | Numérico | N | Informe o CEP do prestador com 8 posições. |
| E-mail do Prestador | 356 | 430 | 75 | Texto | N | Campo contendo o e-mail do prestador. |
| Tipo de NFTS | 431 | 431 | 1 | Numérico | N | 1 - Nota Fiscal do Tomador;<br>2 - Nota Fiscal do Intermediário. |
| Regime de Tributação | 432 | 432 | 1 | Numérico | S | 0 - Normal ou Simples Nacional (DAMSP);<br>4 - Simples Nacional (DAS);<br>5 - Microempreendedor Individual - MEI. |
| Data de Pagamento da Nota | 433 | 440 | 8 | AAAAMMDD | N | Data em que o serviço foi pago ao prestador.<br>Esta informação somente será considerada para tomadores de serviço órgãos públicos. |
| Discriminação dos Serviços | 441 | 441+ | N | Texto | N | Texto contínuo descritivo dos serviços.<br>O conjunto de caracteres correspondentes ao código ASCII 13 e ASCII 10 deverá ser substituído pelo caractere | (pipe ou barra vertical).<br>Exemplo: "Lavagem de carro|com lavagem de motor".<br>Não devem ser colocados espaços neste campo para completar seu tamanho máximo; o campo deve ser preenchido apenas com conteúdo a ser processado/armazenado.<br>Este campo é impresso num retângulo com 95 caracteres de largura e 24 linhas de altura.<br>Caso seja ultrapassado o limite de 24 linhas, o conteúdo será truncado durante a impressão da nota. |
| Fim de Linha | 442+N | 443+N | 2 | ASCII(13)+ASCII(10) | S | Caractere de fim de linha<br>(Chr(13) + Chr(10)). |

### Registro tipo 6 – Dados do Tomador de Serviços

| Campo | Posição Inicial | Posição Final | Tamanho | Formato | Preenchimento Obrigatório (S/N) | Conteúdo |
|---|---:|---:|---:|---|---|---|
| Tipo de registro | 1 | 1 | 1 | Numérico | S | Deve ser preenchido com valor "6", indicando linha de<br>detalhe de dados do tomador. |
| Indicador de CPF/CNPJ do Tomador | 2 | 2 | 1 | Numérico | S | Este campo indica o tipo de dados que será fornecido no campo CPF/CNPJ do Tomador:<br>1 para CPF.<br>2 para CNPJ.<br>3 para CPF não informado. |
| CPF ou CNPJ do Tomador | 3 | 16 | 14 | Numérico | S | Informe o CNPJ do tomador com 14 posições ou CPF do tomador com 11 posições. |
| Nome/Razão Social do Tomador | 17 | 91 | 75 | Texto | S | Será considerado o conteúdo deste campo, mesmo que o CPF ou CNPJ tenha inscrição no CCM. |
| Fim de Linha | 92 | 93 | 2 | ASCII(13)+ASCII(10) | S | Caractere de fim de linha<br>(Chr(13) + Chr(10)). |

### Registro tipo 9 – Rodapé

| Campo | Posição Inicial | Posição Final | Tamanho | Formato | Preenchimento Obrigatório (S/N) | Conteúdo |
|---|---:|---:|---:|---|---|---|
| Tipo de registro | 1 | 1 | 1 | Numérico | S | Deve ser preenchido com valor "9", indicando linha de<br>rodapé. |
| Número de linhas de detalhe do arquivo | 2 | 8 | 7 | Numérico | S | Número de linhas de detalhe (Tipo 4) contidas no arquivo.<br>Observação: não considerar as linhas de registro Tipo 6 na contagem do número de linhas de detalhe. |
| Valor total dos serviços contido no arquivo | 9 | 23 | 15 | Numérico | S | Informe a soma dos valores dos serviços das linhas de detalhe (Tipo 4) contidas no arquivo. |
| Valor total das deduções contidas no arquivo | 24 | 38 | 15 | Numérico | S | Informe a soma dos valores das deduções das linhas de detalhe (Tipo 4) contidas no arquivo. |
| Fim de Linha | 39 | 40 | 2 | ASCII(13)+ASCII(10) | S | Caractere de fim de linha<br>(Chr(13) + Chr(10)). |

## Observações
- Este Markdown foi gerado como versão estruturada e resumida para consumo por IA.
- A tabela acima foi preenchida com base no conteúdo extraído do PDF.
- Para uma extração mais completa do conteúdo visual do PDF, recomenda-se OCR ou conversão textual especializada.
