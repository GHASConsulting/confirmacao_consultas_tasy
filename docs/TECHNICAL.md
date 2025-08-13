# Documentação Técnica - Sistema de Confirmação de Consultas

## 🆕 **ARQUITETURA ATUALIZADA**

O sistema foi completamente reestruturado para integrar com **Botconversa** e **N8N**, oferecendo uma solução robusta e automatizada para confirmação de consultas médicas.

## Arquitetura do Sistema

### Visão Geral

O sistema é construído seguindo uma arquitetura em camadas com separação clara de responsabilidades:

```
┌─────────────────────────────────────────────────────────────┐
│                    FastAPI Application                      │
├─────────────────────────────────────────────────────────────┤
│                    API Routes Layer                         │
│  ┌─────────────────┐ ┌─────────────────┐ ┌─────────────────┐ │
│  │ Botconversa     │ │ Webhook         │ │ Scheduler       │ │
│  │ Test Routes     │ │ Intelligent     │ │ Status          │ │
│  └─────────────────┘ └─────────────────┘ └─────────────────┘ │
├─────────────────────────────────────────────────────────────┤
│                   Services Layer                            │
│  ┌─────────────────┐ ┌─────────────────┐ ┌─────────────────┐ │
│  │ Botconversa     │ │ Webhook         │ │ Appointment     │ │
│  │ Service         │ │ Service         │ │ Scheduler       │ │
│  └─────────────────┘ └─────────────────┘ └─────────────────┘ │
├─────────────────────────────────────────────────────────────┤
│                   Data Access Layer                         │
│  ┌─────────────────┐ ┌─────────────────┐ ┌─────────────────┐ │
│  │ SQLAlchemy      │ │ Models          │ │ Database        │ │
│  │ ORM             │ │ (Atendimento    │ │ Connection      │ │
│  │                 │ │  SantaCasa)     │ │                 │ │
│  └─────────────────┘ └─────────────────┘ └─────────────────┘ │
├─────────────────────────────────────────────────────────────┤
│                    PostgreSQL Database                      │
│                    (Schema: SantaCasa)                      │
└─────────────────────────────────────────────────────────────┘
```

## 🔄 **Fluxo de Integração**

### **1. Envio de Mensagens**

```
Scheduler → BotconversaService → Botconversa API → WhatsApp
```

### **2. Recebimento de Respostas**

```
WhatsApp → Botconversa → N8N → Webhook Inteligente → Database
```

### **3. Processamento Automático**

```
Webhook → Detecção N8N → Atualização Status → Logging
```

## Componentes Principais

### 1. Configuração (`app/config.py`)

- Gerencia todas as configurações via variáveis de ambiente
- Usa Pydantic Settings para validação automática
- Suporte a diferentes ambientes (dev, staging, prod)
- **Novo:** Configurações de Botconversa, N8N e webhook

### 2. Banco de Dados (`app/database.py`)

- Configuração do SQLAlchemy com PostgreSQL
- Pool de conexões otimizado
- Context manager para sessões
- **Novo:** Schema `SantaCasa` configurado

### 3. Modelos (`app/models.py`)

- **Atendimento**: Modelo unificado com schema SantaCasa
- **StatusConfirmacao**: Enum de status atualizado
- **Campos de controle**: Para Botconversa e lembretes
- **Relacionamentos**: Simplificados e otimizados

### 4. Schemas (`app/schemas.py`)

- Validação de entrada/saída com Pydantic
- **Novo:** `N8NWebhookData` para dados do N8N
- Serialização automática de modelos
- Documentação automática da API

### 5. Serviços

#### BotconversaService (`app/services/botconversa_service.py`)

- **Integração completa** com API Botconversa
- **Envio de mensagens** personalizadas
- **Gestão de campanhas** e subscribers
- **Envio de fluxos** interativos
- **Workflow completo** de confirmação

#### WebhookService (`app/services/webhook_service.py`)

- **Detecção inteligente** de dados N8N vs tradicionais
- **Processamento** de respostas "1" e "0"
- **Atualização automática** do banco de dados
- **Validação robusta** e logging completo

#### AppointmentScheduler (`app/scheduler.py`)

- **Jobs agendados** para confirmações e lembretes
- **Controle de frequência** configurável
- **Horários personalizáveis** via variáveis de ambiente
- **Lembretes inteligentes** (48h e 12h)

### 6. API Routes (`app/api/routes/`)

- **Botconversa Test**: Endpoints para testes e workflows
- **Webhook Intelligent**: Endpoint com detecção automática
- **Scheduler Status**: Monitoramento do agendador
- Validação de entrada e tratamento de erros

## Fluxo de Dados

### 1. Criação de Atendimento

```
Cliente → API → Database (Schema SantaCasa)
```

### 2. Envio de Confirmação

```
Scheduler → BotconversaService → Botconversa API → WhatsApp
```

### 3. Recebimento de Resposta

```
WhatsApp → Botconversa → N8N → Webhook Inteligente → Database
```

### 4. Processamento Automático

```
Webhook → Detecção N8N → Atualização Status → Logging
```

## 🔧 **Novos Endpoints**

### **Webhook Inteligente**

- `POST /webhook/botconversa` - Recebe dados do N8N
- `GET /webhook/botconversa/health` - Health check do webhook

### **Botconversa Test**

- `POST /test/workflow/{atendimento_id}` - Executa workflow completo
- `POST /test/subscriber/{subscriber_id}/send_flow` - Envia fluxo
- `GET /test/campanhas` - Lista campanhas disponíveis

### **Scheduler**

- `GET /scheduler/status` - Status do agendador
- `GET /health` - Health check geral da aplicação

## Configurações de Ambiente

### Desenvolvimento

```env
DEBUG=True
LOG_LEVEL=DEBUG
DATABASE_URL=oracle+cx_oracle://dev_user:dev_pass@localhost:1521/dev_db
```

### Produção

```env
DEBUG=False
LOG_LEVEL=INFO
DATABASE_URL=oracle+cx_oracle://prod_user:prod_pass@prod_host:1521/prod_db
```

## Segurança

### Validação de Entrada

- Pydantic schemas para validação
- Sanitização de dados
- Proteção contra SQL injection

### Autenticação (Futuro)

- JWT tokens
- Rate limiting
- API keys para webhooks

### Logs de Auditoria

- Todas as operações são logadas
- Rotação automática de logs
- Níveis de log configuráveis

## Performance

### Otimizações de Banco

- Índices em campos de busca
- Queries otimizadas
- Pool de conexões

### Cache (Futuro)

- Redis para cache de dados
- Cache de configurações
- Cache de templates de mensagem

### Monitoramento

- Health checks
- Métricas de performance
- Alertas automáticos

## Escalabilidade

### Horizontal Scaling

- Stateless application
- Load balancer ready
- Container deployment

### Vertical Scaling

- Configuração de workers
- Pool de conexões ajustável
- Memory optimization

## Integrações

### WhatsApp APIs Suportadas

- Z-API
- Twilio
- WhatsApp Business API
- Extensível para outros provedores

### OpenAI

- GPT-4 (padrão)
- Configurável para outros modelos
- Fallback para interpretação simples

### Banco de Dados

- Oracle (padrão)
- Extensível para PostgreSQL/MySQL

## Deployment

### Docker

- Multi-stage build
- Non-root user
- Health checks
- Volume mounts para logs

### Docker Compose

- Serviços orquestrados
- Environment variables
- Nginx reverse proxy

### Kubernetes (Futuro)

- Deployments
- Services
- ConfigMaps
- Secrets

## Monitoramento e Observabilidade

### Logs

- Structured logging com Loguru
- Rotação automática
- Níveis configuráveis

### Métricas

- Endpoint de estatísticas
- Métricas de negócio
- Performance metrics

### Alertas

- Health check failures
- Database connection issues
- WhatsApp API errors

## Testes

### Unit Tests

- Testes de serviços
- Testes de modelos
- Mock de dependências externas

### Integration Tests

- Testes de API
- Testes de banco de dados
- Testes de webhook

### E2E Tests

- Fluxo completo de confirmação
- Testes de WhatsApp
- Testes de scheduler

## Manutenção

### Backup

- Backup automático do banco
- Backup de logs
- Backup de configurações

### Updates

- Zero-downtime deployment
- Database migrations
- Rollback strategy

### Troubleshooting

- Logs detalhados
- Health check endpoints
- Debug mode para desenvolvimento

## Roadmap

### v1.1

- [ ] Autenticação e autorização
- [ ] Dashboard web
- [ ] Relatórios avançados

### v1.2

- [ ] Multi-tenant
- [ ] API rate limiting
- [ ] Cache Redis

### v2.0

- [ ] Machine learning para interpretação
- [ ] Chatbot inteligente
- [ ] Integração com sistemas hospitalares
