@echo off
setlocal enabledelayedexpansion

REM ========================================
REM SISTEMA DE CONFIRMAÇÃO DE CONSULTAS - SANTA CASA
REM Script de Instalação Automática para Windows
REM ========================================

REM Configurar cores (Windows 10+)
color 0A

echo ========================================
echo 🏥 SISTEMA DE CONFIRMAÇÃO DE CONSULTAS
echo 🐳 INSTALADOR DOCKER AUTOMÁTICO - WINDOWS
echo ========================================
echo.

REM Verificar se é Windows
if not "%OS%"=="Windows_NT" (
    echo [ERROR] Este script é para Windows. Use install.sh no Linux/Mac.
    pause
    exit /b 1
)

REM Verificar se é executado como administrador
net session >nul 2>&1
if %errorLevel% == 0 (
    echo [INFO] Executando como administrador ✓
) else (
    echo [WARNING] Execute como administrador para melhor compatibilidade
    echo.
)

REM Função para log
:log_info
echo [INFO] %~1
goto :eof

:log_success
echo [SUCCESS] %~1
goto :eof

:log_warning
echo [WARNING] %~1
goto :eof

:log_error
echo [ERROR] %~1
goto :eof

REM Verificar pré-requisitos
echo [INFO] Verificando pré-requisitos...
echo.

REM Verificar Docker
docker --version >nul 2>&1
if %errorLevel% neq 0 (
    call :log_error "Docker não está instalado!"
    call :log_info "Instale Docker Desktop em: https://docs.docker.com/desktop/install/windows/"
    echo.
    pause
    exit /b 1
)
call :log_success "Docker está instalado ✓"

REM Verificar Docker Compose
docker-compose --version >nul 2>&1
if %errorLevel% neq 0 (
    call :log_error "Docker Compose não está instalado!"
    call :log_info "Instale Docker Compose em: https://docs.docker.com/compose/install/"
    echo.
    pause
    exit /b 1
)
call :log_success "Docker Compose está instalado ✓"

REM Verificar Git
git --version >nul 2>&1
if %errorLevel% neq 0 (
    call :log_error "Git não está instalado!"
    call :log_info "Instale Git em: https://git-scm.com/download/win"
    echo.
    pause
    exit /b 1
)
call :log_success "Git está instalado ✓"

REM Verificar se Docker está rodando
echo [INFO] Verificando se Docker está rodando...
docker info >nul 2>&1
if %errorLevel% neq 0 (
    call :log_error "Docker não está rodando!"
    call :log_info "Inicie o Docker Desktop e execute este script novamente."
    echo.
    pause
    exit /b 1
)
call :log_success "Docker está rodando ✓"

echo.
call :log_success "Todos os pré-requisitos estão instalados!"
echo.

REM Configurar ambiente
echo [INFO] Configurando ambiente...
echo.

REM Criar diretório de logs se não existir
if not exist "logs" (
    mkdir logs
    call :log_success "Diretório logs criado ✓"
)

REM Verificar se .env existe
if not exist ".env" (
    echo [INFO] Criando arquivo .env a partir do template...
    if exist "env.example" (
        copy "env.example" ".env" >nul
        call :log_success "Arquivo .env criado ✓"
        echo.
        call :log_warning "IMPORTANTE: Edite o arquivo .env com suas configurações antes de continuar!"
        echo [INFO] Pressione qualquer tecla quando terminar de editar o .env...
        pause >nul
    ) else (
        call :log_error "Arquivo env.example não encontrado!"
        pause
        exit /b 1
    )
) else (
    call :log_info "Arquivo .env já existe ✓"
)

REM Verificar se .env foi configurado
findstr /C:"your_api_key_aqui" .env >nul 2>&1
if %errorLevel% == 0 (
    echo.
    call :log_warning "ATENÇÃO: Você ainda não configurou suas chaves no .env!"
    echo [INFO] Configure BOTCONVERSA_API_KEY e BOTCONVERSA_WEBHOOK_SECRET antes de continuar.
    echo [INFO] Pressione qualquer tecla quando terminar...
    pause >nul
)

echo.

REM Iniciar Docker
echo [INFO] Iniciando serviços Docker...
echo.

REM Construir imagens
echo [INFO] Construindo imagens Docker...
make build
if %errorLevel% neq 0 (
    call :log_error "Erro ao construir imagens Docker!"
    echo [INFO] Verifique se o Make está instalado ou execute manualmente:
    echo [INFO] docker-compose build
    echo.
    pause
    exit /b 1
)

REM Iniciar serviços (padrão PostgreSQL)
echo [INFO] Iniciando serviços com PostgreSQL...
make postgresql-setup
if %errorLevel% neq 0 (
    call :log_error "Erro ao iniciar serviços!"
    echo [INFO] Tente executar manualmente:
    echo [INFO] make postgresql-setup
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

echo.

REM Testar instalação
echo [INFO] Testando instalação...
echo.

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
echo 🗄️  Banco: PostgreSQL (porta 5432)
echo 📊 Status: make status
echo 📝 Logs: make logs
echo 🔧 CLI: make cli
echo.
echo 📚 Comandos úteis:
echo   make help              # Ver todos os comandos
echo   make restart           # Reiniciar serviços
echo   make clean             # Limpar tudo
echo   make oracle-setup      # Mudar para Oracle
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
