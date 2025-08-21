# CLI - Sistema de Confirmação de Consultas

Interface de linha de comando para gerenciar e testar o sistema de confirmação de consultas.

## 📋 Comandos Disponíveis

### 🆕 Comandos Principais (Implementados e Testados)

#### `criar-atendimento`

Cria um novo atendimento no banco de dados.

**Uso:**

```bash
python -m cli criar-atendimento --nome "João Silva" --telefone 5531999629004 --medico "Dr. Carlos" --especialidade "Cardiologia" --data "15/01/2025" --hora "14:00" --nr-seq-agenda 12345
```

**Opções:**

- `--nome`: Nome completo do paciente (obrigatório)
- `--telefone`: Telefone no formato 5531999629004 (obrigatório)
- `--medico`: Nome do médico (obrigatório)
- `--especialidade`: Especialidade médica (obrigatório)
- `--data`: Data da consulta (DD/MM/AAAA) (obrigatório)
- `--hora`: Horário da consulta (HH:MM) (obrigatório)
- `--observacoes`: Observações adicionais (opcional)

**Exemplo de Saída:**

```
✅ Atendimento criado com sucesso!
📋 ID: 3
👤 Paciente: João Teste
📱 Telefone: 5531998888888
👨‍⚕️ Médico: Dr. José
🏥 Especialidade: Cardiologia
📅 Data: 20/01/2025 15:30
📊 Status: pendente
```

#### `adicionar-botconversa`

Adiciona um paciente no Botconversa (cria subscriber).

**Uso:**

```bash
python -m cli adicionar-botconversa --telefone 5531999629004
```

**Opções:**

- `--telefone`: Telefone do paciente no formato 5531999629004 (obrigatório)
- `--nome`: Nome do paciente (opcional, será buscado no banco)

**Exemplo de Saída:**

```
🔍 Encontrado atendimento: João Teste
📱 Telefone: 5531998888888
📡 Criando subscriber no Botconversa...
✅ Subscriber criado com sucesso no Botconversa!
🆔 Subscriber ID: 788094936
👤 Nome: João Teste
📱 Telefone: +553198888888
📊 Status: N/A
```

#### `adicionar-campanha`

Adiciona um paciente na campanha do Botconversa.

**Uso:**

```bash
python -m cli adicionar-campanha --telefone 5531999629004
```

**Opções:**

- `--telefone`: Telefone do paciente no formato 5531999629004 (obrigatório)
- `--campanha-id`: ID da campanha (padrão: Confirmação de Consultas)

**Exemplo de Saída:**

```
🔍 Encontrado atendimento: João Teste
🆔 Subscriber ID: 788094936
🔍 Buscando campanha 'Confirmação de Consultas'...
🎯 Campanha encontrada: Confirmação de Consultas (ID: 289860)
📡 Adicionando subscriber 788094936 à campanha 289860...
✅ Subscriber adicionado à campanha com sucesso!
👤 Paciente: João Teste
🆔 Subscriber ID: 788094936
🎯 Campanha ID: 289860
```

### 🔧 Comandos de Sistema

#### `status`

Mostra o status geral do sistema.

**Uso:**

```bash
python -m cli status
```

#### `test-db`

Testa a conexão com o banco de dados.

**Uso:**

```bash
python -m cli test-db
```

#### `test-conexao`

Testa a conexão com a API Botconversa.

**Uso:**

```bash
python -m cli test-conexao
```

### 📊 Comandos de Consulta

#### `atendimentos`

Lista todos os atendimentos cadastrados.

**Uso:**

```bash
python -m cli atendimentos
```

#### `listar-atendimentos`

Lista apenas os atendimentos pendentes de confirmação.

**Uso:**

```bash
python -m cli listar-atendimentos
```

#### `buscar-atendimento`

Busca um atendimento específico por telefone.

**Uso:**

```bash
python -m cli buscar-atendimento --telefone 5531999629004
```

### 🤖 Comandos Botconversa

#### `enviar-mensagem`

Envia uma mensagem personalizada para um paciente.

**Uso:**

```bash
python -m cli enviar-mensagem --telefone 5531999629004
```

#### `executar-workflow`

Executa o workflow completo de confirmação para um atendimento.

**Uso:**

```bash
python -m cli executar-workflow --id 1
```

#### `processar-resposta`

Processa a resposta de um paciente.

**Uso:**

```bash
python -m cli processar-resposta --telefone 5531999629004 --resposta 1
```

**Opções de resposta:**
- `1`: SIM (confirma consulta)
- `0`: NÃO (cancela consulta)

### 📚 Ajuda

#### `help`

Mostra ajuda detalhada sobre todos os comandos disponíveis.

**Uso:**

```bash
python -m cli help
```

## 🎯 Fluxo de Trabalho Recomendado

### **1. Criar Atendimento**
```bash
python -m cli criar-atendimento --nome "João Silva" --telefone 5531999629004 --medico "Dr. Carlos" --especialidade "Cardiologia" --data "15/01/2025" --hora "14:00" --nr-seq-agenda 12345
```

### **2. Adicionar no Botconversa**
```bash
python -m cli adicionar-botconversa --telefone 5531999629004
```

### **3. Executar Workflow**
```bash
python -m cli executar-workflow --id 1
```

### **4. Monitorar Respostas**
```bash
python -m cli processar-resposta --telefone 5531999629004 --resposta 1
```

## 💡 Dicas de Uso

- **Use `--help`** após qualquer comando para ver opções detalhadas
- **Telefone** deve estar no formato internacional: 5531999629004
- **Data** deve estar no formato: DD/MM/AAAA
- **Hora** deve estar no formato: HH:MM
- **Resposta** deve ser 1 (SIM) ou 0 (NÃO)

## 🔍 Troubleshooting

### **Comando não encontrado**
```bash
python -m cli help  # Ver todos os comandos disponíveis
```

### **Erro de conexão**
```bash
python -m cli test-db        # Testar banco
python -m cli test-conexao   # Testar Botconversa
```

### **Erro de parâmetros**
```bash
python -m cli [comando] --help  # Ver opções do comando
```
