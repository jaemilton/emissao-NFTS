@echo off
echo Verificando ambiente virtual Python...

if not exist ".venv" (
    echo Ambiente virtual nao encontrado. Criando novo ambiente virtual...
    python -m venv .venv
    if %ERRORLEVEL% NEQ 0 (
        echo Erro ao criar ambiente virtual. Verifique se Python esta instalado.
        exit /b 1
    )
    echo Ambiente virtual criado com sucesso!
    echo.
    echo Instalando dependencias...
    call .venv\Scripts\activate.bat
    pip install -r requirements.txt
    if %ERRORLEVEL% NEQ 0 (
        echo Erro ao instalar dependencias.
        exit /b 1
    )
    echo Dependencias instaladas com sucesso!
) else (
    echo Ambiente virtual encontrado.
    echo Ativando ambiente virtual...
    call .venv\Scripts\activate.bat
)

echo.
echo Verificando arquivo de configuracao .env...

if not exist ".env" (
    echo Arquivo .env nao encontrado. Criando a partir do .env.example...
    copy .env.example .env
    if %ERRORLEVEL% NEQ 0 (
        echo Erro ao criar arquivo .env.
        exit /b 1
    )
    echo Arquivo .env criado com sucesso!
    echo.
    echo ATENCAO: Edite o arquivo .env e adicione sua Inscrição Municipal.
    echo Exemplo: INSCRICAO_MUNICIPAL_SUJEITO_PASSIVO=12345678
) else (
    echo Arquivo .env encontrado.
)

echo.
echo Ambiente virtual ativado com sucesso!
echo.
echo Para executar o script principal, use: run.bat [arquivo_excel]
echo Exemplo: run.bat docs\ISS_IMPORTAÇÃO_03_06_2026.xlsx
