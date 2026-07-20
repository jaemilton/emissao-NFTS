@echo off
echo Verificando ambiente virtual Python...

if not exist ".venv" (
    echo Ambiente virtual nao encontrado. Executando prepare.bat...
    call prepare.bat
    if %ERRORLEVEL% NEQ 0 (
        echo Erro ao configurar ambiente virtual.
        exit /b 1
    )
    echo.
)

echo Ativando ambiente virtual Python...
call .venv\Scripts\activate.bat

if "%1"=="" (
    echo Nenhum arquivo Excel especificado. O sistema abrirá um seletor de arquivo...
    echo.
    python src\main.py
) else (
    echo Executando script principal com arquivo: %1
    python src\main.py "%1"
)

if %ERRORLEVEL% EQU 0 (
    echo.
    echo Processamento concluido com sucesso!
) else (
    echo.
    echo Erro no processamento. Verifique os logs em: logs\
)

pause