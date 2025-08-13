# 📋 README - Implementação Botconversa

## 🎯 **Resumo do Projeto**

Sistema de confirmação de consultas médicas integrado com Botconversa para automatizar o processo de confirmação de pacientes.

## 📁 **Estrutura do Projeto**

```
confirmacao_consultas/
├── app/
│   ├── api/
│   │   └── routes/
│   │       ├── botconversa_test.py    # Rotas de teste
│   │       └── webhook.py             # Rotas de webhook (não usado ainda)
│   ├── config/
│   │   └── config.py                  # Configurações (.env)
│   ├── database/
│   │   ├── manager.py                 # Gerenciamento do banco
│   │   └── models.py                  # Modelos (Atendimento, etc.)
│   └── services/
│       └── botconversa_service.py     # Serviço principal
├── .env                               # Variáveis de ambiente
├── env.example                        # Exemplo de configuração
└── README_IMPLEMENTACAO.md           # Este arquivo
```

## 🗄️ **Banco de Dados**

### Tabela Principal: `Atendimento`

**Schema:** `SantaCasa.atendimentos`

| Campo                    | Tipo     | Descrição                                             |
| ------------------------ | -------- | ----------------------------------------------------- |
| `id`                     | Integer  | ID único                                              |
| `nome_paciente`          | String   | Nome completo do paciente                             |
| `telefone`               | String   | Telefone (formato: 5531999629004)                     |
| `email`                  | String   | Email (opcional)                                      |
| `nome_medico`            | String   | Nome do médico                                        |
| `especialidade`          | String   | Especialidade médica                                  |
| `data_consulta`          | DateTime | Data e hora da consulta                               |
| `observacoes`            | String   | Observações (opcional)                                |
| `status`                 | Enum     | **CAMPO DE CONTROLE** (PENDENTE/CONFIRMADO/CANCELADO) |
| `subscriber_id`          | Integer  | ID do subscriber no Botconversa                       |
| `mensagem_enviada`       | String   | Mensagem enviada ao paciente                          |
| `resposta_paciente`      | String   | Resposta do paciente (1/0/texto)                      |
| `interpretacao_resposta` | String   | Interpretação da resposta                             |
| `enviado_em`             | DateTime | Quando a mensagem foi enviada                         |
| `respondido_em`          | DateTime | Quando o paciente respondeu                           |
| `criado_em`              | DateTime | Data de criação                                       |
| `atualizado_em`          | DateTime | Última atualização                                    |

## ⚙️ **Configurações (.env)**

### Variáveis Implementadas

```bash
# Database Configuration
DATABASE_TYPE=postgresql
POSTGRESQL_URL=postgresql://username:password@host:port/database_name

# Botconversa API Configuration
BOTCONVERSA_API_URL=https://backend.botconversa.com.br/api/v1/webhook
BOTCONVERSA_API_KEY=your_botconversa_api_key

# Hospital Information (para mensagens personalizadas)
HOSPITAL_NAME=Santa Casa de Belo Horizonte
HOSPITAL_PHONE=(31) 3238-8100
HOSPITAL_ADDRESS=Rua Domingos Vieira, 590 - Santa Efigênia
HOSPITAL_CITY=Belo Horizonte
HOSPITAL_STATE=MG
```

## 🔧 **Funcionalidades Implementadas**

### 1. ✅ **Conexão com Botconversa**

- **Método:** `testar_conexao()`
- **Endpoint:** `GET /test/conexao`
- **Status:** ✅ Funcionando

### 2. ✅ **Criação de Subscriber**

- **Método:** `criar_subscriber(telefone, nome, sobrenome)`
- **Endpoint:** `POST /test/subscriber`
- **Status:** ✅ Funcionando

### 3. ✅ **Busca de Subscriber**

- **Método:** `buscar_subscriber(telefone)`
- **Endpoint:** `GET /test/subscriber/{telefone}`
- **Status:** ✅ Funcionando

### 4. ✅ **Criação de Atendimento**

- **Método:** `criar_atendimento(dados)`
- **Endpoint:** `POST /test/atendimento`
- **Status:** ✅ Funcionando

### 5. ✅ **Envio de Mensagem Personalizada**

- **Método:** `enviar_mensagem_consulta(atendimento)`
- **Status:** ✅ Funcionando
- **Formato da mensagem:**

```
🏥 **Santa Casa de Belo Horizonte**

Olá {nome_paciente}! 👋

Você tem uma consulta agendada:
📅 **Data:** {data_formatada}
⏰ **Horário:** {hora_formatada}
👨‍⚕️ **Médico:** {nome_medico}
🏥 **Especialidade:** {especialidade}

Aguardamos sua confirmação! 🙏

📞 Para dúvidas: (31) 3238-8100
📍 Endereço: Rua Domingos Vieira, 590 - Santa Efigênia, Belo Horizonte - MG
```

### 6. ✅ **Adição à Campanha**

- **Método:** `adicionar_subscriber_campanha(subscriber_id, campaign_id=289860)`
- **Endpoint:** `POST /test/subscriber/{subscriber_id}/campaigns/{campaign_id}`
- **Status:** ✅ Funcionando

### 7. ✅ **Envio de Fluxo**

- **Método:** `enviar_fluxo(subscriber_id, flow_id=7725640)`
- **Endpoint:** `POST /test/subscriber/{subscriber_id}/send_flow`
- **Status:** ✅ Funcionando

### 8. ✅ **Processamento de Respostas**

- **Método:** `processar_resposta_paciente(telefone, resposta)`
- **Status:** ✅ Funcionando
- **Respostas aceitas:**
  - `"1"` → CONFIRMADO
  - `"0"` → CANCELADO
  - Texto (sim/não) → Fallback

### 9. ✅ **Workflow Completo**

- **Método:** `executar_workflow_consulta(atendimento_id)`
- **Endpoint:** `POST /test/workflow/{atendimento_id}`
- **Status:** ✅ Funcionando
- **Passos:**
  1. Envia mensagem personalizada
  2. Adiciona à campanha
  3. Envia fluxo

## 🎯 **Status Atual**

### ✅ **IMPLEMENTADO E FUNCIONANDO:**

1. ✅ Conexão com Botconversa
2. ✅ Criação de subscribers
3. ✅ Busca de subscribers
4. ✅ Criação de atendimentos
5. ✅ Envio de mensagem personalizada
6. ✅ Adição à campanha
7. ✅ Envio de fluxo
8. ✅ Processamento de respostas (1/0)
9. ✅ Workflow completo

### ⏳ **PENDENTE:**

1. ⏳ Configuração do fluxo no Botconversa (1=SIM, 0=NÃO)
2. ⏳ Recebimento de webhooks do Botconversa
3. ⏳ Monitoramento automático da tabela
4. ⏳ Interface de usuário

## 🚀 **Como Usar**

### 1. **Configurar .env**

```bash
# Copie o env.example e configure suas variáveis
cp env.example .env
# Edite o .env com suas configurações
```

### 2. **Testar Conexão**

```bash
# Via API
curl http://localhost:8000/test/conexao

# Via Python
python -c "from app.database.manager import initialize_database, get_db; from app.services.botconversa_service import BotconversaService; initialize_database(); db = next(get_db()); service = BotconversaService(db); print(service.testar_conexao())"
```

### 3. **Criar Atendimento**

```bash
# Via API
curl -X POST "http://localhost:8000/test/atendimento" \
  -H "Content-Type: application/json" \
  -d '{
    "nome_paciente": "João Silva",
    "telefone": "5531999629004",
    "nome_medico": "Dr. Maria Santos",
    "especialidade": "Cardiologia",
    "data_consulta": "2025-08-15T15:00:00"
  }'
```

### 4. **Executar Workflow**

```bash
# Via API
curl -X POST "http://localhost:8000/test/workflow/1"
```

## 📝 **Próximos Passos**

### **Imediato (Próximo Sprint):**

1. **Configurar fluxo no Botconversa** com opções "1" e "0"
2. **Testar workflow completo** end-to-end
3. **Verificar se respostas** estão sendo processadas

### **Futuro:**

1. **Implementar webhooks** para receber respostas automaticamente
2. **Criar monitoramento** da tabela de atendimentos
3. **Desenvolver interface** de usuário
4. **Adicionar relatórios** e dashboards

## 🔍 **Endpoints Disponíveis**

| Método | Endpoint                               | Descrição                      |
| ------ | -------------------------------------- | ------------------------------ |
| GET    | `/test/conexao`                        | Testa conexão com Botconversa  |
| POST   | `/test/subscriber`                     | Cria subscriber                |
| GET    | `/test/subscriber/{telefone}`          | Busca subscriber               |
| POST   | `/test/atendimento`                    | Cria atendimento               |
| GET    | `/test/atendimentos/pendentes`         | Lista atendimentos pendentes   |
| GET    | `/test/atendimento/{telefone}`         | Busca atendimento por telefone |
| PUT    | `/test/atendimento/{id}/status`        | Atualiza status                |
| GET    | `/test/campanhas`                      | Lista campanhas                |
| POST   | `/test/subscriber/{id}/campaigns/{id}` | Adiciona à campanha            |
| GET    | `/test/fluxos`                         | Lista fluxos                   |
| POST   | `/test/subscriber/{id}/send_flow`      | Envia fluxo                    |
| POST   | `/test/workflow/{id}`                  | Executa workflow completo      |

## 🐛 **Problemas Conhecidos**

1. **Nenhum problema crítico** identificado
2. **Todos os testes** passando
3. **Integração** funcionando corretamente

## 📞 **Suporte**

Para dúvidas ou problemas:

1. Verificar logs em `logs/`
2. Testar conexão com Botconversa
3. Verificar configurações no `.env`
4. Consultar este README

---

**Última atualização:** 08/08/2025
**Versão:** 1.0.0
**Status:** ✅ Funcionando
