# Guia de Desenvolvimento - Sistema de Confirmação de Consultas

## Visão Geral

Este documento explica passo a passo todo o desenvolvimento do sistema de confirmação de consultas médicas via WhatsApp, integrado com Botconversa e N8N para automação completa do processo.

## 🆕 **NOVAS FUNCIONALIDADES IMPLEMENTADAS**

### **Webhook Inteligente com N8N**

- **Detecção automática** de dados N8N vs webhook tradicional
- **Processamento** de respostas "1" (SIM) e "0" (NÃO)
- **Atualização automática** do banco de dados

### **Integração Botconversa**

- **API conectada** para envio de mensagens e fluxos
- **Gestão de campanhas** e subscribers
- **Workflow completo** de confirmação

### **Scheduler Avançado**

- **Jobs agendados** para confirmações e lembretes
- **Controle de frequência** configurável
- **Horários personalizáveis** via variáveis de ambiente

## 1. Estrutura do Projeto

### 1.1 Organização de Diretórios

```
confirmacao_consultas/
├── app/                    # Código principal da aplicação
│   ├── api/               # Endpoints da API
│   │   ├── routes/        # Rotas organizadas por funcionalidade
│   │   └── webhook.py     # Endpoint de webhook inteligente
│   ├── services/          # Lógica de negócio e integrações
│   │   ├── botconversa_service.py  # Integração Botconversa
│   │   ├── webhook_service.py      # Processamento de webhooks
│   │   └── scheduler.py            # Agendamento de tarefas
│   ├── config.py          # Configurações da aplicação
│   ├── database.py        # Configuração do banco de dados
│   ├── models.py          # Modelos SQLAlchemy
│   ├── schemas.py         # Schemas Pydantic
│   └── main.py           # Ponto de entrada da aplicação
├── cli/                   # Interface de linha de comando
│   ├── commands/          # Comandos organizados
│   └── cli.py            # CLI principal
├── scripts/               # Scripts utilitários
├── tests/                 # Testes automatizados
├── docs/                  # Documentação
├── logs/                  # Logs da aplicação
├── requirements.txt       # Dependências Python
├── .env.example          # Template de variáveis de ambiente
└── README.md             # Documentação principal
```

## 2. Desenvolvimento Passo a Passo

### 2.1 Configuração Inicial

**Arquivo: `requirements.txt`**

- Definimos todas as dependências necessárias
- FastAPI para a API web
- SQLAlchemy para ORM
- cx_Oracle para conexão Oracle
- OpenAI para processamento de linguagem natural
- APScheduler para agendamento de tarefas
- Loguru para logging estruturado

**Arquivo: `.env.example`**

- Template para variáveis de ambiente
- Configurações de banco, APIs e aplicação
- Segurança: nunca commitar o arquivo `.env` real

### 2.2 Configuração da Aplicação

**Arquivo: `app/config.py`**

```python
class Settings(BaseSettings):
    # Configurações do banco de dados
    database_type: str = "postgresql"
    postgresql_url: Optional[str] = None
    oracle_url: Optional[str] = None
    firebird_url: Optional[str] = None

    # Configurações do Botconversa
    botconversa_api_url: str = "https://backend.botconversa.com.br/api/v1/webhook"
    botconversa_api_key: str
    botconversa_webhook_secret: Optional[str] = None

    # Configurações de Hospital (para mensagens personalizadas)
    hospital_name: Optional[str] = None
    hospital_phone: Optional[str] = None
    hospital_address: Optional[str] = None
    hospital_city: Optional[str] = None
    hospital_state: Optional[str] = None

    # Configurações de Webhook
    webhook_host: str = "0.0.0.0"
    webhook_port: int = 8000
    webhook_url: Optional[str] = None

    # Configurações do Scheduler
    scheduler_confirmation_hour: int = 9
    scheduler_confirmation_minute: int = 0
    scheduler_reminder_hour: int = 14
    scheduler_reminder_minute: int = 0
    scheduler_enable_confirmation_job: bool = True
    scheduler_enable_reminder_job: bool = True

    # Configurações da aplicação
    app_secret_key: Optional[str] = None
    debug: bool = False
    log_level: str = "INFO"
    max_workers: int = 4
    worker_timeout: int = 30
```

**Por que Pydantic Settings?**

- Validação automática de tipos
- Carregamento de variáveis de ambiente
- Configuração centralizada e tipada

### 2.3 Configuração do Banco de Dados

**Arquivo: `app/database.py`**

```python
# Engine SQLAlchemy para Oracle
engine = create_async_engine(settings.database_url)

# Sessão local para operações
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base para modelos declarativos
Base = declarative_base()

# Dependency injection para FastAPI
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
```

**Por que SQLAlchemy?**

- ORM robusto e maduro
- Suporte nativo ao Oracle
- Migrations e versionamento de schema
- Performance otimizada

### 2.4 Modelos de Dados

**Arquivo: `app/models.py`**

**Enum de Status:**

```python
class StatusConfirmacao(str, Enum):
    PENDENTE = "PENDENTE"
    CONFIRMADO = "CONFIRMADO"
    CANCELADO = "CANCELADO"
    SEM_RESPOSTA = "SEM_RESPOSTA"
```

**Modelo Atendimento (Unificado):**

```python
class Atendimento(Base):
    __tablename__ = "atendimentos"
    __table_args__ = {"schema": "SantaCasa"}

    id = Column(Integer, primary_key=True, index=True)
    nome_paciente = Column(String(100), nullable=False)
    telefone = Column(String(20), nullable=False)
    email = Column(String(100))
    data_consulta = Column(DateTime, nullable=False)
    nome_medico = Column(String(100))
    especialidade = Column(String(100))
    status_confirmacao = Column(Enum(StatusConfirmacao), default=StatusConfirmacao.PENDENTE)

    # Campos de controle para Botconversa
    subscriber_id = Column(Integer, unique=True)
    mensagem_enviada = Column(Text)
    resposta_paciente = Column(String(10))
    respondido_em = Column(DateTime(timezone=True))

    # Controle de frequência de lembretes
    lembrete_48h_enviado = Column(Boolean, default=False)
    lembrete_12h_enviado = Column(Boolean, default=False)
    ultimo_lembrete_enviado = Column(DateTime(timezone=True))
    tipo_ultimo_lembrete = Column(String(10))

    # Timestamps
    criado_em = Column(DateTime(timezone=True), default=datetime.now)
    atualizado_em = Column(DateTime(timezone=True), onupdate=datetime.now)
```

**Por que esta estrutura?**

- Separação clara entre pacientes, consultas e confirmações
- Rastreabilidade completa das mensagens
- Flexibilidade para diferentes tipos de status
- Relacionamentos bem definidos

### 2.5 Schemas Pydantic

**Arquivo: `app/schemas.py`**

**Estrutura de Schemas:**

- `Base`: Campos comuns
- `Create`: Para criação (sem ID)
- `Response`: Para respostas da API

**Exemplo Patient:**

```python
class PatientBase(BaseModel):
    name: str
    phone: str
    email: Optional[str] = None

class PatientCreate(PatientBase):
    pass

class Patient(PatientBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True
```

**Schemas para WhatsApp:**

```python
class WhatsAppWebhook(BaseModel):
    message: str
    from_number: str
    timestamp: datetime
    message_id: str

class WhatsAppMessage(BaseModel):
    to: str
    message: str
    message_type: str = "text"
```

**Por que Pydantic?**

- Validação automática de dados
- Serialização/deserialização
- Documentação automática da API
- Type hints para melhor IDE support

### 2.6 Serviços de Integração

#### 2.6.1 Serviço WhatsApp

**Arquivo: `app/services/whatsapp_service.py`**

```python
class WhatsAppService:
    def __init__(self):
        self.api_url = settings.whatsapp_api_url
        self.webhook_secret = settings.whatsapp_webhook_secret

    async def send_message(self, to: str, message: str) -> bool:
        """Envia mensagem via WhatsApp API"""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.api_url}/send",
                    json={"to": to, "message": message}
                )
                return response.status_code == 200
        except Exception as e:
            logger.error(f"Erro ao enviar mensagem: {e}")
            return False

    def send_confirmation_message(self, patient: Patient, appointment: Appointment) -> str:
        """Gera mensagem de confirmação personalizada"""
        return f"""
Olá {patient.name}!

Você tem uma consulta agendada:
📅 Data: {appointment.scheduled_date.strftime('%d/%m/%Y')}
⏰ Horário: {appointment.scheduled_date.strftime('%H:%M')}
👨‍⚕️ Médico: {appointment.doctor_name}
🏥 Especialidade: {appointment.specialty}

Por favor, confirme sua presença respondendo:
✅ SIM - Vou comparecer
❌ NÃO - Preciso cancelar

Aguardamos sua confirmação!
        """.strip()
```

**Por que httpx?**

- Cliente HTTP assíncrono
- Performance superior ao requests
- Compatível com FastAPI

#### 2.6.2 Serviço OpenAI

**Arquivo: `app/services/openai_service.py`**

```python
class OpenAIService:
    def __init__(self):
        self.api_key = settings.openai_api_key
        self.model = settings.openai_model

    async def interpret_response(self, message: str) -> str:
        """Interpreta resposta do paciente usando OpenAI"""
        if not self.api_key:
            return self._simple_interpretation(message)

        try:
            client = AsyncOpenAI(api_key=self.api_key)
            response = await client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "Você é um assistente que interpreta respostas de pacientes sobre confirmação de consultas médicas. Responda apenas: 'confirmed', 'cancelled' ou 'unclear'."},
                    {"role": "user", "content": f"Paciente respondeu: {message}"}
                ],
                max_tokens=10
            )
            return response.choices[0].message.content.strip().lower()
        except Exception as e:
            logger.warning(f"Erro OpenAI, usando interpretação simples: {e}")
            return self._simple_interpretation(message)

    def _simple_interpretation(self, message: str) -> str:
        """Interpretação simples baseada em palavras-chave"""
        message_lower = message.lower()

        if any(word in message_lower for word in ['sim', 'confirmo', 'vou', 'comparecer', 'ok', 'certo']):
            return 'confirmed'
        elif any(word in message_lower for word in ['não', 'não posso', 'cancelar', 'desmarcar']):
            return 'cancelled'
        else:
            return 'unclear'
```

**Por que fallback simples?**

- Robustez: funciona mesmo sem OpenAI
- Performance: resposta rápida
- Confiabilidade: não depende de API externa

#### 2.6.3 Serviço de Agendamentos

**Arquivo: `app/services/appointment_service.py`**

```python
class AppointmentService:
    def __init__(self, db: Session):
        self.db = db
        self.whatsapp_service = WhatsAppService()
        self.openai_service = OpenAIService()

    def get_pending_confirmations(self) -> List[Appointment]:
        """Busca consultas que precisam de confirmação (72h antes)"""
        cutoff_time = datetime.utcnow() + timedelta(hours=72)
        return self.db.query(Appointment).filter(
            Appointment.scheduled_date <= cutoff_time,
            Appointment.status == ConfirmationStatus.PENDING
        ).all()

    def get_appointments_for_reminder(self) -> List[Appointment]:
        """Busca consultas para lembrete diário"""
        cutoff_time = datetime.utcnow() + timedelta(hours=24)
        return self.db.query(Appointment).filter(
            Appointment.scheduled_date <= cutoff_time,
            Appointment.status == ConfirmationStatus.PENDING
        ).all()

    async def send_confirmation_messages(self) -> int:
        """Envia mensagens de confirmação"""
        appointments = self.get_pending_confirmations()
        sent_count = 0

        for appointment in appointments:
            patient = appointment.patient
            message = self.whatsapp_service.send_confirmation_message(patient, appointment)

            if await self.whatsapp_service.send_message(patient.phone, message):
                # Registra confirmação
                confirmation = Confirmation(
                    appointment_id=appointment.id,
                    status=ConfirmationStatus.PENDING,
                    message_sent=message
                )
                self.db.add(confirmation)
                sent_count += 1

        self.db.commit()
        return sent_count

    async def process_patient_response(self, phone: str, message: str) -> bool:
        """Processa resposta do paciente"""
        # Busca paciente pelo telefone
        patient = self.db.query(Patient).filter(Patient.phone == phone).first()
        if not patient:
            return False

        # Busca consulta pendente
        appointment = self.db.query(Appointment).filter(
            Appointment.patient_id == patient.id,
            Appointment.status == ConfirmationStatus.PENDING
        ).first()

        if not appointment:
            return False

        # Interpreta resposta
        interpreted = await self.openai_service.interpret_response(message)

        # Atualiza status
        if interpreted == 'confirmed':
            appointment.status = ConfirmationStatus.CONFIRMED
        elif interpreted == 'cancelled':
            appointment.status = ConfirmationStatus.CANCELLED

        # Registra confirmação
        confirmation = Confirmation(
            appointment_id=appointment.id,
            status=appointment.status,
            patient_response=message,
            interpreted_response=interpreted
        )

        self.db.add(confirmation)
        self.db.commit()
        return True
```

**Por que esta lógica?**

- Separação de responsabilidades
- Reutilização de código
- Testabilidade
- Manutenibilidade

### 2.7 Agendamento de Tarefas

**Arquivo: `app/scheduler.py`**

```python
class AppointmentScheduler:
    def __init__(self):
        self.scheduler = AsyncIOScheduler()
        self.appointment_service = None

    def start(self, db: Session):
        """Inicia o scheduler"""
        self.appointment_service = AppointmentService(db)

        # Job diário às 8h para confirmações
        self.scheduler.add_job(
            self._send_confirmation_job,
            'cron', hour=8, minute=0,
            id='send_confirmations'
        )

        # Job diário às 14h para lembretes
        self.scheduler.add_job(
            self._send_reminder_job,
            'cron', hour=14, minute=0,
            id='send_reminders'
        )

        # Job a cada 30min para marcar sem resposta
        self.scheduler.add_job(
            self._mark_no_response_job,
            'interval', minutes=30,
            id='mark_no_response'
        )

        self.scheduler.start()

    async def _send_confirmation_job(self):
        """Job para enviar confirmações"""
        if self.appointment_service:
            sent_count = await self.appointment_service.send_confirmation_messages()
            logger.info(f"Enviadas {sent_count} confirmações")

    async def _send_reminder_job(self):
        """Job para enviar lembretes"""
        if self.appointment_service:
            sent_count = await self.appointment_service.send_reminder_messages()
            logger.info(f"Enviados {sent_count} lembretes")

    async def _mark_no_response_job(self):
        """Job para marcar consultas sem resposta"""
        if self.appointment_service:
            marked_count = self.appointment_service.mark_no_response_appointments()
            if marked_count > 0:
                logger.info(f"Marcadas {marked_count} consultas sem resposta")
```

**Por que APScheduler?**

- Suporte a cron expressions
- Jobs assíncronos
- Persistência de jobs
- Fácil configuração

### 2.8 API Endpoints

**Arquivo: `app/api/routes.py`**

```python
router = APIRouter()

# CRUD de Pacientes
@router.post("/patients/", response_model=Patient)
def create_patient(patient: PatientCreate, db: Session = Depends(get_db)):
    """Cria um novo paciente"""
    db_patient = Patient(**patient.dict())
    db.add(db_patient)
    db.commit()
    db.refresh(db_patient)
    return db_patient

@router.get("/patients/", response_model=List[Patient])
def list_patients(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """Lista todos os pacientes"""
    patients = db.query(Patient).offset(skip).limit(limit).all()
    return patients

# CRUD de Consultas
@router.post("/appointments/", response_model=Appointment)
def create_appointment(appointment: AppointmentCreate, db: Session = Depends(get_db)):
    """Cria uma nova consulta"""
    db_appointment = Appointment(**appointment.dict())
    db.add(db_appointment)
    db.commit()
    db.refresh(db_appointment)
    return db_appointment

@router.get("/appointments/", response_model=List[Appointment])
def list_appointments(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """Lista todas as consultas"""
    appointments = db.query(Appointment).offset(skip).limit(limit).all()
    return appointments

# Webhook WhatsApp
@router.post("/webhook/whatsapp")
async def whatsapp_webhook(webhook: WhatsAppWebhook, db: Session = Depends(get_db)):
    """Recebe mensagens do WhatsApp"""
    appointment_service = AppointmentService(db)
    success = await appointment_service.process_patient_response(
        webhook.from_number, webhook.message
    )
    return {"success": success}

# Triggers manuais
@router.post("/send-confirmations")
async def send_confirmations(db: Session = Depends(get_db)):
    """Envia confirmações manualmente"""
    appointment_service = AppointmentService(db)
    sent_count = await appointment_service.send_confirmation_messages()
    return {"sent_count": sent_count}

@router.get("/stats")
def get_stats(db: Session = Depends(get_db)):
    """Retorna estatísticas do sistema"""
    total_patients = db.query(Patient).count()
    total_appointments = db.query(Appointment).count()
    pending_confirmations = db.query(Appointment).filter(
        Appointment.status == ConfirmationStatus.PENDING
    ).count()

    return {
        "total_patients": total_patients,
        "total_appointments": total_appointments,
        "pending_confirmations": pending_confirmations
    }
```

**Por que esta estrutura de endpoints?**

- RESTful design
- Separação clara de responsabilidades
- Documentação automática
- Validação automática

### 2.9 Aplicação Principal

**Arquivo: `app/main.py`**

```python
# Configuração de logging
logger.add("logs/app.log", rotation="1 day", retention="30 days")

# Criação da aplicação FastAPI
app = FastAPI(
    title="Sistema de Confirmação de Consultas",
    description="API para gerenciamento de confirmações via WhatsApp",
    version="1.0.0"
)

# Middleware CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Inclusão das rotas
app.include_router(api_router, prefix="/api/v1")

# Eventos de startup/shutdown
@app.on_event("startup")
async def startup_event():
    """Inicializa a aplicação"""
    # Cria tabelas
    Base.metadata.create_all(bind=engine)

    # Inicia scheduler
    db = SessionLocal()
    scheduler.start(db)

@app.on_event("shutdown")
async def shutdown_event():
    """Finaliza a aplicação"""
    scheduler.stop()

# Endpoint de saúde
@app.get("/health")
def health_check():
    return {"status": "healthy", "timestamp": datetime.utcnow()}

# Handler global de exceções
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Erro não tratado: {exc}")
    return JSONResponse(
        status_code=500,
        content={"detail": "Erro interno do servidor"}
    )
```

**Por que esta estrutura?**

- Configuração centralizada
- Logging estruturado
- Tratamento de erros global
- Eventos de lifecycle

## 3. Scripts Utilitários

### 3.1 Script de Setup

**Arquivo: `setup.py`**

```python
def check_python_version():
    """Verifica versão do Python"""
    if sys.version_info < (3, 8):
        print("❌ Python 3.8+ é necessário")
        sys.exit(1)
    print("✅ Versão do Python OK")

def create_virtual_environment():
    """Cria ambiente virtual"""
    if not os.path.exists("venv"):
        subprocess.run([sys.executable, "-m", "venv", "venv"])
        print("✅ Ambiente virtual criado")
    else:
        print("✅ Ambiente virtual já existe")

def install_dependencies():
    """Instala dependências"""
    subprocess.run([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
    print("✅ Dependências instaladas")

def create_env_file():
    """Cria arquivo .env"""
    if not os.path.exists(".env"):
        shutil.copy(".env.example", ".env")
        print("✅ Arquivo .env criado")
        print("📝 Configure as variáveis no arquivo .env")
    else:
        print("✅ Arquivo .env já existe")

def main():
    """Função principal"""
    print("🚀 Configurando Sistema de Confirmação de Consultas...")

    check_python_version()
    create_virtual_environment()
    install_dependencies()
    create_env_file()

    print("\n✅ Setup concluído!")
    print("📝 Configure o arquivo .env com suas credenciais")
    print("🚀 Execute 'make run' para iniciar a aplicação")
```

### 3.2 Script de Inicialização do Banco

**Arquivo: `scripts/init_db.py`**

```python
def init_database():
    """Inicializa banco com dados de exemplo"""
    engine = create_engine(settings.database_url)
    Base.metadata.create_all(bind=engine)

    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = SessionLocal()

    # Verifica se já existem dados
    if db.query(Patient).count() == 0:
        # Cria pacientes de exemplo
        patients = [
            Patient(name="João Silva", phone="+5511999999999", email="joao@email.com"),
            Patient(name="Maria Santos", phone="+5511888888888", email="maria@email.com"),
        ]

        for patient in patients:
            db.add(patient)

        db.commit()

        # Cria consultas de exemplo
        appointments = [
            Appointment(
                patient_id=1,
                scheduled_date=datetime.utcnow() + timedelta(days=3),
                doctor_name="Dr. Carlos",
                specialty="Cardiologia"
            ),
            Appointment(
                patient_id=2,
                scheduled_date=datetime.utcnow() + timedelta(days=2),
                doctor_name="Dra. Ana",
                specialty="Dermatologia"
            ),
        ]

        for appointment in appointments:
            db.add(appointment)

        db.commit()
        print("✅ Dados de exemplo criados")
    else:
        print("✅ Banco já possui dados")

if __name__ == "__main__":
    init_database()
```

### 3.3 Script de Teste WhatsApp

**Arquivo: `scripts/test_whatsapp.py`**

```python
def test_whatsapp_integration():
    """Testa integração com WhatsApp"""
    if not settings.whatsapp_api_url:
        print("❌ WhatsApp API não configurada")
        return

    # Busca paciente de exemplo
    engine = create_engine(settings.database_url)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = SessionLocal()

    patient = db.query(Patient).first()
    if not patient:
        print("❌ Nenhum paciente encontrado")
        return

    appointment = db.query(Appointment).filter(
        Appointment.patient_id == patient.id
    ).first()

    if not appointment:
        print("❌ Nenhuma consulta encontrada")
        return

    # Gera mensagem
    whatsapp_service = WhatsAppService()
    message = whatsapp_service.send_confirmation_message(patient, appointment)

    print(f"📱 Mensagem gerada para {patient.name}:")
    print(message)

    # Pergunta se deve enviar
    response = input("\nEnviar mensagem? (s/n): ")
    if response.lower() == 's':
        success = asyncio.run(whatsapp_service.send_message(patient.phone, message))
        if success:
            print("✅ Mensagem enviada com sucesso!")
        else:
            print("❌ Erro ao enviar mensagem")
    else:
        print("ℹ️ Mensagem não enviada")

if __name__ == "__main__":
    test_whatsapp_integration()
```

## 4. Testes

### 4.1 Configuração de Testes

**Arquivo: `pytest.ini`**

```ini
[tool:pytest]
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*
addopts = -v --tb=short
filterwarnings =
    ignore::DeprecationWarning
    ignore::PendingDeprecationWarning
```

### 4.2 Testes Unitários

**Arquivo: `tests/test_app.py`**

```python
class TestOpenAIService:
    def test_simple_interpretation_confirmed(self):
        """Testa interpretação simples - confirmado"""
        service = OpenAIService()
        result = service._simple_interpretation("Sim, vou comparecer")
        assert result == "confirmed"

    def test_simple_interpretation_cancelled(self):
        """Testa interpretação simples - cancelado"""
        service = OpenAIService()
        result = service._simple_interpretation("Não posso ir")
        assert result == "cancelled"

    def test_simple_interpretation_unclear(self):
        """Testa interpretação simples - não claro"""
        service = OpenAIService()
        result = service._simple_interpretation("Talvez")
        assert result == "unclear"

class TestAppointmentService:
    def test_get_pending_confirmations(self):
        """Testa busca de confirmações pendentes"""
        # Setup mock database
        db = MagicMock()
        service = AppointmentService(db)

        # Mock query results
        mock_appointments = [
            Appointment(scheduled_date=datetime.utcnow() + timedelta(hours=48)),
            Appointment(scheduled_date=datetime.utcnow() + timedelta(hours=24))
        ]
        db.query.return_value.filter.return_value.all.return_value = mock_appointments

        result = service.get_pending_confirmations()
        assert len(result) == 2

class TestModels:
    def test_patient_creation(self):
        """Testa criação de paciente"""
        patient = Patient(
            name="Teste",
            phone="+5511999999999",
            email="teste@email.com"
        )
        assert patient.name == "Teste"
        assert patient.phone == "+5511999999999"

    def test_appointment_creation(self):
        """Testa criação de consulta"""
        appointment = Appointment(
            patient_id=1,
            scheduled_date=datetime.utcnow(),
            doctor_name="Dr. Teste",
            specialty="Teste"
        )
        assert appointment.patient_id == 1
        assert appointment.doctor_name == "Dr. Teste"

def test_confirmation_status_enum():
    """Testa enum de status de confirmação"""
    assert ConfirmationStatus.PENDING == "pending"
    assert ConfirmationStatus.CONFIRMED == "confirmed"
    assert ConfirmationStatus.CANCELLED == "cancelled"
    assert ConfirmationStatus.NO_RESPONSE == "no_response"
```

## 5. Containerização

### 5.1 Dockerfile

**Arquivo: `Dockerfile`**

```dockerfile
# Estágio de build
FROM python:3.11-slim as builder

# Instala dependências do sistema
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    libaio1 \
    wget \
    unzip \
    && rm -rf /var/lib/apt/lists/*

# Instala Oracle Instant Client
RUN wget https://download.oracle.com/otn_software/linux/instantclient/instantclient-basiclite-linuxx64.zip \
    && unzip instantclient-basiclite-linuxx64.zip \
    && mv instantclient_* /opt/oracle/instantclient \
    && rm instantclient-basiclite-linuxx64.zip

# Configura variáveis de ambiente Oracle
ENV LD_LIBRARY_PATH=/opt/oracle/instantclient
ENV PATH=/opt/oracle/instantclient:$PATH

# Cria usuário não-root
RUN useradd --create-home --shell /bin/bash app

# Copia requirements e instala dependências Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Estágio de produção
FROM python:3.11-slim

# Copia Oracle Client do estágio anterior
COPY --from=builder /opt/oracle/instantclient /opt/oracle/instantclient
COPY --from=builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages

# Configura variáveis de ambiente
ENV LD_LIBRARY_PATH=/opt/oracle/instantclient
ENV PATH=/opt/oracle/instantclient:$PATH

# Cria usuário não-root
RUN useradd --create-home --shell /bin/bash app

# Define diretório de trabalho
WORKDIR /app

# Copia código da aplicação
COPY --chown=app:app app/ ./app/
COPY --chown=app:app scripts/ ./scripts/

# Cria diretório de logs
RUN mkdir -p logs && chown app:app logs

# Muda para usuário não-root
USER app

# Expõe porta
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Comando para executar aplicação
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### 5.2 Docker Compose

**Arquivo: `docker-compose.yml`**

```yaml
version: "3.8"

services:
  app:
    build: .
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=${DATABASE_URL}
      - WHATSAPP_API_URL=${WHATSAPP_API_URL}
      - WHATSAPP_WEBHOOK_SECRET=${WHATSAPP_WEBHOOK_SECRET}
      - OPENAI_API_KEY=${OPENAI_API_KEY}
      - APP_SECRET_KEY=${APP_SECRET_KEY}
      - DEBUG=${DEBUG:-false}
      - LOG_LEVEL=${LOG_LEVEL:-INFO}
    volumes:
      - ./logs:/app/logs
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 40s

  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf:ro
    depends_on:
      - app
    profiles:
      - production
    restart: unless-stopped
```

## 6. Automação com Makefile

**Arquivo: `Makefile`**

```makefile
.PHONY: help install setup run test clean docker-build docker-run

# Variáveis
PYTHON = python
PIP = pip
UVICORN = uvicorn
PYTEST = pytest

# Comandos padrão
help: ## Mostra esta ajuda
	@echo "Comandos disponíveis:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

install: ## Instala dependências
	$(PIP) install -r requirements.txt

setup: ## Configura o projeto
	$(PYTHON) setup.py

run: ## Executa a aplicação em desenvolvimento
	$(UVICORN) app.main:app --reload --host 0.0.0.0 --port 8000

test: ## Executa os testes
	$(PYTEST) tests/ -v

init-db: ## Inicializa o banco de dados
	$(PYTHON) scripts/init_db.py

test-whatsapp: ## Testa integração WhatsApp
	$(PYTHON) scripts/test_whatsapp.py

docker-build: ## Constrói imagem Docker
	docker build -t hospital-app .

docker-compose-up: ## Inicia serviços Docker Compose
	docker-compose up -d

clean: ## Limpa arquivos temporários
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete
	rm -rf .pytest_cache

# Comandos de desenvolvimento
dev-setup: setup install init-db ## Setup completo para desenvolvimento
	@echo "✅ Setup de desenvolvimento concluído!"

# Comandos de deploy
deploy-docker: docker-build docker-run ## Deploy com Docker
```

## 7. Fluxo de Dados

### 7.1 Fluxo de Confirmação

1. **Agendamento**: Consulta é criada com status `PENDING`
2. **72h antes**: Scheduler executa job de confirmação
3. **Envio**: WhatsApp Service envia mensagem personalizada
4. **Registro**: Confirmation é criada com status `PENDING`
5. **Resposta**: Paciente responde via WhatsApp
6. **Webhook**: Endpoint recebe resposta
7. **Interpretação**: OpenAI Service interpreta resposta
8. **Atualização**: Status da consulta é atualizado
9. **Registro**: Nova Confirmation com resposta do paciente

### 7.2 Fluxo de Lembrete

1. **Verificação**: Scheduler verifica consultas pendentes
2. **Filtro**: Consultas dentro de 24h sem confirmação
3. **Envio**: WhatsApp Service envia lembrete
4. **Registro**: Confirmation é criada
5. **Repetição**: Processo se repete até confirmação

### 7.3 Fluxo de Marcação Sem Resposta

1. **Verificação**: Scheduler verifica a cada 30min
2. **Filtro**: Consultas passadas sem confirmação
3. **Atualização**: Status muda para `NO_RESPONSE`
4. **Parada**: Não envia mais mensagens

## 8. Considerações de Segurança

### 8.1 Validação de Entrada

- Pydantic schemas validam todos os dados
- Sanitização de mensagens do WhatsApp
- Validação de números de telefone

### 8.2 Autenticação

- Webhook secret para validação
- API key para OpenAI
- Variáveis de ambiente para credenciais

### 8.3 Logs e Monitoramento

- Logs estruturados com Loguru
- Endpoint de health check
- Tratamento de erros global

## 9. Performance e Escalabilidade

### 9.1 Otimizações

- Conexões assíncronas com httpx
- Sessões de banco gerenciadas
- Jobs agendados eficientes

### 9.2 Escalabilidade

- Containerização com Docker
- Load balancer com Nginx
- Banco de dados Oracle robusto

## 10. Próximos Passos

### 10.1 Melhorias Sugeridas

- Implementar cache Redis
- Adicionar métricas com Prometheus
- Implementar rate limiting
- Adicionar autenticação JWT
- Implementar testes de integração

### 10.2 Monitoramento

- Logs centralizados
- Métricas de performance
- Alertas automáticos
- Dashboard de status

Este guia cobre todo o desenvolvimento do sistema, desde a concepção até a implementação completa. Cada componente foi projetado pensando em manutenibilidade, escalabilidade e robustez.
