@echo off
setlocal enabledelayedexpansion

REM =============================================================================
REM SCRIPT DE INSTALAÇÃO AUTOMÁTICA - CONFIRMAÇÃO DE CONSULTAS
REM Compatível com Windows
REM =============================================================================

title Instalação Automática - Sistema de Confirmação de Consultas

echo.
echo ==============================================================================
echo 🚀 INSTALAÇÃO AUTOMÁTICA - SISTEMA DE CONFIRMAÇÃO DE CONSULTAS
echo ==============================================================================
echo.

REM Verificar se está rodando como administrador
net session >nul 2>&1
if %errorLevel% == 0 (
    echo ⚠️  Este script não deve ser executado como administrador
    echo ℹ️  Execute como usuário normal. O script pedirá permissões quando necessário.
    pause
    exit /b 1
)

REM Função para imprimir com cores (simulada)
set "RED=[91m"
set "GREEN=[92m"
set "YELLOW=[93m"
set "BLUE=[94m"
set "PURPLE=[95m"
set "CYAN=[96m"
set "NC=[0m"

echo.
echo 📋 PASSO 1: Verificando dependências do sistema
echo.

REM Verificar Docker
docker --version >nul 2>&1
if %errorLevel% neq 0 (
    echo ❌ Docker não encontrado
    echo ℹ️  Por favor, instale o Docker Desktop e execute o script novamente
    echo ℹ️  Download: https://www.docker.com/products/docker-desktop
    pause
    exit /b 1
) else (
    for /f "tokens=*" %%i in ('docker --version') do echo ✅ Docker encontrado: %%i
)

REM Verificar Docker Compose
docker-compose --version >nul 2>&1
if %errorLevel% neq 0 (
    echo ❌ Docker Compose não encontrado
    echo ℹ️  Por favor, instale o Docker Compose e execute o script novamente
    pause
    exit /b 1
) else (
    for /f "tokens=*" %%i in ('docker-compose --version') do echo ✅ Docker Compose encontrado: %%i
)

REM Verificar Git
git --version >nul 2>&1
if %errorLevel% neq 0 (
    echo ❌ Git não encontrado
    echo ℹ️  Por favor, instale o Git e execute o script novamente
    echo ℹ️  Download: https://git-scm.com/download/win
    pause
    exit /b 1
) else (
    for /f "tokens=*" %%i in ('git --version') do echo ✅ Git encontrado: %%i
)

echo.
echo 📋 PASSO 2: Verificando se Docker está rodando
echo.

docker info >nul 2>&1
if %errorLevel% neq 0 (
    echo ⚠️  Docker não está rodando
    echo ℹ️  Tentando iniciar Docker Desktop...
    start "" "C:\Program Files\Docker\Docker\Docker Desktop.exe"
    echo ℹ️  Aguardando Docker iniciar...
    timeout /t 15 /nobreak >nul
    
    REM Verificar novamente
    docker info >nul 2>&1
    if !errorLevel! neq 0 (
        echo ❌ Não foi possível iniciar o Docker
        echo ℹ️  Por favor, inicie o Docker Desktop manualmente e execute o script novamente
        pause
        exit /b 1
    )
)

echo ✅ Docker está rodando

echo.
echo 📋 PASSO 3: Configurando arquivo de ambiente
echo.

if exist ".env" (
    echo ⚠️  Arquivo .env já existe
    set /p overwrite="Deseja sobrescrever? (y/N): "
    if /i not "!overwrite!"=="y" (
        echo ℹ️  Mantendo arquivo .env existente
        goto :choose_database
    )
)

REM Copiar arquivo de exemplo
if exist ".env.backup" (
    copy ".env.backup" ".env" >nul
    echo ✅ Arquivo .env criado a partir do backup
) else if exist ".env.example" (
    copy ".env.example" ".env" >nul
    echo ✅ Arquivo .env criado a partir do exemplo
) else (
    echo ⚠️  Nenhum arquivo de exemplo encontrado, criando .env básico
    (
        echo # Configurações da aplicação
        echo BOTCONVERSA_API_KEY=your_api_key_here
        echo BOTCONVERSA_API_URL=https://api.botconversa.com.br/v1
        echo BOTCONVERSA_WEBHOOK_SECRET=your_webhook_secret_here
        echo.
        echo # Configurações do banco de dados
        echo DATABASE_TYPE=postgresql
        echo POSTGRESQL_URL=postgresql://postgres:1234@db-postgresql:5432/santaCasa
        echo ORACLE_URL=oracle+cx_oracle://system:oracle@db-oracle:1521/XE
        echo FIREBIRD_URL=firebird://SYSDBA:masterkey@db-firebird:3050/hospital_db
        echo.
        echo # Configurações do webhook
        echo WEBHOOK_HOST=0.0.0.0
        echo WEBHOOK_PORT=5001
        echo WEBHOOK_URL=https://seu-servidor.com/webhook/botconversa
        echo.
        echo # Configurações do hospital
        echo HOSPITAL_NAME=Seu Hospital
        echo HOSPITAL_ADDRESS=Endereço do Hospital
        echo HOSPITAL_CITY=Sua Cidade
        echo HOSPITAL_STATE=SEU ESTADO
        echo HOSPITAL_PHONE=^(00^) 0000-0000
        echo.
        echo # Configurações do scheduler
        echo SCHEDULER_ENABLE_CONFIRMATION_JOB=True
        echo SCHEDULER_ENABLE_REMINDER_JOB=True
        echo SCHEDULER_CONFIRMATION_HOUR=9
        echo SCHEDULER_CONFIRMATION_MINUTE=0
        echo SCHEDULER_REMINDER_HOUR=14
        echo SCHEDULER_REMINDER_MINUTE=0
        echo.
        echo # Configurações gerais
        echo DEBUG=True
        echo LOG_LEVEL=INFO
        echo MAX_WORKERS=4
        echo WORKER_TIMEOUT=30
    ) > .env
    echo ✅ Arquivo .env básico criado
)

:choose_database
echo.
echo 📋 PASSO 4: Escolhendo banco de dados
echo.

echo Qual banco de dados deseja usar?
echo 1^) PostgreSQL ^(Recomendado^)
echo 2^) Oracle
echo 3^) Firebird
echo.
set /p db_choice="Escolha uma opção (1-3) [1]: "

if "%db_choice%"=="2" (
    set DATABASE_TYPE=oracle
    echo ✅ Oracle selecionado
) else if "%db_choice%"=="3" (
    set DATABASE_TYPE=firebird
    echo ✅ Firebird selecionado
) else (
    set DATABASE_TYPE=postgresql
    echo ✅ PostgreSQL selecionado (padrão)
)

echo.
echo 📋 PASSO 5: Instalando aplicação
echo.

REM Parar containers existentes
echo ℹ️  Parando containers existentes...
docker-compose down >nul 2>&1

REM Limpar cache do Docker
echo ℹ️  Limpando cache do Docker...
docker system prune -f >nul

REM Construir e iniciar containers
echo ℹ️  Construindo e iniciando containers...
docker-compose --profile %DATABASE_TYPE% up -d --build

echo ✅ Aplicação instalada e iniciada

echo.
echo 📋 PASSO 6: Verificando instalação
echo.

REM Aguardar containers iniciarem
echo ℹ️  Aguardando containers iniciarem...
timeout /t 15 /nobreak >nul

REM Verificar saúde da aplicação
set max_attempts=30
set attempt=1

:health_check
curl -f http://localhost:5001/health >nul 2>&1
if %errorLevel% == 0 (
    echo ✅ Aplicação está respondendo corretamente
    goto :final_info
)

if %attempt% equ %max_attempts% (
    echo ⚠️  Aplicação não está respondendo após %max_attempts% tentativas
    echo ℹ️  Verifique os logs com: docker-compose logs
    goto :final_info
)

<<<<<<< HEAD
REM Iniciar serviços (padrão Oracle - banco principal da aplicação)
echo [INFO] Iniciando serviços com Oracle...
make oracle-setup
if %errorLevel% neq 0 (
    call :log_error "Erro ao iniciar serviços!"
    echo [INFO] Tente executar manualmente:
    echo [INFO] make oracle-setup
    echo.
    pause
    exit /b 1
)

REM Aguardar serviços estarem prontos
echo [INFO] Aguardando serviços estarem prontos...
timeout /t 30 /nobreak >nul

REM Verificar status
echo [INFO] Verificando status dos serviços...
make status
=======
echo ℹ️  Tentativa %attempt%/%max_attempts% - Aguardando...
timeout /t 5 /nobreak >nul
set /a attempt+=1
goto :health_check
>>>>>>> d68998a574fb5f1a3f9edc3be084d95b00ad7be4

:final_info
echo.
echo 📋 PASSO 7: Instalação concluída
echo.

echo.
echo 🎉 INSTALAÇÃO CONCLUÍDA COM SUCESSO!
echo.
echo 📱 Aplicação: http://localhost:5001
echo 🗄️  Banco de dados: %DATABASE_TYPE%
echo 📊 Status: docker-compose ps
echo 📝 Logs: docker-compose logs -f
echo 🔧 CLI: docker-compose exec app python -m cli
echo.
echo 📋 PRÓXIMOS PASSOS:
echo 1. Configure sua API_KEY do BotConversa no arquivo .env
echo 2. Configure o WEBHOOK_URL com o endereço do seu servidor
echo 3. Teste a aplicação: curl http://localhost:5001/health
echo.
echo 📚 Documentação completa: README.md
echo.

<<<<<<< HEAD
REM Aguardar um pouco mais
timeout /t 10 /nobreak >nul

REM Testar saúde da aplicação
echo [INFO] Testando saúde da aplicação...
powershell -Command "try { Invoke-WebRequest -Uri 'http://localhost:8000/health' -UseBasicParsing | Out-Null; Write-Host '[SUCCESS] ✅ Aplicação está respondendo!' } catch { Write-Host '[WARNING] ⚠️  Aplicação ainda não está respondendo. Aguarde mais alguns minutos.' }"

echo [INFO] Testando status do scheduler...
powershell -Command "try { Invoke-WebRequest -Uri 'http://localhost:8000/scheduler/status' -UseBasicParsing | Out-Null; Write-Host '[SUCCESS] ✅ Scheduler está funcionando!' } catch { Write-Host '[WARNING] ⚠️  Scheduler ainda não está respondendo.' }"

echo.

REM Mostrar próximos passos
echo ========================================
echo 🎉 INSTALAÇÃO CONCLUÍDA COM SUCESSO! 🎉
echo ========================================
echo.
echo 📱 Aplicação: http://localhost:8000
echo 🗄️  Banco: Oracle (porta 1521)
echo 📊 Status: make status
echo 📝 Logs: make logs
echo 🔧 CLI: make cli
echo.
echo 📚 Comandos úteis:
echo   make help              # Ver todos os comandos
echo   make restart           # Reiniciar serviços
echo   make clean             # Limpar tudo
echo   make postgresql-setup  # Mudar para PostgreSQL
echo   make firebird-setup    # Mudar para Firebird
echo.
echo 🌐 Para acessar de outras máquinas:
echo   - Configure o IP da máquina no .env
echo   - Ajuste as configurações de firewall
echo.
echo 📖 Documentação: README.md
echo.

REM Verificar se Make está disponível
make --version >nul 2>&1
if %errorLevel% neq 0 (
    echo [WARNING] Make não está instalado no Windows.
    echo [INFO] Para usar comandos make, instale:
    echo [INFO] - Chocolatey: choco install make
    echo [INFO] - Ou use comandos docker-compose diretamente
    echo.
)

echo [INFO] Instalação concluída! Pressione qualquer tecla para sair...
pause >nul
=======
pause
>>>>>>> d68998a574fb5f1a3f9edc3be084d95b00ad7be4
