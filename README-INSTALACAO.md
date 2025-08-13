# 🚀 **GUIA DE INSTALAÇÃO COMPLETO**

## 📋 **Visão Geral**

Este guia fornece instruções detalhadas para instalar o **Sistema de Confirmação de Consultas** em diferentes sistemas operacionais usando Docker.

## 🎯 **Opções de Instalação**

### **1. 🐳 Instalação Automática (RECOMENDADA)**

- **Linux/Mac**: `./install.sh`
- **Windows**: `install.bat`

### **2. 🔧 Instalação Manual**

- Configuração passo a passo
- Para usuários avançados

### **3. ⚡ Setup Rápido Docker**

- **Linux/Mac**: `./setup-docker.sh [banco]`

## 🐧 **LINUX/MAC - Instalação Automática**

### **Pré-requisitos:**

- Docker Desktop ou Docker Engine
- Git
- Terminal com suporte a cores

### **Passos:**

```bash
# 1. Clone o repositório
git clone <seu-repositorio>
cd confirmacao_consultas

# 2. Torne o script executável
chmod +x install.sh

# 3. Execute a instalação
./install.sh
```

### **O que o script faz automaticamente:**

✅ Verifica se Docker está instalado e rodando  
✅ Verifica se Docker Compose está disponível  
✅ Verifica se Git está instalado  
✅ Instala Make se necessário  
✅ Cria arquivo .env a partir do template  
✅ Constrói imagens Docker  
✅ Inicia serviços com PostgreSQL  
✅ Testa a instalação  
✅ Mostra próximos passos

## 🪟 **WINDOWS - Instalação Automática**

### **Pré-requisitos:**

- Docker Desktop para Windows
- Git para Windows
- PowerShell ou CMD

### **Passos:**

```cmd
# 1. Clone o repositório
git clone <seu-repositorio>
cd confirmacao_consultas

# 2. Execute a instalação
install.bat
```

### **O que o script faz automaticamente:**

✅ Verifica se Docker Desktop está instalado  
✅ Verifica se Docker está rodando  
✅ Verifica se Git está instalado  
✅ Cria arquivo .env a partir do template  
✅ Constrói imagens Docker  
✅ Inicia serviços com PostgreSQL  
✅ Testa a instalação  
✅ Mostra próximos passos

## 🔧 **Instalação Manual (Passo a Passo)**

### **1. Pré-requisitos**

#### **Docker:**

```bash
# Ubuntu/Debian
sudo apt-get update
sudo apt-get install docker.io docker-compose

# CentOS/RHEL
sudo yum install docker docker-compose

# macOS
brew install docker docker-compose

# Windows
# Baixe Docker Desktop: https://docs.docker.com/desktop/install/windows/
```

#### **Git:**

```bash
# Ubuntu/Debian
sudo apt-get install git

# CentOS/RHEL
sudo yum install git

# macOS
brew install git

# Windows
# Baixe: https://git-scm.com/download/win
```

#### **Make:**

```bash
# Ubuntu/Debian
sudo apt-get install make

# CentOS/RHEL
sudo yum install make

# macOS
brew install make

# Windows
choco install make
```

### **2. Clone do Repositório**

```bash
git clone <seu-repositorio>
cd confirmacao_consultas
```

### **3. Configuração do Ambiente**

```bash
# Copiar template de configuração
cp env.example .env

# Editar configurações
nano .env  # Linux/Mac
# ou
notepad .env  # Windows
```

#### **Configurações Obrigatórias no .env:**

```bash
# ESCOLHA DO BANCO
DOCKER_DATABASE_TYPE=postgresql  # ou oracle, firebird

# BOTCONVERSA (OBRIGATÓRIO)
BOTCONVERSA_API_KEY=sua_api_key_real_aqui
BOTCONVERSA_WEBHOOK_SECRET=seu_webhook_secret_real_aqui
WEBHOOK_URL=https://seudominio.com/webhook/botconversa

# HOSPITAL
HOSPITAL_NAME=Santa Casa de Belo Horizonte
HOSPITAL_PHONE=(31) 3238-8100
HOSPITAL_ADDRESS=Rua Domingos Vieira, 590 - Santa Efigênia
HOSPITAL_CITY=Belo Horizonte
HOSPITAL_STATE=MG
```

### **4. Iniciar Serviços**

#### **Com PostgreSQL (Recomendado):**

```bash
make postgresql-setup
```

#### **Com Oracle:**

```bash
make oracle-setup
```

#### **Com Firebird:**

```bash
make firebird-setup
```

### **5. Verificar Instalação**

```bash
# Status dos serviços
make status

# Testar aplicação
curl http://localhost:8000/health
curl http://localhost:8000/scheduler/status

# Ver logs
make logs
```

## ⚡ **Setup Rápido Docker**

### **Uso do Script:**

```bash
# Torne executável
chmod +x setup-docker.sh

# PostgreSQL (padrão)
./setup-docker.sh

# Oracle
./setup-docker.sh oracle

# Firebird
./setup-docker.sh firebird

# Limpar tudo
./setup-docker.sh clean

# Ver status
./setup-docker.sh status

# Ver logs
./setup-docker.sh logs
```

## 🧪 **Testando a Instalação**

### **1. Verificar Serviços:**

```bash
make status
# Deve mostrar todos os serviços como "Up"
```

### **2. Testar Endpoints:**

```bash
# Saúde da aplicação
curl http://localhost:8000/health
# Resposta esperada: {"status": "healthy"}

# Status do scheduler
curl http://localhost:8000/scheduler/status
# Deve mostrar status dos jobs
```

### **3. Testar CLI:**

```bash
# Acessar container
make shell

# Testar conexão com banco
python -m cli test-db

# Testar Botconversa
python -m cli test-botconversa
```

## 🚨 **Troubleshooting**

### **Problema: Docker não está rodando**

```bash
# Linux
sudo systemctl start docker
sudo systemctl enable docker

# macOS
open -a Docker

# Windows
# Inicie Docker Desktop
```

### **Problema: Porta já está em uso**

```bash
# Verificar portas
netstat -tulpn | grep :8000
netstat -tulpn | grep :5432

# Mudar portas no .env
APP_PORT=8001
POSTGRESQL_DOCKER_PORT=5433
```

### **Problema: Erro de permissão**

```bash
# Linux
sudo usermod -aG docker $USER
# Faça logout e login novamente

# macOS/Windows
# Execute como administrador
```

### **Problema: Erro de memória**

```bash
# Aumentar memória do Docker
# Docker Desktop: Settings > Resources > Memory
# Linux: /etc/docker/daemon.json
```

### **Problema: Banco não inicia**

```bash
# Ver logs
make logs

# Limpar e recomeçar
make clean
make postgresql-setup
```

## 📊 **Comandos Úteis**

### **Gerenciamento de Serviços:**

```bash
make help              # Ver todos os comandos
make status            # Status dos serviços
make logs              # Ver logs
make restart           # Reiniciar serviços
make down              # Parar serviços
```

### **Banco de Dados:**

```bash
make db-shell          # Acessar shell do banco
make db-reset          # Resetar banco
```

### **Desenvolvimento:**

```bash
make shell             # Acessar container
make cli               # Executar CLI
make test              # Executar testes
```

### **Limpeza:**

```bash
make clean             # Limpar tudo
make clean-logs        # Limpar logs
```

## 🌐 **Configuração para Acesso Externo**

### **1. Mudar Host no .env:**

```bash
WEBHOOK_HOST=0.0.0.0
```

### **2. Configurar Firewall:**

```bash
# Ubuntu/Debian
sudo ufw allow 8000
sudo ufw allow 5432

# CentOS/RHEL
sudo firewall-cmd --permanent --add-port=8000/tcp
sudo firewall-cmd --permanent --add-port=5432/tcp
sudo firewall-cmd --reload
```

### **3. Acessar de outras máquinas:**

```
http://IP_DA_MAQUINA:8000
```

## 📚 **Próximos Passos**

### **1. Configurar Botconversa:**

- Obter API Key
- Configurar webhook
- Testar integração

### **2. Configurar N8N:**

- Instalar N8N
- Configurar webhook
- Testar fluxo

### **3. Configurar Produção:**

- Mudar DEBUG=false
- Configurar domínio
- Configurar SSL

## 🆘 **Suporte**

### **Documentação:**

- **README.md** - Visão geral do projeto
- **docs/** - Documentação técnica
- **IMPLEMENTACOES_COMPLETADAS.md** - Status das funcionalidades

### **Comandos de Ajuda:**

```bash
make help              # Ajuda do Makefile
./setup-docker.sh help # Ajuda do setup Docker
```

### **Logs e Debug:**

```bash
make logs              # Logs em tempo real
make status            # Status dos serviços
docker-compose logs    # Logs específicos
```

---

**🎉 Agora você tem um sistema completo de instalação automática!**

**Para testar em outra máquina, basta executar:**

- **Linux/Mac**: `./install.sh`
- **Windows**: `install.bat`
