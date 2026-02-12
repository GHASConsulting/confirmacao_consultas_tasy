#!/bin/bash

# =============================================================================
# SCRIPT DE INSTALAÇÃO AUTOMÁTICA - CONFIRMAÇÃO DE CONSULTAS
# Compatível com Linux e macOS
# =============================================================================

set -e  # Para execução em caso de erro

# Cores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Função para imprimir com cores
print_color() {
    printf "${1}${2}${NC}\n"
}

print_header() {
    echo ""
    print_color $CYAN "=============================================================================="
    print_color $CYAN "🚀 INSTALAÇÃO AUTOMÁTICA - SISTEMA DE CONFIRMAÇÃO DE CONSULTAS"
    print_color $CYAN "=============================================================================="
    echo ""
}

print_step() {
    print_color $BLUE "📋 PASSO $1: $2"
    echo ""
}

print_success() {
    print_color $GREEN "✅ $1"
}

print_warning() {
    print_color $YELLOW "⚠️  $1"
}

print_error() {
    print_color $RED "❌ $1"
}

print_info() {
    print_color $PURPLE "ℹ️  $1"
}

# Verificar se está rodando como root
check_root() {
    if [[ $EUID -eq 0 ]]; then
        print_warning "Este script não deve ser executado como root/sudo"
        print_info "Execute como usuário normal. O script pedirá sudo quando necessário."
        exit 1
    fi
}

# Detectar sistema operacional
detect_os() {
    if [[ "$OSTYPE" == "linux-gnu"* ]]; then
        OS="linux"
        print_success "Sistema detectado: Linux"
    elif [[ "$OSTYPE" == "darwin"* ]]; then
        OS="macos"
        print_success "Sistema detectado: macOS"
    else
        print_error "Sistema operacional não suportado: $OSTYPE"
        exit 1
    fi
}

# Verificar dependências
check_dependencies() {
    print_step "1" "Verificando dependências do sistema"
    
    local missing_deps=()
    
    # Verificar Docker
    if ! command -v docker &> /dev/null; then
        missing_deps+=("Docker")
    else
        print_success "Docker encontrado: $(docker --version)"
    fi
    
    # Verificar Docker Compose
    if ! command -v docker-compose &> /dev/null; then
        missing_deps+=("Docker Compose")
    else
        print_success "Docker Compose encontrado: $(docker-compose --version)"
    fi
    
    # Verificar Git
    if ! command -v git &> /dev/null; then
        missing_deps+=("Git")
    else
        print_success "Git encontrado: $(git --version)"
    fi
    
    # Verificar curl
    if ! command -v curl &> /dev/null; then
        missing_deps+=("curl")
    else
        print_success "curl encontrado"
    fi
    
    if [ ${#missing_deps[@]} -ne 0 ]; then
        print_error "Dependências faltando: ${missing_deps[*]}"
        print_info "Por favor, instale as dependências faltando e execute o script novamente."
        
        if [ "$OS" = "linux" ]; then
            print_info "Para Ubuntu/Debian: sudo apt update && sudo apt install docker.io docker-compose git curl"
            print_info "Para CentOS/RHEL: sudo yum install docker docker-compose git curl"
        elif [ "$OS" = "macos" ]; then
            print_info "Para macOS: brew install docker docker-compose git curl"
        fi
        exit 1
    fi
}

# Verificar se Docker está rodando
check_docker_running() {
    print_step "2" "Verificando se Docker está rodando"
    
    if ! docker info &> /dev/null; then
        print_warning "Docker não está rodando"
        print_info "Tentando iniciar Docker..."
        
        if [ "$OS" = "linux" ]; then
            sudo systemctl start docker
            sudo systemctl enable docker
        elif [ "$OS" = "macos" ]; then
            open -a Docker
            print_info "Aguardando Docker iniciar..."
            sleep 10
        fi
        
        # Verificar novamente
        if ! docker info &> /dev/null; then
            print_error "Não foi possível iniciar o Docker"
            print_info "Por favor, inicie o Docker manualmente e execute o script novamente"
            exit 1
        fi
    fi
    
    print_success "Docker está rodando"
}

# Configurar arquivo .env
setup_env() {
    print_step "3" "Configurando arquivo de ambiente"
    
    if [ -f ".env" ]; then
        print_warning "Arquivo .env já existe"
        read -p "Deseja sobrescrever? (y/N): " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            print_info "Mantendo arquivo .env existente"
            return
        fi
    fi
    
    # Copiar arquivo de exemplo
    if [ -f ".env.backup" ]; then
        cp .env.backup .env
        print_success "Arquivo .env criado a partir do backup"
    elif [ -f ".env.example" ]; then
        cp .env.example .env
        print_success "Arquivo .env criado a partir do exemplo"
    else
        print_warning "Nenhum arquivo de exemplo encontrado, criando .env básico"
        cat > .env << EOF
# Configurações da aplicação
BOTCONVERSA_API_KEY=your_api_key_here
BOTCONVERSA_API_URL=https://api.botconversa.com.br/v1
BOTCONVERSA_WEBHOOK_SECRET=your_webhook_secret_here

# Configurações do banco de dados
DATABASE_TYPE=postgresql
POSTGRESQL_URL=postgresql://postgres:1234@db-postgresql:5432/santaCasa
ORACLE_URL=oracle+cx_oracle://system:oracle@db-oracle:1521/XE
FIREBIRD_URL=firebird://SYSDBA:masterkey@db-firebird:3050/hospital_db

# Configurações do webhook
WEBHOOK_HOST=0.0.0.0
WEBHOOK_PORT=5001
WEBHOOK_URL=https://seu-servidor.com/webhook/botconversa

# Configurações do hospital
HOSPITAL_NAME=Seu Hospital
HOSPITAL_ADDRESS=Endereço do Hospital
HOSPITAL_CITY=Sua Cidade
HOSPITAL_STATE=SEU ESTADO
HOSPITAL_PHONE=(00) 0000-0000

# Configurações do scheduler
SCHEDULER_ENABLE_CONFIRMATION_JOB=True
SCHEDULER_ENABLE_REMINDER_JOB=True
SCHEDULER_CONFIRMATION_HOUR=9
SCHEDULER_CONFIRMATION_MINUTE=0
SCHEDULER_REMINDER_HOUR=14
SCHEDULER_REMINDER_MINUTE=0

# Configurações gerais
DEBUG=True
LOG_LEVEL=INFO
MAX_WORKERS=4
WORKER_TIMEOUT=30
EOF
        print_success "Arquivo .env básico criado"
    fi
}

# Escolher banco de dados
choose_database() {
    print_step "4" "Escolhendo banco de dados"
    
    echo "Qual banco de dados deseja usar?"
    echo "1) PostgreSQL (Recomendado)"
    echo "2) Oracle"
    echo "3) Firebird"
    echo ""
    read -p "Escolha uma opção (1-3) [1]: " db_choice
    
    case $db_choice in
        2)
            DATABASE_TYPE="oracle"
            print_success "Oracle selecionado"
            ;;
        3)
            DATABASE_TYPE="firebird"
            print_success "Firebird selecionado"
            ;;
        *)
            DATABASE_TYPE="postgresql"
            print_success "PostgreSQL selecionado (padrão)"
            ;;
    esac
}

# Instalar aplicação
install_application() {
    print_step "5" "Instalando aplicação"
    
    # Parar containers existentes
    print_info "Parando containers existentes..."
    docker-compose down 2>/dev/null || true
    
    # Limpar cache do Docker
    print_info "Limpando cache do Docker..."
    docker system prune -f
    
    # Construir e iniciar containers
    print_info "Construindo e iniciando containers..."
    docker-compose --profile $DATABASE_TYPE up -d --build
    
    print_success "Aplicação instalada e iniciada"
}

# Verificar instalação
verify_installation() {
    print_step "6" "Verificando instalação"
    
    # Aguardar containers iniciarem
    print_info "Aguardando containers iniciarem..."
    sleep 15
    
    # Verificar saúde da aplicação
    local max_attempts=30
    local attempt=1
    
    while [ $attempt -le $max_attempts ]; do
        if curl -f http://localhost:5001/health &> /dev/null; then
            print_success "Aplicação está respondendo corretamente"
            break
        fi
        
        if [ $attempt -eq $max_attempts ]; then
            print_warning "Aplicação não está respondendo após $max_attempts tentativas"
            print_info "Verifique os logs com: docker-compose logs"
            return
        fi
        
        print_info "Tentativa $attempt/$max_attempts - Aguardando..."
        sleep 5
        ((attempt++))
    done
}

# Mostrar informações finais
show_final_info() {
    print_step "7" "Instalação concluída"
    
<<<<<<< HEAD
    # Verificar se é Linux/Mac
    if [[ "$OSTYPE" == "msys" || "$OSTYPE" == "win32" ]]; then
        log_error "Este script é para Linux/Mac. Use install.bat no Windows."
        exit 1
    fi
    
    # Verificar Docker
    if ! command_exists docker; then
        log_error "Docker não está instalado!"
        log_info "Instale Docker em: https://docs.docker.com/get-docker/"
        exit 1
    fi
    
    # Verificar Docker Compose
    if ! command_exists docker-compose; then
        log_error "Docker Compose não está instalado!"
        log_info "Instale Docker Compose em: https://docs.docker.com/compose/install/"
        exit 1
    fi
    
    # Verificar Git
    if ! command_exists git; then
        log_error "Git não está instalado!"
        log_info "Instale Git em: https://git-scm.com/downloads"
        exit 1
    fi
    
    # Verificar Make
    if ! command_exists make; then
        log_warning "Make não está instalado. Instalando..."
        if [[ "$OSTYPE" == "darwin"* ]]; then
            # macOS
            if command_exists brew; then
                brew install make
            else
                log_error "Instale Homebrew primeiro: https://brew.sh/"
                exit 1
            fi
        else
            # Linux
            if command_exists apt-get; then
                sudo apt-get update && sudo apt-get install -y make
            elif command_exists yum; then
                sudo yum install -y make
            else
                log_error "Não foi possível instalar Make automaticamente"
                exit 1
            fi
        fi
    fi
    
    log_success "Todos os pré-requisitos estão instalados!"
}

# Função para configurar ambiente
setup_environment() {
    log_info "Configurando ambiente..."
    
    # Criar diretório de logs se não existir
    mkdir -p logs
    
    # Verificar se .env existe
    if [ ! -f .env ]; then
        log_info "Criando arquivo .env a partir do template..."
        if [ -f env.example ]; then
            cp env.example .env
            log_success "Arquivo .env criado!"
            log_warning "IMPORTANTE: Edite o arquivo .env com suas configurações antes de continuar!"
            log_info "Pressione ENTER quando terminar de editar o .env..."
            read -r
        else
            log_error "Arquivo env.example não encontrado!"
            exit 1
        fi
    else
        log_info "Arquivo .env já existe!"
    fi
    
    # Verificar se .env foi configurado
    if grep -q "your_api_key_aqui\|your_webhook_secret_aqui" .env; then
        log_warning "ATENÇÃO: Você ainda não configurou suas chaves no .env!"
        log_info "Configure BOTCONVERSA_API_KEY e BOTCONVERSA_WEBHOOK_SECRET antes de continuar."
        log_info "Pressione ENTER quando terminar..."
        read -r
    fi
}

# Função para construir e iniciar Docker
start_docker() {
    log_info "Iniciando serviços Docker..."
    
    # Verificar se Docker está rodando
    if ! docker_running; then
        log_error "Docker não está rodando!"
        log_info "Inicie o Docker e execute este script novamente."
        exit 1
    fi
    
    # Construir imagens
    log_info "Construindo imagens Docker..."
    make build
    
    # Iniciar serviços (padrão Oracle - banco principal da aplicação)
    log_info "Iniciando serviços com Oracle..."
    make oracle-setup
    
    # Aguardar serviços estarem prontos
    log_info "Aguardando serviços estarem prontos..."
    sleep 30
    
    # Verificar status
    log_info "Verificando status dos serviços..."
    make status
}

# Função para testar instalação
test_installation() {
    log_info "Testando instalação..."
    
    # Aguardar um pouco mais para garantir que tudo está rodando
    sleep 10
    
    # Testar saúde da aplicação
    if command_exists curl; then
        log_info "Testando saúde da aplicação..."
        if curl -f http://localhost:8000/health >/dev/null 2>&1; then
            log_success "✅ Aplicação está respondendo!"
        else
            log_warning "⚠️  Aplicação ainda não está respondendo. Aguarde mais alguns minutos."
        fi
        
        log_info "Testando status do scheduler..."
        if curl -f http://localhost:8000/scheduler/status >/dev/null 2>&1; then
            log_success "✅ Scheduler está funcionando!"
        else
            log_warning "⚠️  Scheduler ainda não está respondendo."
        fi
    else
        log_warning "curl não está instalado. Não foi possível testar a aplicação automaticamente."
    fi
}

# Função para mostrar próximos passos
show_next_steps() {
=======
>>>>>>> d68998a574fb5f1a3f9edc3be084d95b00ad7be4
    echo ""
    print_color $GREEN "🎉 INSTALAÇÃO CONCLUÍDA COM SUCESSO!"
    echo ""
<<<<<<< HEAD
    echo -e "${BLUE}📱 Aplicação:${NC} http://localhost:8000"
    echo -e "${BLUE}🗄️  Banco:${NC} Oracle (porta 1521)"
    echo -e "${BLUE}📊 Status:${NC} make status"
    echo -e "${BLUE}📝 Logs:${NC} make logs"
    echo -e "${BLUE}🔧 CLI:${NC} make cli"
    echo ""
    echo -e "${BLUE}📚 Comandos úteis:${NC}"
    echo "  make help              # Ver todos os comandos"
    echo "  make restart           # Reiniciar serviços"
    echo "  make clean             # Limpar tudo"
    echo "  make postgresql-setup  # Mudar para PostgreSQL"
    echo "  make firebird-setup    # Mudar para Firebird"
=======
    print_color $CYAN "📱 Aplicação: http://localhost:5001"
    print_color $CYAN "🗄️  Banco de dados: $DATABASE_TYPE"
    print_color $CYAN "📊 Status: docker-compose ps"
    print_color $CYAN "📝 Logs: docker-compose logs -f"
    print_color $CYAN "🔧 CLI: docker-compose exec app python -m cli"
    echo ""
    print_color $YELLOW "📋 PRÓXIMOS PASSOS:"
    print_color $YELLOW "1. Configure sua API_KEY do BotConversa no arquivo .env"
    print_color $YELLOW "2. Configure o WEBHOOK_URL com o endereço do seu servidor"
    print_color $YELLOW "3. Teste a aplicação: curl http://localhost:5001/health"
>>>>>>> d68998a574fb5f1a3f9edc3be084d95b00ad7be4
    echo ""
    print_color $PURPLE "📚 Documentação completa: README.md"
    echo ""
}

# Função principal
main() {
    print_header
    check_root
    detect_os
    check_dependencies
    check_docker_running
    setup_env
    choose_database
    install_application
    verify_installation
    show_final_info
}

# Executar função principal
main "$@"
