#!/bin/bash

# ========================================
# SETUP DOCKER - SISTEMA DE CONFIRMAÇÃO DE CONSULTAS
# Script para configuração rápida do Docker
# ========================================

set -e

# Cores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

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

# Função para mostrar ajuda
show_help() {
    echo "Uso: $0 [OPÇÃO]"
    echo ""
    echo "Opções:"
    echo "  oracle        Inicia com Oracle (padrão - banco principal)"
    echo "  postgresql    Inicia com PostgreSQL"
    echo "  firebird      Inicia com Firebird"
    echo "  clean         Limpa tudo e reconstrói"
    echo "  status        Mostra status dos serviços"
    echo "  logs          Mostra logs dos serviços"
    echo "  help          Mostra esta ajuda"
    echo ""
    echo "Exemplos:"
    echo "  $0                # Inicia com Oracle"
    echo "  $0 postgresql     # Inicia com PostgreSQL"
    echo "  $0 clean          # Limpa tudo e reconstrói"
}

# Função para verificar Docker
check_docker() {
    if ! docker info >/dev/null 2>&1; then
        log_error "Docker não está rodando!"
        log_info "Inicie o Docker e execute novamente."
        exit 1
    fi
}

# Função para setup PostgreSQL
setup_postgresql() {
    log_info "Configurando PostgreSQL..."
    
    # Parar serviços existentes
    docker-compose down 2>/dev/null || true
    
    # Iniciar PostgreSQL
    docker-compose --profile postgresql up -d
    
    # Aguardar banco estar pronto
    log_info "Aguardando PostgreSQL estar pronto..."
    sleep 15
    
    # Verificar status
    if docker-compose ps | grep -q "Up"; then
        log_success "PostgreSQL iniciado com sucesso!"
    else
        log_error "Erro ao iniciar PostgreSQL!"
        exit 1
    fi
}

# Função para setup Oracle
setup_oracle() {
    log_info "Configurando Oracle..."
    
    # Parar serviços existentes
    docker-compose down 2>/dev/null || true
    
    # Iniciar Oracle
    docker-compose --profile oracle up -d
    
    # Aguardar banco estar pronto (Oracle demora mais)
    log_info "Aguardando Oracle estar pronto (pode demorar alguns minutos)..."
    sleep 120
    
    # Verificar status
    if docker-compose ps | grep -q "Up"; then
        log_success "Oracle iniciado com sucesso!"
    else
        log_error "Erro ao iniciar Oracle!"
        exit 1
    fi
}

# Função para setup Firebird
setup_firebird() {
    log_info "Configurando Firebird..."
    
    # Parar serviços existentes
    docker-compose down 2>/dev/null || true
    
    # Iniciar Firebird
    docker-compose --profile firebird up -d
    
    # Aguardar banco estar pronto
    log_info "Aguardando Firebird estar pronto..."
    sleep 30
    
    # Verificar status
    if docker-compose ps | grep -q "Up"; then
        log_success "Firebird iniciado com sucesso!"
    else
        log_error "Erro ao iniciar Firebird!"
        exit 1
    fi
}

# Função para limpar tudo
clean_all() {
    log_info "Limpando tudo..."
    
    # Parar e remover containers
    docker-compose down -v --rmi all 2>/dev/null || true
    
    # Limpar imagens não utilizadas
    docker system prune -f
    
    log_success "Limpeza concluída!"
}

# Função para mostrar status
show_status() {
    log_info "Status dos serviços:"
    docker-compose ps
}

# Função para mostrar logs
show_logs() {
    log_info "Logs dos serviços:"
    docker-compose logs -f
}

# Função para testar aplicação
test_app() {
    log_info "Testando aplicação..."
    
    # Aguardar um pouco
    sleep 10
    
    # Testar saúde
    if command -v curl >/dev/null 2>&1; then
        if curl -f http://localhost:8000/health >/dev/null 2>&1; then
            log_success "✅ Aplicação está respondendo!"
        else
            log_warning "⚠️  Aplicação ainda não está respondendo"
        fi
        
        if curl -f http://localhost:8000/scheduler/status >/dev/null 2>&1; then
            log_success "✅ Scheduler está funcionando!"
        else
            log_warning "⚠️  Scheduler ainda não está respondendo"
        fi
    else
        log_warning "curl não está instalado. Teste manualmente:"
        log_info "  http://localhost:8000/health"
        log_info "  http://localhost:8000/scheduler/status"
    fi
}

# Função principal
main() {
    # Verificar argumentos
    if [ $# -eq 0 ]; then
        # Sem argumentos, usar Oracle como padrão (banco principal da aplicação)
        check_docker
        setup_oracle
        test_app
        show_status
        return 0
    fi
    
    case "$1" in
        oracle)
            check_docker
            setup_oracle
            test_app
            show_status
            ;;
        postgresql)
            check_docker
            setup_postgresql
            test_app
            show_status
            ;;
        firebird)
            check_docker
            setup_firebird
            test_app
            show_status
            ;;
        clean)
            clean_all
            ;;
        status)
            show_status
            ;;
        logs)
            show_logs
            ;;
        help|--help|-h)
            show_help
            ;;
        *)
            log_error "Opção inválida: $1"
            show_help
            exit 1
            ;;
    esac
}

# Executar função principal
main "$@"
