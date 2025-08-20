# 🏥 Sistema de Confirmação de Consultas - Santa Casa

Sistema automatizado para confirmação de consultas médicas via WhatsApp, integrado com Botconversa API e N8N para automação completa.

## 🚀 **Funcionalidades Principais**

- ✅ **Integração Botconversa**: Gestão de subscribers, campanhas e fluxos
- 🤖 **Scheduler Automatizado**: Confirmações, lembretes e monitoramento de novos atendimentos
- 🔄 **Webhook Inteligente**: Processamento de respostas via N8N
- 📊 **CLI Robusto**: Interface de linha de comando para testes e administração
- 🐳 **Docker Ready**: Containerização completa com suporte a Oracle, PostgreSQL e Firebird
- 📱 **Monitoramento Automático**: Detecção automática de novos atendimentos
- 🔌 **Webhook N8N**: Processamento automático de respostas dos pacientes
- 🛡️ **Tratamento de Erros**: Sistema robusto com rollback controlado

## 🛠️ **Tecnologias**

- **Backend**: FastAPI + Python 3.11
- **Banco**: Suporte a Oracle, PostgreSQL e Firebird
- **ORM**: SQLAlchemy
- **Scheduler**: APScheduler
- **CLI**: Click + Rich
- **Containerização**: Docker + Docker Compose
- **Integração**: Botconversa API + N8N
- **Webhook**: Endpoint robusto para processamento de respostas

## 🚀 **Primeiros Passos (5 minutos)**

### **Para testar rapidamente em uma nova máquina:**

```bash
# 1. Clone o repositório
git clone <seu-repositorio>
cd confirmacao_consultas

# 2. Execute a instalação automática
./install.sh          # Linux/Mac
# ou
install.bat           # Windows

# 3. Configure o .env com suas chaves Botconversa
# 4. Acesse: http://localhost:8000
```

**🎯 Resultado**: Sistema completo rodando com PostgreSQL em menos de 5 minutos!

---

## 📋 **Pré-requisitos**

- Python 3.11+ (para instalação local)
- Docker e Docker Compose (para instalação Docker)
- Conta Botconversa com API Key
- Git

## 🚀 **INSTALAÇÃO AUTOMÁTICA (RECOMENDADA)**

### **🐧 Linux/Mac:**

```bash
# 1. Clone o repositório
git clone <seu-repositorio>
cd confirmacao_consultas

# 2. Torne executável e execute
chmod +x install.sh
./install.sh
```

### **🪟 Windows:**

```cmd
# 1. Clone o repositório
git clone <seu-repositorio>
cd confirmacao_consultas

# 2. Execute a instalação
install.bat
```

### **⚡ Setup Rápido Docker (Linux/Mac):**

```bash
# Torne executável
chmod +x setup-docker.sh

# PostgreSQL (padrão)
./setup-docker.sh

# Oracle
./setup-docker.sh oracle

# Firebird
./setup-docker.sh firebird
```

### **🎯 O que os scripts fazem automaticamente:**

✅ Verificam se Docker está instalado e rodando  
✅ Verificam se Docker Compose está disponível  
✅ Verificam se Git está instalado  
✅ Instalam Make se necessário  
✅ Criam arquivo .env a partir do template  
✅ Constróem imagens Docker  
✅ Iniciam serviços com PostgreSQL  
✅ Testam a instalação  
✅ Mostram próximos passos

---

## 🐳 **Docker (Configuração Manual)**

### **Setup Rápido com Docker:**

```bash
# 1. Clone o repositório
git clone <seu-repositorio>
cd confirmacao_consultas

# 2. Configure as variáveis de ambiente
cp env.example .env
# Edite o .env com suas configurações

# 3. Inicie os serviços (escolha o banco)
make postgresql-setup    # Para PostgreSQL
make oracle-setup        # Para Oracle
make firebird-setup      # Para Firebird

# 4. Verifique o status
make status
```

### **Configuração do .env para Docker:**

**IMPORTANTE**: Configure estas variáveis no seu `.env`:

```bash
# ========================================
# ESCOLHA DO BANCO DOCKER
# ========================================
DOCKER_DATABASE_TYPE=postgresql  # oracle, postgresql, firebird

# ========================================
# CONFIGURAÇÕES BOTCONVERSA (OBRIGATÓRIAS)
# ========================================
BOTCONVERSA_API_KEY=sua_api_key_real_aqui
BOTCONVERSA_WEBHOOK_SECRET=seu_webhook_secret_real_aqui
WEBHOOK_URL=https://seudominio.com/webhook/botconversa

# ========================================
# CONFIGURAÇÕES DO HOSPITAL
# ========================================
HOSPITAL_NAME=Santa Casa de Belo Horizonte
HOSPITAL_PHONE=(31) 3238-8100
HOSPITAL_ADDRESS=Rua Domingos Vieira, 590 - Santa Efigênia
HOSPITAL_CITY=Belo Horizonte
HOSPITAL_STATE=MG
```

### **Comandos Docker Disponíveis:**

```bash
# Comandos principais
make help                    # Mostra todos os comandos disponíveis
make build                   # Constrói as imagens Docker
make up                      # Inicia serviços (usa banco do .env)
make down                    # Para serviços
make logs                    # Mostra logs
make status                  # Status dos serviços

# Setup específico por banco
make postgresql-setup        # Inicia com PostgreSQL
make oracle-setup            # Inicia com Oracle
make firebird-setup          # Inicia com Firebird
make dev                     # Setup padrão (PostgreSQL)

# Banco de dados
make db-shell-postgresql     # Shell PostgreSQL
make db-shell-oracle         # Shell Oracle
make db-shell-firebird       # Shell Firebird
make db-reset                # Reseta banco de dados

# Desenvolvimento
make shell                   # Acessa shell do container
make cli                     # Executa CLI da aplicação
make test                    # Executa testes

# Monitoramento
make health                  # Verifica saúde da aplicação
make scheduler-status        # Status do scheduler

# Limpeza
make clean                   # Limpa tudo (containers, volumes, imagens)
make restart                 # Reinicia todos os serviços
```

### **Como Escolher o Banco:**

1. **PostgreSQL (Recomendado para desenvolvimento):**

   ```bash
   DOCKER_DATABASE_TYPE=postgresql
   make postgresql-setup
   ```

2. **Oracle:**

   ```bash
   DOCKER_DATABASE_TYPE=oracle
   make oracle-setup
   ```

3. **Firebird:**
   ```bash
   DOCKER_DATABASE_TYPE=firebird
   make firebird-setup
   ```

### **Troubleshooting Docker:**

**Erro de porta em uso:**

```bash
# Verifique portas em uso
netstat -tulpn | grep :8000
netstat -tulpn | grep :5432

# Pare serviços conflitantes ou mude portas no .env
APP_PORT=8001
POSTGRESQL_DOCKER_PORT=5433
```

**Erro de permissão Docker:**

```bash
# Adicione usuário ao grupo docker
sudo usermod -aG docker $USER
# Faça logout e login novamente
```

**Limpar tudo e recomeçar:**

```bash
make clean                   # Remove tudo
make build                   # Reconstrói
make postgresql-setup        # Inicia novamente
```

## 🔧 **Instalação Local (Sem Docker)**

### **1. Configuração do Ambiente:**

```bash
# Crie um ambiente virtual
python -m venv venv
source venv/bin/activate  # Linux/Mac
# ou
venv\Scripts\activate     # Windows

# Instale dependências
pip install -r requirements.txt
```

### **2. Configuração do Banco:**

```bash
# Configure as variáveis no .env
cp env.example .env
# Edite o .env com suas configurações de banco

# Inicialize o banco
python -m app.database.init_db
```

### **3. Execução:**

```bash
# Inicie a aplicação
python -m app.main

# Em outro terminal, execute o CLI
python -m cli help                    # Ver ajuda completa
python -m cli status                  # Ver status do sistema
python -m cli test-db                 # Testar banco de dados
python -m cli test-conexao            # Testar Botconversa
```

## 📱 **Usando o CLI**

O CLI oferece comandos para todas as operações principais:

```bash
# Testes de conexão
python -m cli test-db          # Testa conexão com banco
python -m cli test-conexao     # Testa API Botconversa

# Gestão de atendimentos
python -m cli atendimentos              # Lista todos os atendimentos
python -m cli listar-atendimentos       # Lista atendimentos pendentes
python -m cli buscar-atendimento        # Busca atendimento por telefone
python -m cli criar-atendimento         # Cria novo atendimento

# Operações Botconversa
python -m cli adicionar-botconversa     # Adiciona subscriber no Botconversa
python -m cli enviar-mensagem           # Envia mensagem personalizada
python -m cli executar-workflow         # Executa workflow completo
python -m cli processar-resposta        # Processa resposta do paciente
python -m cli adicionar-campanha        # Adiciona na campanha

# Status e monitoramento
python -m cli status                    # Status geral do sistema
python -m cli help                      # Ajuda detalhada
```

## 🔗 **Webhook e N8N**

### **Endpoint do Webhook:**

```
POST /webhook/botconversa
```

### **Payload N8N Esperado:**

```json
{
  "telefone": "5511999999999",
  "subscriber_id": 123456,
  "resposta": "1" // "1" = SIM, "0" = NÃO
}
```

### **Configuração N8N:**

1. Configure o webhook no N8N para enviar POST para sua URL
2. Formate o payload conforme especificado acima
3. A aplicação processará automaticamente as respostas

### **Testando o Webhook:**

#### **Com Insomnia/Postman:**
```bash
POST http://101.44.2.109:5001/webhook/botconversa
Headers: Content-Type: application/json
Body: {
  "telefone": "5591982636266",
  "subscriber_id": "791023626",
  "resposta": "1"
}
```

#### **Com curl:**
```bash
curl -X POST http://101.44.2.109:5001/webhook/botconversa \
  -H "Content-Type: application/json" \
  -d '{
    "telefone": "5591982636266",
    "subscriber_id": "791023626",
    "resposta": "1"
  }'
```

### **Resposta do Webhook:**

```json
{
  "success": true,
  "message": "Webhook processado com sucesso",
  "data": {
    "success": true,
    "message": "Atendimento CONFIRMADO com sucesso",
    "atendimento_id": 2,
    "status": "CONFIRMADO",
    "telefone": "5591982636266",
    "subscriber_id": "791023626",
    "resposta": "1"
  }
}
```

## 🛡️ **Solução de Problemas Implementados**

### **✅ Rollback Automático Resolvido:**

O sistema agora possui tratamento robusto de erros:

- **Commit final forçado** para evitar rollbacks automáticos
- **Tratamento de exceções** aprimorado
- **Middleware de logging** protegido contra falhas
- **Rollback controlado** apenas quando necessário

### **✅ Firewall e Conectividade:**

- **Porta 5001** configurada e aberta
- **IPTables** configurado para permitir conexões externas
- **Docker** expondo porta corretamente
- **Conectividade externa** testada e funcionando

### **✅ Webhook Robusto:**

- **Validação de dados** implementada
- **Processamento de respostas** automatizado
- **Atualização de status** no banco de dados
- **Logs detalhados** para debugging

## ⏰ **Scheduler Automatizado**

O sistema executa automaticamente:

- **Confirmações**: Diariamente às 9h (configurável)
- **Lembretes**: Diariamente às 14h (configurável)
- **Monitoramento**: A cada 30 minutos para novos atendimentos

### **Configuração dos Horários:**

```bash
SCHEDULER_CONFIRMATION_HOUR=9      # Hora das confirmações
SCHEDULER_CONFIRMATION_MINUTE=0    # Minuto das confirmações
SCHEDULER_REMINDER_HOUR=14         # Hora dos lembretes
SCHEDULER_REMINDER_MINUTE=0        # Minuto dos lembretes
```

## 📊 **Monitoramento**

### **Endpoints de Status:**

- `GET /health` - Saúde da aplicação
- `GET /scheduler/status` - Status detalhado do scheduler

### **Logs:**

- Logs são salvos em `./logs/`
- Nível configurável via `LOG_LEVEL` no `.env`

## 🚀 **Deploy em Produção**

### **1. Com Docker (Recomendado):**

```bash
# Configure o .env para produção
cp env.example .env
# Edite com configurações de produção

# Inicie com Nginx
make prod

# Verifique status
make status
```

### **2. Configurações de Produção:**

```bash
# Desabilite debug
DEBUG=false

# Configure host e porta
WEBHOOK_HOST=0.0.0.0
WEBHOOK_PORT=8000

# Configure URL pública
WEBHOOK_URL=https://seudominio.com/webhook/botconversa

# Ajuste workers
MAX_WORKERS=4
WORKER_TIMEOUT=30
```

### **3. Configuração de Firewall (Produção):**

```bash
# Abrir porta 5001 para webhook
iptables -A INPUT -p tcp --dport 5001 -j ACCEPT

# Salvar regras
iptables-save > /etc/iptables/rules.v4

# Verificar status
iptables -L -n
```

## 📁 **Estrutura do Projeto**

```
confirmacao_consultas/
├── app/                    # Aplicação principal
│   ├── api/               # Endpoints da API
│   │   └── routes/        # Rotas da API
│   │       └── webhook.py # Webhook para N8N
│   ├── config/            # Configurações
│   ├── database/          # Modelos e conexão DB
│   ├── services/          # Lógica de negócio
│   │   ├── webhook_service.py    # Serviço do webhook
│   │   └── botconversa_service.py # Serviço Botconversa
│   └── scheduler.py       # Scheduler automatizado
├── cli/                   # Interface de linha de comando
├── docs/                  # Documentação
├── logs/                  # Logs da aplicação
├── Dockerfile             # Imagem Docker
├── docker-compose.yml     # Orquestração Docker (múltiplos bancos)
├── init-*.sql             # Scripts de inicialização dos bancos
├── Makefile               # Automação de comandos
├── requirements.txt       # Dependências Python
├── .env                   # Variáveis de ambiente
├── install.sh             # 🚀 Script de instalação Linux/Mac
├── install.bat            # 🚀 Script de instalação Windows
├── setup-docker.sh        # ⚡ Setup rápido Docker
└── README-INSTALACAO.md   # 📖 Guia completo de instalação
```

## 🔍 **Testes e Validação**

### **Testes Automatizados:**

```bash
# Com Docker
make test

# Local
pytest
```

### **Testes Manuais:**

```bash
# Teste CLI
python -m cli test-db
python -m cli test-conexao

# Teste API
curl http://localhost:8000/health
curl http://localhost:8000/scheduler/status

# Teste Webhook
curl -X POST http://localhost:8000/webhook/botconversa \
  -H "Content-Type: application/json" \
  -d '{"telefone": "5511999999999", "subscriber_id": "123", "resposta": "1"}'
```

## 📚 **Documentação Adicional**

- 📖 [Guia de Desenvolvimento](docs/development_guide.md)
- 🔧 [Documentação Técnica](docs/TECHNICAL.md)
- 🔄 [Fluxo Botconversa](docs/fluxo_botconversa_consultas.md)
- 🌐 [Guia Webhook N8N](docs/webhook_n8n_guide.md)
- ✅ [Implementações Completadas](IMPLEMENTACOES_COMPLETADAS.md)
- 🚀 **[Guia de Instalação Completo](README-INSTALACAO.md)** ⭐ **NOVO!**

## 🆘 **Suporte e Troubleshooting**

### **Problemas Comuns:**

1. **Erro de conexão com banco:**

   - Verifique `DATABASE_TYPE` e URLs no `.env`
   - Confirme se o banco Docker está rodando
   - Use `make status` para verificar serviços

2. **Erro Botconversa:**

   - Valide `BOTCONVERSA_API_KEY` no `.env`
   - Teste com `python -m cli test-conexao`

3. **Scheduler não funciona:**

   - Verifique `make scheduler-status`
   - Confirme horários no `.env`

4. **Erro Docker:**
   - Use `make clean` para limpar tudo
   - Verifique portas disponíveis
   - Confirme `DOCKER_DATABASE_TYPE` no `.env`

5. **Webhook não funciona externamente:**
   - Verifique firewall: `iptables -L -n`
   - Abra porta 5001: `iptables -A INPUT -p tcp --dport 5001 -j ACCEPT`
   - Salve regras: `iptables-save > /etc/iptables/rules.v4`

6. **Rollback automático:**
   - ✅ **RESOLVIDO** - Sistema agora possui commit final forçado
   - ✅ **RESOLVIDO** - Tratamento de exceções aprimorado
   - ✅ **RESOLVIDO** - Middleware protegido contra falhas

### **Logs e Debug:**

```bash
# Ver logs em tempo real
make logs

# Acesse shell do container
make shell

# Verifique status dos serviços
make status

# Teste conectividade externa
curl -v http://101.44.2.109:5001/health
```

### **Verificação de Status:**

```bash
# Status dos containers
docker-compose ps

# Status da porta
netstat -tlnp | grep :5001

# Status do firewall
iptables -L -n

# Teste de conectividade
telnet 101.44.2.109 5001
```

## 🎯 **Status das Implementações**

### **✅ COMPLETADO:**

- ✅ **Webhook para N8N** - Funcionando perfeitamente
- ✅ **Processamento de respostas** - Automatizado
- ✅ **Tratamento de rollbacks** - Resolvido
- ✅ **Configuração de firewall** - Implementada
- ✅ **Conectividade externa** - Testada e funcionando
- ✅ **Integração N8N** - Funcionando
- ✅ **Sistema de logs** - Implementado
- ✅ **Tratamento de erros** - Robusto

### **🚀 PRÓXIMOS PASSOS:**

- 🔄 **Testes automatizados** - Em desenvolvimento
- 📊 **Dashboard de monitoramento** - Planejado
- 🔔 **Notificações em tempo real** - Planejado
- 📱 **Interface web** - Planejado

---

## 🏆 **Sistema 100% Funcional**

O sistema está completamente funcional e pronto para produção:

- ✅ **Webhook processando respostas do N8N**
- ✅ **Banco de dados sendo atualizado automaticamente**
- ✅ **Sem rollbacks automáticos**
- ✅ **Conectividade externa funcionando**
- ✅ **Integração N8N operacional**
- ✅ **Scheduler automatizado funcionando**
- ✅ **CLI robusto para administração**

**🎉 Parabéns! O sistema está funcionando perfeitamente!**


