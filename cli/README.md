# CLI - Sistema de Confirmação de Consultas

Interface de linha de comando para gerenciar e testar o sistema de confirmação de consultas.

## 📋 Comandos Disponíveis

### 🆕 Novos Comandos (Implementados e Testados)

#### `criar-atendimento`

Cria um novo atendimento no banco de dados.

**Uso:**

```bash
python -m cli criar-atendimento --nome "João Silva" --telefone 5531999629004 --medico "Dr. Carlos" --especialidade "Cardiologia" --data "15/01/2025" --hora "14:00"
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

Mostra o status atual do sistema.

#### `test-db`

Testa a conexão com o banco de dados configurado.

#### `conexao`

Testa a conexão com a API do Botconversa.

### 📊 Comandos de Atendimentos

#### `atendimentos`

Lista todos os atendimentos pendentes.

#### `buscar`

Busca atendimento por telefone.

**Uso:**

```bash
python -m cli buscar --telefone 5531999629004
```

#### `mensagem`

Envia mensagem para um paciente.

**Uso:**

```bash
python -m cli mensagem --telefone 5531999629004
```

#### `workflow`

Executa o workflow completo para um atendimento.

**Uso:**

```bash
python -m cli workflow --id 1
```

#### `resposta`

Processa a resposta de um paciente.

**Uso:**

```bash
python -m cli resposta --telefone 5531999629004 --resposta 1
```

## 🎯 Exemplos de Uso Completos

### Fluxo Completo de Criação e Integração

1. **Criar novo atendimento:**

```bash
python -m cli criar-atendimento --nome "João Silva" --telefone 5531999629004 --medico "Dr. Carlos" --especialidade "Cardiologia" --data "15/01/2025" --hora "14:00"
```

2. **Adicionar paciente ao Botconversa:**

```bash
python -m cli adicionar-botconversa --telefone 5531999629004
```

3. **Adicionar paciente à campanha:**

```bash
python -m cli adicionar-campanha --telefone 5531999629004
```

### Verificação de Dados

- **Listar atendimentos:**

```bash
python -m cli atendimentos
```

- **Buscar atendimento específico:**

```bash
python -m cli buscar --telefone 5531999629004
```

## ✅ Status de Implementação

Todos os comandos foram **implementados e testados com sucesso**:

- ✅ `criar-atendimento` - Funcionando perfeitamente
- ✅ `adicionar-botconversa` - Integração com API funcionando
- ✅ `adicionar-campanha` - Adição automática à campanha padrão
- ✅ Banco de dados integrado (PostgreSQL + Schema SantaCasa)
- ✅ Conexão com Botconversa API funcionando
- ✅ Tratamento de erros e validações implementadas

## 🔧 Requisitos Técnicos

- Python 3.11+
- Dependências: `click`, `rich`, `sqlalchemy`, `psycopg2-binary`
- Banco PostgreSQL configurado
- API Key do Botconversa configurada no `.env`

## 📝 Notas Importantes

- **Telefone**: Sempre use o formato `5531999629004` (código do país + DDD + número)
- **Data**: Use o formato `DD/MM/AAAA`
- **Hora**: Use o formato `HH:MM` (24h)
- **Campanha**: Por padrão, usa "Confirmação de Consultas" (ID: 289860)
- **Schema**: Todas as tabelas estão no schema `SantaCasa`

## 🚀 Próximos Passos

O sistema CLI está completamente funcional para:

1. ✅ Criação de atendimentos
2. ✅ Integração com Botconversa
3. ✅ Gerenciamento de campanhas
4. ✅ Consultas e listagens

Próximas funcionalidades planejadas:

- Envio de mensagens personalizadas
- Execução de workflows automatizados
- Processamento de respostas dos pacientes
