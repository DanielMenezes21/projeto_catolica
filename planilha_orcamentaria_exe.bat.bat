@echo off
REM Ativa o ambiente virtual, inicia o servidor Django e abre o navegador
cd /d %~dp0
start "Django" cmd /c ".\venv\Scripts\activate.bat && python manage.py runserver"
REM Aguarda alguns segundos para o servidor iniciar
ping 127.0.0.1 -n 3 >nul
start http://127.0.0.1:8000/
pause