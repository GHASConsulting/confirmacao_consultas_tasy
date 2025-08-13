# Configuração de Múltiplos Bancos de Dados

Este documento explica como configurar e usar diferentes tipos de banco de dados na aplicação.

## 🏥 Configuração do Hospital

A aplicação suporta a configuração do nome do hospital para identificação e logs:

```env
# Nome do hospital (opcional)
HOSPITAL_NAME=Hospital Santa Casa
```

**Benefícios:**

- Identificação clara em logs e relatórios
- Personalização de mensagens
- Suporte futuro para multi-tenancy
- Integração com sistemas hospitalares específicos

## 🗄️ Bancos de Dados Suportados

### Oracle Database

```env
# Oracle Database (usado quando DATABASE_TYPE=oracle)
ORACLE_URL=oracle+cx_oracle://username:password@host:port/service_name

# Exemplo:
ORACLE_URL=oracle+cx_oracle://hospital:password123@localhost:1521/XE
```

**Dependências necessárias:**

- `cx-oracle==8.3.0` (já incluído no requirements.txt)

#### PostgreSQL Database

```env
# PostgreSQL Database (usado quando DATABASE_TYPE=postgresql)
POSTGRESQL_URL=postgresql://username:password@host:port/database_name

# Exemplo:
POSTGRESQL_URL=postgresql://hospital:password123@localhost:5432/hospital_db
```

**Dependências necessárias:**

- `psycopg2-binary==2.9.9` (já incluído no requirements.txt)

#### Firebase Database

```env
# Firebase Configuration (usado quando DATABASE_TYPE=firebase)
FIREBASE_PROJECT_ID=your-firebase-project-id
FIREBASE_CREDENTIALS_PATH=path/to/firebase-credentials.json
FIREBASE_DATABASE_URL=https://your-project-id.firebaseio.com

# Exemplo:
FIREBASE_PROJECT_ID=hospital-app
FIREBASE_CREDENTIALS_PATH=./firebase-credentials.json
FIREBASE_DATABASE_URL=https://hospital-app.firebaseio.com
```

**Dependências necessárias:**

- `firebase-admin==6.2.0` (já incluído no requirements.txt)
- `google-cloud-firestore==2.13.1` (já incluído no requirements.txt)

## 🚀 Como Usar

### 1. Configuração Inicial

1. **Clone o repositório:**

```bash
git clone <repository-url>
cd confirmacao_consultas
```

2. **Instale as dependências:**

```bash
pip install -r requirements.txt
```

3. **Configure o arquivo .env:**

```bash
cp env.example .env
# Edite o arquivo .env com suas configurações
```

### 2. Exemplos de Configuração

#### Exemplo 1: Oracle

```env
DATABASE_TYPE=oracle
ORACLE_URL=oracle+cx_oracle://hospital:password123@localhost:1521/XE
```

#### Exemplo 2: PostgreSQL

```env
DATABASE_TYPE=postgresql
POSTGRESQL_URL=postgresql://hospital:password123@localhost:5432/hospital_db
```

#### Exemplo 3: Firebase

```env
DATABASE_TYPE=firebase
FIREBASE_PROJECT_ID=hospital-app
FIREBASE_CREDENTIALS_PATH=./firebase-credentials.json
FIREBASE_DATABASE_URL=https://hospital-app.firebaseio.com
```

### 3. Execução

```bash
# Inicia a aplicação
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```
