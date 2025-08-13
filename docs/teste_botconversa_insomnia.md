# Teste das Rotas do Botconversa no Insomnia

## 📋 Pré-requisitos

- **Insomnia** instalado
- **Credenciais do Botconversa** configuradas
- **Número de telefone** para teste

## 🔧 Configuração Base

### **URL Base**

```
https://backend.botconversa.com.br/api/v1/webhook
```

### **Headers Necessários**

```
Authorization: Bearer {SUA_API_KEY}
Content-Type: application/json
```

## 👥 1. Rotas do Subscriber (Gerenciamento de Contatos)

### **1.1 Listar Subscribers**

```
GET /api/v1/webhook/subscriber/
```

### **1.2 Criar Subscriber**

```
POST /api/v1/webhook/subscriber/
```

### **1.3 Buscar Subscriber por ID**

```
GET /api/v1/webhook/subscriber/{subscriber_id}/
```

### **1.4 Atualizar Subscriber**

```
PUT /api/v1/webhook/subscriber/{subscriber_id}/
```

### **1.5 Deletar Subscriber**

```
DELETE /api/v1/webhook/subscriber/{subscriber_id}/
```

## 📊 2. Rotas do Manager (Gerenciamento de Mensagens)

### **2.1 Listar Managers**

```
GET /api/v1/webhook/manager/
```

### **2.2 Criar Manager**

```
POST /api/v1/webhook/manager/
```

### **2.3 Buscar Manager por ID**

```
GET /api/v1/webhook/manager/{manager_id}/
```

### **2.4 Atualizar Manager**

```
PUT /api/v1/webhook/manager/{manager_id}/
```

### **2.5 Deletar Manager**

```
DELETE /api/v1/webhook/manager/{manager_id}/
```

## 🎯 4. Exemplos de Uso

### **4.1 Criar Subscriber (Paciente)**

```
POST https://backend.botconversa.com.br/api/v1/webhook/subscriber/
```

**Headers:**

```
Authorization: Bearer {SUA_API_KEY}
Content-Type: application/json
```

**Body (JSON):**

```json
{
  "phone": "5531999629004",
  "first_name": "Iury",
  "last_name": "Costa"
}
```

**Resposta Esperada:**

```json
{
  "id": 786889127,
  "full_name": "Iury Costa",
  "first_name": "Iury",
  "last_name": "Costa",
  "phone": "+553199629004",
  "ddd": "31",
  "created_at": "2025-08-06T19:39:10.685447Z",
  "live_chat": "live-chat/all/+553199629004",
  "referrer": null,
  "referral_count": 0,
  "campaigns": [],
  "tags": [],
  "variables": {
    "Caminho_Atendimento": null,
    "DataMomento": null,
    "ResumoAtendimento IA": null,
    "Resumo_SAC_SCBH": null,
    "atendimentoSCBH": null,
    "autenticacaoscbh": null,
    "centrocustoSCBH": null,
    "chatgpt_entrada": null,
    "chatgpt_resposta": null,
    "chatgpt_thread": null,
    "dataSCBH": null,
    "descricaoChamadoDRG": null,
    "descricaoatendimento": null,
    "diagnosticoSCBH": null,
    "historico_ava": null,
    "lDRG": null,
    "leitoSCBH": null,
    "matriculaSantaCasa": null,
    "messagevalida": null,
    "nomeCompleto": null,
    "nomeSCBH": null,
    "nomeSistemaX": null,
    "notaatendimento": null,
    "numeroChamado": null,
    "numeroChamadoDRGC": null,
    "palavraChaveReset": null,
    "pergunta10SCBH": null,
    "pergunta11SCBH": null,
    "pergunta13SCBH": null,
    "pergunta16SCBH": null,
    "pergunta17SCBH": null,
    "pergunta18SCBH": null,
    "pergunta19SCBH": null,
    "pergunta1SCBH": null,
    "pergunta20SCBH": null,
    "pergunta2SCBH": null,
    "pergunta3SCBH": null,
    "pergunta4SCBH": null,
    "pergunta5SCBH": null,
    "pergunta6SCBH": null,
    "pergunta7SCBH": null,
    "pergunta8SCBH": null,
    "pergunta9SCBH": null,
    "pergunta_1": null,
    "pergunta_2": null,
    "perguntaavav3": null,
    "qnt_verificacao": null,
    "ramal": null,
    "ramalSCBH": null,
    "ramalXSCBH": null,
    "retornocpf": null,
    "retornocpfv": null,
    "retornodtnasc": null,
    "retornomatricula": null,
    "retornosenha": null,
    "statusalteracao": null,
    "tentativa_cpf": null,
    "validamatricula": null,
    "validamatriculaini": null,
    "validamatrisenha": null
  },
  "sequences": [],
  "created": true
}
```

### **4.2 Enviar Mensagem via Subscriber**

```
POST https://backend.botconversa.com.br/api/v1/webhook/subscriber/{subscriber_id}/send_message/
```

**Headers:**

```
Authorization: Bearer {SUA_API_KEY}
Content-Type: application/json
```

**Body (JSON):**

```json
{
  "type": "text",
  "value": "Olá Iury! Você tem consulta agendada para amanhã às 14h. Confirma presença? Responda SIM ou NÃO."
}
```

**Resposta Esperada:**

```json
{
  "success": true,
  "message_id": "abc123",
  "status": "sent"
}
```

**Exemplo com subscriber_id real:**

```
POST https://backend.botconversa.com.br/api/v1/webhook/subscriber/786889127/send_message/
```

**Body (JSON):**

```json
{
  "type": "text",
  "value": "Teste confimação de consultas segundo teste"
}
```

### **4.3 Listar Subscribers**

```
GET https://backend.botconversa.com.br/api/v1/webhook/subscriber/
```

**Headers:**

```
Authorization: Bearer {SUA_API_KEY}
```

**Resposta Esperada:**

```json
{
  "subscribers": [
    {
      "id": 786889127,
      "full_name": "Iury Costa",
      "first_name": "Iury",
      "last_name": "Costa",
      "phone": "+553199629004",
      "ddd": "31",
      "created_at": "2025-08-06T19:39:10.685447Z",
      "live_chat": "live-chat/all/+553199629004",
      "referrer": null,
      "referral_count": 0,
      "campaigns": [],
      "tags": [],
      "variables": {
        "Caminho_Atendimento": null,
        "DataMomento": null,
        "ResumoAtendimento IA": null,
        "Resumo_SAC_SCBH": null,
        "atendimentoSCBH": null,
        "autenticacaoscbh": null,
        "centrocustoSCBH": null,
        "chatgpt_entrada": null,
        "chatgpt_resposta": null,
        "chatgpt_thread": null,
        "dataSCBH": null,
        "descricaoChamadoDRG": null,
        "descricaoatendimento": null,
        "diagnosticoSCBH": null,
        "historico_ava": null,
        "lDRG": null,
        "leitoSCBH": null,
        "matriculaSantaCasa": null,
        "messagevalida": null,
        "nomeCompleto": null,
        "nomeSCBH": null,
        "nomeSistemaX": null,
        "notaatendimento": null,
        "numeroChamado": null,
        "numeroChamadoDRGC": null,
        "palavraChaveReset": null,
        "pergunta10SCBH": null,
        "pergunta11SCBH": null,
        "pergunta13SCBH": null,
        "pergunta16SCBH": null,
        "pergunta17SCBH": null,
        "pergunta18SCBH": null,
        "pergunta19SCBH": null,
        "pergunta1SCBH": null,
        "pergunta20SCBH": null,
        "pergunta2SCBH": null,
        "pergunta3SCBH": null,
        "pergunta4SCBH": null,
        "pergunta5SCBH": null,
        "pergunta6SCBH": null,
        "pergunta7SCBH": null,
        "pergunta8SCBH": null,
        "pergunta9SCBH": null,
        "pergunta_1": null,
        "pergunta_2": null,
        "perguntaavav3": null,
        "qnt_verificacao": null,
        "ramal": null,
        "ramalSCBH": null,
        "ramalXSCBH": null,
        "retornocpf": null,
        "retornocpfv": null,
        "retornodtnasc": null,
        "retornomatricula": null,
        "retornosenha": null,
        "statusalteracao": null,
        "tentativa_cpf": null,
        "validamatricula": null,
        "validamatriculaini": null,
        "validamatrisenha": null
      },
      "sequences": []
    }
  ]
}
```

## 📥 3. Webhook para Receber Respostas dos Pacientes

### **3.1 Configurar Webhook**

Para receber as respostas dos pacientes, você precisa configurar um **webhook** no Botconversa.

### **3.2 URL do Webhook**

```
POST https://sua-aplicacao.com/api/v1/webhook/botconversa
```

### **3.3 Exemplo de Payload Recebido**

Quando um paciente responde, você receberá um payload como este:

```json
{
  "type": "message",
  "contact": {
    "id": 786889127,
    "full_name": "Iury Costa",
    "first_name": "Iury",
    "last_name": "Costa",
    "phone": "+553199629004",
    "ddd": "31"
  },
  "message": {
    "id": "msg123",
    "type": "text",
    "content": "SIM",
    "timestamp": "2025-08-06T19:39:10.685447Z"
  }
}
```

### **3.4 Estrutura do Payload**

**Campos principais:**

- **`type`**: Tipo do evento ("message", "status", etc.)
- **`contact`**: Dados do contato que enviou a mensagem
  - **`id`**: ID do subscriber
  - **`full_name`**: Nome completo
  - **`phone`**: Número do telefone
- **`message`**: Dados da mensagem
  - **`id`**: ID da mensagem
  - **`type`**: Tipo da mensagem ("text", "image", etc.)
  - **`content`**: Conteúdo da mensagem
  - **`timestamp`**: Data/hora da mensagem

### **3.5 Configuração no Botconversa**

1. **Acesse o painel do Botconversa**
2. **Vá em Configurações > Webhooks**
3. **Configure a URL do webhook**: `https://sua-aplicacao.com/api/v1/webhook/botconversa`
4. **Adicione a chave secreta** (opcional, para segurança)

### **3.6 Implementação na Aplicação**

**Endpoint para receber webhooks:**

```python
@router.post("/webhook/botconversa")
async def botconversa_webhook(webhook: BotconversaWebhook, db: Session = Depends(get_db)):
    """Recebe mensagens do Botconversa"""

    # Extrai dados da mensagem
    contact_id = webhook.contact.get("id")
    phone = webhook.contact.get("phone")
    message_content = webhook.message.get("content") if webhook.message else ""

    # Processa a resposta do paciente
    appointment_service = AppointmentService(db)
    success = await appointment_service.process_patient_response(phone, message_content)

    return {"success": success}
```

### **3.7 Teste do Webhook**

Para testar o webhook localmente, use **ngrok**:

1. **Instale o ngrok**: `npm install -g ngrok`
2. **Exponha sua aplicação**: `ngrok http 8000`
3. **Use a URL do ngrok** no painel do Botconversa
4. **Teste enviando uma mensagem** para o subscriber

**Exemplo de URL do ngrok:**

```
https://abc123.ngrok.io/api/v1/webhook/botconversa
```

## 🔍 5. Passo a Passo no Insomnia

### **5.1 Criar Nova Collection**

- Abra o Insomnia
- Clique em "New Collection"
- Nome: "Botconversa API"

### **5.2 Configurar Environment**

- Clique em "Manage Environments"
- Crie um novo environment chamado "Botconversa"
- Adicione as variáveis:
  ```
  API_KEY: sua_api_key_aqui
  PHONE: seu_numero_aqui
  BASE_URL: https://backend.botconversa.com.br/api/v1/webhook
  ```

### **5.3 Criar Requests**

- **List Subscribers**: `GET {{BASE_URL}}/subscriber/`
- **Create Subscriber**: `POST {{BASE_URL}}/subscriber/`
- **Get Subscriber**: `GET {{BASE_URL}}/subscriber/{id}/`
- **Update Subscriber**: `PUT {{BASE_URL}}/subscriber/{id}/`
- **Delete Subscriber**: `DELETE {{BASE_URL}}/subscriber/{id}/`
- **Send Message**: `POST {{BASE_URL}}/subscriber/{id}/send_message/`
- **List Managers**: `GET {{BASE_URL}}/manager/`
- **Create Manager**: `POST {{BASE_URL}}/manager/`

### **5.4 Configurar Headers Globais**

- Em cada request, adicione:
  ```
  Authorization: Bearer {{API_KEY}}
  Content-Type: application/json
  ```

## 🧪 6. Sequência de Testes Recomendada

### **Teste 1: Criar Subscriber**

1. Execute `POST /subscriber/` com seus dados
2. Verifique se retorna sucesso e anote o `id`

### **Teste 2: Listar Subscribers**

1. Execute `GET /subscriber/`
2. Verifique se seu subscriber aparece na lista

### **Teste 3: Enviar Mensagem**

1. Execute `POST /subscriber/{id}/send_message/` com o `subscriber_id`
2. Verifique se a mensagem chega no WhatsApp

### **Teste 4: Buscar Subscriber**

1. Execute `GET /subscriber/{id}/` com o ID retornado
2. Verifique se os dados estão corretos

## ⚠️ 7. Observações Importantes

### **Formato do Telefone**

- Use o formato: `5531999629004` (código do país + DDD + número)
- Sem espaços, hífens ou parênteses
- A API retorna o telefone com `+` no início: `+553199629004`
- O DDD é extraído automaticamente: `31`

### **Campos Obrigatórios para Subscriber**

- **`phone`**: Número do telefone (obrigatório)
- **`first_name`**: Primeiro nome (obrigatório)
- **`last_name`**: Sobrenome (obrigatório)

### **Campos Obrigatórios para Enviar Mensagem**

- **`type`**: Tipo da mensagem (ex: "text", "image", "file")
- **`value`**: Conteúdo da mensagem (texto, URL da imagem, etc.)

### **Tipos de Mensagem Suportados**

- **`text`**: Mensagem de texto simples
- **`image`**: Imagem (URL da imagem)
- **`file`**: Arquivo (URL do arquivo)
- **`audio`**: Áudio (URL do áudio)
- **`video`**: Vídeo (URL do vídeo)

### **Campos Opcionais**

- **`email`**: Email do subscriber (opcional)
- **`variables`**: Variáveis customizadas (opcional)

### **Rate Limiting**

- Limite: **600 RPM** (Requests Per Minute)
- Não envie muitas mensagens rapidamente

### **Webhook URL**

- Para receber webhooks reais, você precisa de uma URL pública
- Use ngrok ou similar para desenvolvimento local

## 🚨 8. Troubleshooting

### **Erro 401 (Unauthorized)**

- Verifique se a API_KEY está correta
- Confirme se o header Authorization está correto

### **Erro 400 (Bad Request)**

- Verifique o formato do JSON
- Confirme se todos os campos obrigatórios estão presentes

### **Erro 404 (Not Found)**

- Verifique se a URL está correta
- Confirme se o endpoint existe na documentação

### **Mensagem não chega**

- Verifique se o número está no formato correto
- Confirme se o subscriber existe no Botconversa
- Verifique os logs do Botconversa

## 📞 9. Suporte

- **Documentação**: https://backend.botconversa.com.br/swagger/
- **Suporte Botconversa**: [contato do suporte]
- **Logs**: Verifique o painel do Botconversa para logs detalhados
