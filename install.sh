#!/bin/bash

# ========================================
# SISTEMA DE CONFIRMAÇÃO DE CONSULTAS - SANTA CASA
# Script de Instalação Automática
# ========================================

set -e  # Para o script se houver erro

# Cores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Função para log colorido
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Função para verificar se comando existe
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Função para verificar se Docker está rodando
docker_running() {
    docker info >/dev/null 2>&1
}

# Função para aguardar Docker estar pronto
wait_for_docker() {
    log_info "Aguardando Docker estar pronto..."
    local max_attempts=30
    local attempt=1
    
    while [ $attempt -le $max_attempts ]; do
        if docker_running; then
            log_success "Docker está rodando!"
            return 0
        fi
        
        log_info "Tentativa $attempt/$max_attempts - Aguardando Docker..."
        sleep 2
        attempt=$((attempt + 1))
    done
    
    log_error "Docker não está rodando após $max_attempts tentativas"
    return 1
}

# Função para verificar pré-requisitos
check_prerequisites() {
    log_info "Verificando pré-requisitos..."
    
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
    
    # Iniciar serviços (padrão PostgreSQL)
    log_info "Iniciando serviços com PostgreSQL..."
    make postgresql-setup
    
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
    echo ""
    echo -e "${GREEN}========================================${NC}"
    echo -e "${GREEN}🎉 INSTALAÇÃO CONCLUÍDA COM SUCESSO! 🎉${NC}"
    echo -e "${GREEN}========================================${NC}"
    echo ""
    echo -e "${BLUE}📱 Aplicação:${NC} http://localhost:8000"
    echo -e "${BLUE}🗄️  Banco:${NC} PostgreSQL (porta 5432)"
    echo -e "${BLUE}📊 Status:${NC} make status"
    echo -e "${BLUE}📝 Logs:${NC} make logs"
    echo -e "${BLUE}🔧 CLI:${NC} make cli"
    echo ""
    echo -e "${BLUE}📚 Comandos úteis:${NC}"
    echo "  make help              # Ver todos os comandos"
    echo "  make restart           # Reiniciar serviços"
    echo "  make clean             # Limpar tudo"
    echo "  make oracle-setup      # Mudar para Oracle"
    echo "  make firebird-setup    # Mudar para Firebird"
    echo ""
    echo -e "${BLUE}🌐 Para acessar de outras máquinas:${NC}"
    echo "  - Configure o IP da máquina no .env"
    echo "  - Ajuste as configurações de firewall"
    echo ""
    echo -e "${BLUE}📖 Documentação:${NC} README.md"
    echo ""
}

# Função principal
main() {
    echo -e "${BLUE}========================================${NC}"
    echo -e "${BLUE}🏥 SISTEMA DE CONFIRMAÇÃO DE CONSULTAS${NC}"
    echo -e "${BLUE}🐳 INSTALADOR DOCKER AUTOMÁTICO${NC}"
    echo -e "${BLUE}========================================${NC}"
    echo ""
    
    # Verificar pré-requisitos
    check_prerequisites
    
    # Configurar ambiente
    setup_environment
    
    # Iniciar Docker
    start_docker
    
    # Testar instalação
    test_installation
    
    # Mostrar próximos passos
    show_next_steps
}

# Executar função principal
main "$@"
