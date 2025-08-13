# Guia do Webhook e N8N

Este documento explica como configurar e usar o sistema de webhook integrado com N8N para processar respostas dos pacientes.

## 🌐 Visão Geral

O sistema possui um webhook inteligente que:

- **Recebe dados** do N8N via POST
- **Detecta automaticamente** o tipo de dados
- **Processa respostas** dos pacientes
- **Atualiza o banco** de dados automaticamente

## 🛣️ Endpoint

```
POST /webhook/botconversa
```

**URL completa:** `https://meuservidor.com/webhook/botconversa`

## 📋 Estrutura dos Dados

### Dados do N8N (Recomendado)

```json
{
  "telefone": "5511999999999",
  "subscriber_id": 123456,
  "resposta": "1",
  "nome_paciente": "João Silva",
  "mensagem_original": "1"
}
```

### Campos Obrigatórios

- **`telefone`**: Telefone do paciente (string)
- **`subscriber_id`**: ID do subscriber no Botconversa (integer)
- **`resposta`**: Resposta do paciente (string)

### Campos Opcionais

- **`nome_paciente`**: Nome do paciente (string)
- **`mensagem_original`**: Mensagem original recebida (string)

## 🎯 Respostas Aceitas

### Confirmação

```json
{
  "resposta": "1"
}
```

- **Status:** `CONFIRMADO`
- **Ação:** Paciente confirma presença na consulta

### Cancelamento

```json
{
  "resposta": "0"
}
```

- **Status:** `CANCELADO`
- **Ação:** Paciente cancela a consulta

## 🔄 Fluxo de Processamento

1. **N8N recebe** resposta do paciente via Botconversa
2. **N8N processa** e envia POST para nosso webhook
3. **Sistema detecta** automaticamente dados do N8N
4. **Busca atendimento** por `subscriber_id`
5. **Atualiza status** no banco de dados
6. **Retorna confirmação** para o N8N

## ⚙️ Configuração

### 1. Configurações no .env

```bash
# Webhook Configuration
WEBHOOK_HOST=0.0.0.0
WEBHOOK_PORT=8000
WEBHOOK_URL=https://meuservidor.com/webhook/botconversa
```

### 2. Configuração do N8N

No N8N, configure o webhook para:

- **Método:** POST
- **URL:** `https://meuservidor.com/webhook/botconversa`
- **Headers:** `Content-Type: application/json`
- **Body:** Dados estruturados conforme especificação

## 🧪 Testes

### Teste Local

```bash
# Simular dados do N8N
curl -X POST http://localhost:8000/webhook/botconversa \
  -H "Content-Type: application/json" \
  -d '{
    "telefone": "5511999999999",
    "subscriber_id": 123456,
    "resposta": "1",
    "nome_paciente": "Teste"
  }'
```

### Teste de Produção

```bash
# Testar endpoint público
curl -X POST https://meuservidor.com/webhook/botconversa \
  -H "Content-Type: application/json" \
  -d '{
    "telefone": "5511999999999",
    "subscriber_id": 123456,
    "resposta": "1"
  }'
```

## 📊 Respostas da API

### Sucesso

```json
{
  "success": true,
  "message": "Atendimento CONFIRMADO com sucesso",
  "data": {
    "atendimento_id": 123,
    "status": "CONFIRMADO",
    "telefone": "5511999999999",
    "subscriber_id": 123456,
    "resposta": "1"
  }
}
```

### Erro

```json
{
  "success": false,
  "detail": "Erro ao processar webhook: Atendimento não encontrado para subscriber_id: 123456"
}
```

## 🔍 Monitoramento

### Health Check

```bash
GET /webhook/botconversa/health
```

### Logs

Todos os processamentos são logados em `logs/app.log` com:

- Dados recebidos
- Processamento realizado
- Resultado da operação
- Erros (se houver)

## 🚨 Tratamento de Erros

### Erros Comuns

1. **Atendimento não encontrado**

   - Verificar se `subscriber_id` existe no banco
   - Confirmar se atendimento está ativo

2. **Resposta inválida**

   - Apenas "1" e "0" são aceitos
   - Verificar formato da mensagem

3. **Dados incompletos**
   - Verificar campos obrigatórios
   - Validar formato dos dados

### Rollback Automático

Em caso de erro, o sistema:

- Faz rollback da transação
- Loga o erro detalhadamente
- Retorna mensagem de erro apropriada

## 🔐 Segurança

### Validações

- **Campos obrigatórios** verificados
- **Formato de dados** validado
- **SQL Injection** prevenido via SQLAlchemy
- **Rate limiting** configurável

### Logs de Auditoria

- **Todas as requisições** são logadas
- **Dados processados** registrados
- **Erros** documentados com contexto
- **Timestamps** precisos para auditoria

## 📚 Referências

- [Guia de Desenvolvimento](development_guide.md)
- [Configuração do Sistema](README.md)
- [API Endpoints](TECHNICAL.md)
