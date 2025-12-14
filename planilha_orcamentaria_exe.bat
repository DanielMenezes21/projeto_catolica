@echo off
REM Verifica se Python está instalado
where python >nul 2>nul
if errorlevel 1 (
    echo Python nao encontrado! Instale o Python 3.13 antes de rodar este sistema.
    pause
    exit /b
)
REM Verifica se as bibliotecas essenciais estao instaladas
set PACKAGES=django openpyxl django_select2 django-crispy-forms
set NEED_INSTALL=0
for %%P in (%PACKAGES%) do (
    python -c "import %%P" 2>nul
    if errorlevel 1 (
        echo Biblioteca '%%P' nao encontrada! Instalando dependencias...
        set NEED_INSTALL=1
    )
)
if %NEED_INSTALL%==1 (
    pip install -r requirements.txt
    if errorlevel 1 (
        echo Falha ao instalar dependencias! Verifique o Python/pip.
        pause
        exit /b
    )
)
REM Ativa o ambiente virtual, inicia o servidor Django e abre o navegador
cd /d %~dp0
start "Django" cmd /c ".\venv\Scripts\activate.bat && python manage.py runserver"
REM Aguarda alguns segundos para o servidor iniciar
ping 127.0.0.1 -n 3 >nul
start http://127.0.0.1:8000/
pause