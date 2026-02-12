from enum import Enum
from typing import Optional

from pydantic_settings import BaseSettings


class DataBaseType(str, Enum):
    """Tipos de banco de dados suportados pela aplicação."""

    ORACLE = "oracle"
    POSTGRESQL = "postgresql"
    FIREBIRD = "firebird"


class Settings(BaseSettings):
    """
    Configurações da aplicação carregadas de variáveis de ambiente.

    Suporta múltiplos tipos de banco de dados (Oracle, PostgreSQL, Firebird)
    e configurações para APIs externas (Botconversa).

    Attributes:
        database_type: Tipo de banco de dados a ser usado (padrão: ORACLE)
        database_url: URL genérica do banco de dados (fallback)
        oracle_url: URL específica para Oracle
        postgresql_url: URL específica para PostgreSQL
        firebird_url: URL específica para Firebird
        botconversa_api_url: URL da API do Botconversa (obrigatório)
        botconversa_webhook_secret: Chave secreta do webhook do Botconversa (obrigatório)
        botconversa_api_key: Chave da API do Botconversa (obrigatório)
        app_secret_key: Chave secreta da aplicação (opcional - para futuras funcionalidades de segurança)
        hospital_name: Nome do hospital (opcional - para identificação e logs)
        debug: Modo debug da aplicação (padrão: False)
        log_level: Nível de log (padrão: INFO)
        max_workers: Número máximo de workers (padrão: 4) - para futuras funcionalidades de processamento assíncrono
        worker_timeout: Timeout dos workers em segundos (padrão: 30)
        reminder_interval: Intervalo de lembretes em horas (padrão: 24)
        confirmation_window_hours: Janela de confirmação em horas (padrão: 72)
    """

    # Database Configuration
    database_type: DataBaseType = DataBaseType.ORACLE
    database_url: Optional[str] = None

    # Oracle specific configuration
    oracle_url: Optional[str] = None

    # PostgreSQL specific configuration
    postgresql_url: Optional[str] = None

    # Firebird specific configuration
    firebird_url: Optional[str] = None

    # Botconversa API Configuration
    botconversa_api_url: str = "https://backend.botconversa.com.br/api/v1/webhook"
    botconversa_webhook_secret: Optional[str] = None
    botconversa_api_key: Optional[str] = None

    # Application Configuration
    app_secret_key: Optional[str] = None
    hospital_name: Optional[str] = None
    debug: bool = False
    log_level: str = "INFO"

    # Hospital Information (para mensagens personalizadas)
    hospital_phone: Optional[str] = None
    hospital_address: Optional[str] = None
    hospital_city: Optional[str] = None
    hospital_state: Optional[str] = None

    # Performance settings Configuration
    max_workers: int = 4
    worker_timeout: int = 30

    # Webhook Configuration
    webhook_host: str = "0.0.0.0"  # Host para aceitar conexões externas
    webhook_port: int = 8000  # Porta do servidor webhook
    webhook_url: Optional[str] = None  # URL pública do webhook

    # Scheduler Configuration
    reminder_interval: int = 24
    confirmation_window_hours: int = 72

    # Scheduler Time Configuration
    scheduler_confirmation_hour: int = 9  # Hora para verificar confirmações (0-23)
    scheduler_confirmation_minute: int = 0  # Minuto para verificar confirmações (0-59)
    scheduler_reminder_hour: int = 14  # Hora para verificar lembretes (0-23)
    scheduler_reminder_minute: int = 0  # Minuto para verificar lembretes (0-59)

    # Scheduler Job Configuration
    scheduler_enable_confirmation_job: bool = True  # Habilitar job de confirmação
    scheduler_enable_reminder_job: bool = True  # Habilitar job de lembretes

    # SQLite (controle "já enviado" para lembretes 48h/12h)
    sqlite_url: str = "sqlite:///./data/envios_lembrete.db"

    # View de confirmação (banco principal - Oracle)
    view_confirmacao_nome: str = "TASY.AVA_CONFIRMACAO_CONSULTA"

    # Tabela agenda_consulta no banco principal (para UPDATE de confirmação)
    tabela_agenda_consulta: str = "TASY.AGENDA_CONSULTA"

    # Intervalo (minutos) para consultar a view e processar lembretes 48h/12h
    view_poll_interval_minutes: int = 5

    # Se False, não cria tabelas da app (atendimentos, etc.) no startup - uso apenas view + agenda_consulta
    create_app_tables: bool = True

    class Config:
        env_file = ".env"
        case_sensitive = False
        extra = "ignore"

    @property
    def get_database_url(self) -> str:
        """
        Retorna a URL do banco de dados baseado no tipo selecionado.

        Returns:
            str: URL do banco de dados configurado

        Raises:
            ValueError: Se o tipo de banco de dados não for suportado
        """
        if self.database_type == DataBaseType.ORACLE:
            return self.oracle_url or self.database_url
        elif self.database_type == DataBaseType.POSTGRESQL:
            return self.postgresql_url or self.database_url
        elif self.database_type == DataBaseType.FIREBIRD:
            return self.firebird_url or self.database_url
        else:
            raise ValueError(
                f"Tipo de banco de dados não suportado: {self.database_type}"
            )


settings = Settings()
