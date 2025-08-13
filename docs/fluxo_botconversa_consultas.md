# Fluxo Botconversa - Sistema de Confirmação de Consultas

## 🎯 Visão Geral

Este documento descreve como configurar um fluxo completo no Botconversa para automatizar o processo de confirmação de consultas médicas.

## 📋 Pré-requisitos

- **Conta Botconversa** ativa
- **API Key** configurada
- **Webhook** configurado na aplicação
- **Número de WhatsApp** conectado

## 🔄 Fluxo Principal

### **1. Estrutura do Fluxo**

```
📞 Paciente recebe mensagem
    ↓
🤖 Botconversa processa resposta
    ↓
📥 Webhook envia para aplicação
    ↓
💾 Aplicação atualiza banco
    ↓
📊 Relatório de confirmações
```

## 🎨 Configuração no Botconversa

### **1.1 Criar Novo Bot**

1. **Acesse o painel do Botconversa**
2. **Clique em "Novo Bot"**
3. **Nome**: "Confirmação de Consultas"
4. **Descrição**: "Sistema automatizado para confirmação de consultas médicas"

### **1.2 Configurar Variáveis**

**Variáveis do Sistema:**

- `nome_paciente` - Nome do paciente
- `data_consulta` - Data da consulta
- `hora_consulta` - Horário da consulta
- `nome_medico` - Nome do médico
- `especialidade` - Especialidade médica
- `status_confirmacao` - Status da confirmação

### **1.3 Criar Mensagens**

#### **Mensagem 1: Boas-vindas**

```
Olá {{nome_paciente}}! 👋

Você tem uma consulta agendada:
📅 Data: {{data_consulta}}
⏰ Horário: {{hora_consulta}}
👨‍⚕️ Médico: {{nome_medico}}
🏥 Especialidade: {{especialidade}}

Por favor, confirme sua presença respondendo:
✅ SIM - Vou comparecer
❌ NÃO - Preciso cancelar
⏰ REAGENDAR - Quero reagendar

Aguardamos sua confirmação!
```

#### **Mensagem 2: Confirmação Recebida**

```
✅ Obrigado, {{nome_paciente}}!

Sua consulta foi **CONFIRMADA** para:
📅 {{data_consulta}} às {{hora_consulta}}
👨‍⚕️ Dr. {{nome_medico}}

📍 Local: [Endereço do hospital]
📞 Telefone: [Telefone para contato]

Lembre-se de:
• Chegar 15 minutos antes
• Trazer documentos
• Estar em jejum (se necessário)

Até lá! 👋
```

#### **Mensagem 3: Cancelamento**

```
❌ Entendemos, {{nome_paciente}}!

Sua consulta foi **CANCELADA** para:
📅 {{data_consulta}} às {{hora_consulta}}

Para reagendar, entre em contato:
📞 [Telefone para reagendamento]
🌐 [Website para agendamento online]

Obrigado por nos avisar! 👋
```

#### **Mensagem 4: Reagendamento**

```
⏰ {{nome_paciente}}, entendemos que você quer reagendar!

Para reagendar sua consulta, entre em contato:
📞 [Telefone para reagendamento]
🌐 [Website para agendamento online]

Ou responda com uma data preferida:
📅 Exemplo: "Quero reagendar para 15/08/2024 às 14h"

Aguardo seu contato! 👋
```

#### **Mensagem 5: Lembrete (48h antes)**

```
🔔 Lembrete importante, {{nome_paciente}}!

Sua consulta está marcada para **AMANHÃ**:
📅 {{data_consulta}} às {{hora_consulta}}
👨‍⚕️ Dr. {{nome_medico}}

Por favor, confirme sua presença:
✅ SIM - Vou comparecer
❌ NÃO - Preciso cancelar

Aguardamos sua confirmação! 🙏
```

#### **Mensagem 6: Lembrete (12h antes)**

```
⚠️ ÚLTIMO LEMBRETE, {{nome_paciente}}!

Sua consulta é **HOJE** às {{hora_consulta}}:
👨‍⚕️ Dr. {{nome_medico}}
🏥 [Endereço do hospital]

Confirme sua presença AGORA:
✅ SIM - Vou comparecer
❌ NÃO - Preciso cancelar

Não perca sua consulta! 🏥
```

## 🤖 Configuração de Automação

### **2.1 Gatilhos (Triggers)**

#### **Gatilho 1: Nova Consulta**

- **Tipo**: Webhook
- **URL**: `https://sua-aplicacao.com/api/v1/botconversa/nova-consulta`
- **Payload**:

```json
{
  "subscriber_id": "{{subscriber_id}}",
  "nome_paciente": "{{nome_paciente}}",
  "data_consulta": "{{data_consulta}}",
  "hora_consulta": "{{hora_consulta}}",
  "nome_medico": "{{nome_medico}}",
  "especialidade": "{{especialidade}}"
}
```

#### **Gatilho 2: Lembrete 48h**

- **Tipo**: Agendamento
- **Frequência**: 48h antes da consulta
- **Condição**: Status = "PENDENTE"

#### **Gatilho 3: Lembrete 12h**

- **Tipo**: Agendamento
- **Frequência**: 12h antes da consulta
- **Condição**: Status = "PENDENTE"

### **2.2 Ações (Actions)**

#### **Ação 1: Enviar Mensagem**

- **Tipo**: Enviar mensagem
- **Template**: Mensagem de confirmação
- **Variáveis**: Preenchidas automaticamente

#### **Ação 2: Atualizar Status**

- **Tipo**: Webhook
- **URL**: `https://sua-aplicacao.com/api/v1/botconversa/atualizar-status`
- **Método**: POST

#### **Ação 3: Registrar Resposta**

- **Tipo**: Salvar variável
- **Variável**: `status_confirmacao`
- **Valor**: Baseado na resposta

### **2.3 Condições (Conditions)**

#### **Condição 1: Resposta Positiva**

```
{{message}} contém "SIM" OU {{message}} contém "sim" OU {{message}} contém "Sim"
```

#### **Condição 2: Resposta Negativa**

```
{{message}} contém "NÃO" OU {{message}} contém "não" OU {{message}} contém "Não"
```

#### **Condição 3: Reagendamento**

```
{{message}} contém "REAGENDAR" OU {{message}} contém "reagendar"
```

## 🔄 Fluxo Detalhado

### **3.1 Fluxo de Confirmação**

```
1. 📞 Paciente recebe mensagem inicial
   ↓
2. 🤖 Paciente responde (SIM/NÃO/REAGENDAR)
   ↓
3. 📥 Botconversa processa resposta
   ↓
4. 🔄 Aplicação recebe via webhook
   ↓
5. 💾 Status atualizado no banco
   ↓
6. 📤 Mensagem de confirmação enviada
   ↓
7. 📊 Relatório gerado
```

### **3.2 Fluxo de Lembretes**

```
1. ⏰ 48h antes da consulta
   ↓
2. 📞 Lembrete enviado automaticamente
   ↓
3. 🤖 Se não responder em 24h
   ↓
4. ⏰ 12h antes da consulta
   ↓
5. 📞 Último lembrete enviado
   ↓
6. ❌ Se não responder, status = "SEM_RESPOSTA"
```

## 🎯 Configuração de Mensagens

### **4.1 Templates de Mensagem**

#### **Template Base**

```
🏥 [NOME_DO_HOSPITAL]

Olá {{nome_paciente}}!

[CONTEÚDO_ESPECÍFICO]

📞 Para dúvidas: [TELEFONE]
🌐 Website: [WEBSITE]
📍 Endereço: [ENDEREÇO]

Obrigado! 🙏
```

#### **Template de Confirmação**

```
✅ Confirmação Recebida!

Sua consulta foi **CONFIRMADA** para:
📅 {{data_consulta}} às {{hora_consulta}}
👨‍⚕️ Dr. {{nome_medico}}

📍 Local: [Endereço do hospital]
📞 Telefone: [Telefone para contato]

Lembre-se de:
• Chegar 15 minutos antes
• Trazer documentos
• Estar em jejum (se necessário)

Até lá! 👋
```

#### **Template de Cancelamento**

```
❌ Cancelamento Confirmado

Sua consulta foi **CANCELADA** para:
📅 {{data_consulta}} às {{hora_consulta}}

Para reagendar, entre em contato:
📞 [Telefone para reagendamento]
🌐 [Website para agendamento online]

Obrigado por nos avisar! 👋
```

## 🔧 Integração com a Aplicação

### **5.1 Endpoints Necessários**

#### **Endpoint 1: Nova Consulta**

```
POST /api/v1/botconversa/nova-consulta
```

**Payload:**

```json
{
  "subscriber_id": "123456",
  "nome_paciente": "João Silva",
  "data_consulta": "2024-08-15",
  "hora_consulta": "14:00",
  "nome_medico": "Dr. Maria Santos",
  "especialidade": "Cardiologia"
}
```

#### **Endpoint 2: Atualizar Status**

```
POST /api/v1/botconversa/atualizar-status
```

**Payload:**

```json
{
  "subscriber_id": "123456",
  "status": "CONFIRMADO",
  "resposta_paciente": "SIM",
  "timestamp": "2024-08-06T19:39:10.685447Z"
}
```

### **5.2 Processamento de Respostas**

#### **Interpretação de Respostas**

```python
def interpretar_resposta(mensagem: str) -> str:
    """Interpreta a resposta do paciente"""
    mensagem_lower = mensagem.lower()

    if any(palavra in mensagem_lower for palavra in ["sim", "confirmo", "vou", "comparecer"]):
        return "CONFIRMADO"
    elif any(palavra in mensagem_lower for palavra in ["não", "nao", "cancelo", "cancelar"]):
        return "CANCELADO"
    elif any(palavra in mensagem_lower for palavra in ["reagendar", "outra data", "mudar"]):
        return "REAGENDAR"
    else:
        return "INDEFINIDO"
```

## 📊 Relatórios e Analytics

### **6.1 Métricas Importantes**

- **Taxa de confirmação**: % de consultas confirmadas
- **Taxa de cancelamento**: % de consultas canceladas
- **Taxa de resposta**: % de pacientes que respondem
- **Tempo médio de resposta**: Tempo entre envio e resposta

### **6.2 Dashboard**

#### **Métricas Diárias**

- Consultas agendadas hoje
- Confirmações recebidas
- Cancelamentos
- Sem resposta

#### **Métricas Semanais**

- Taxa de confirmação semanal
- Consultas por especialidade
- Performance por médico

## 🚨 Troubleshooting

### **7.1 Problemas Comuns**

#### **Paciente não recebe mensagem**

- Verificar se o número está correto
- Confirmar se o subscriber existe
- Verificar logs do Botconversa

#### **Webhook não funciona**

- Verificar URL do webhook
- Confirmar se a aplicação está rodando
- Verificar logs da aplicação

#### **Resposta não processada**

- Verificar formato do payload
- Confirmar se o endpoint está correto
- Verificar logs de processamento

### **7.2 Logs Importantes**

#### **Logs do Botconversa**

- Mensagens enviadas
- Respostas recebidas
- Erros de envio

#### **Logs da Aplicação**

- Webhooks recebidos
- Processamento de respostas
- Atualizações no banco

## 📞 Suporte

### **8.1 Contatos**

- **Botconversa**: [Suporte Botconversa]
- **Desenvolvimento**: [Equipe de desenvolvimento]
- **Hospital**: [Contato do hospital]

### **8.2 Documentação**

- **API Botconversa**: https://backend.botconversa.com.br/swagger/
- **Documentação da aplicação**: [Link para docs]
- **Guia de troubleshooting**: [Link para guia]

## 🎯 Próximos Passos

1. **Configurar o bot no Botconversa**
2. **Criar os templates de mensagem**
3. **Configurar os gatilhos e ações**
4. **Testar o fluxo completo**
5. **Monitorar métricas**
6. **Ajustar conforme necessário**

---

**Versão**: 1.0  
**Última atualização**: 2024-08-06  
**Autor**: Equipe de Desenvolvimento
