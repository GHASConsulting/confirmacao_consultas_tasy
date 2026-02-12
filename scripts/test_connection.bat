@echo off
cd /d "%~dp0.."
echo 🔍 Testando conexão com o banco de dados...
python scripts\test_connection.py
if %errorLevel% neq 0 (
    echo.
    echo [ERRO] Falha no teste. Verifique o .env e se o banco está acessível.
    pause
    exit /b 1
)
echo.
echo [OK] Teste concluído.
pause 