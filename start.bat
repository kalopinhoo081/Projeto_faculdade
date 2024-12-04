@echo off
echo ===========================================
echo Iniciando os servidores Flask...
echo ===========================================

:: Ativa o ambiente virtual
call venv\Scripts\activate

:: Inicia o app.py na porta 5000 em uma nova janela
start "Servidor 1 - app.py" cmd /k "python app.py"


echo.
echo Servidores iniciados com sucesso.
echo ===========================================
echo Pressione qualquer tecla para sair...
pause > nul
