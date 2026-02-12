"""
SQLite para controle de envios de lembretes (48h e 12h).

Armazena o que já foi enviado para comparar com a view e evitar reenvios.
Também serve de base para derivar a lista de 12h a partir do que foi enviado em 48h.
"""

from datetime import datetime

from sqlalchemy import Column, DateTime, Integer, String, Text, create_engine, text
from sqlalchemy.orm import declarative_base, sessionmaker

from app.config.config import settings

SqliteBase = declarative_base()


class EnvioLembrete(SqliteBase):
    """
    Registro de envio de lembrete (48h ou 12h) por nr_sequencia.

    - 48h: preenchido ao enviar lembrete 48h (dados vêm da view).
    - 12h: preenchido ao enviar lembrete 12h (dados vêm do próprio SQLite).
    """

    __tablename__ = "envios_lembrete"

    id = Column(Integer, primary_key=True, autoincrement=True)
    nr_sequencia = Column(Integer, nullable=False, index=True)
    cd_agenda = Column(Integer, nullable=True, index=True)  # nr_sequencia_agenda: identifica a agenda para UPDATE
    tipo_lembrete = Column(String(3), nullable=False, index=True)  # '48H' ou '12H'
    enviado_em = Column(DateTime, nullable=False, default=datetime.utcnow)

    # Dados guardados para montar mensagem 12h depois (e auditoria)
    dt_agenda = Column(DateTime, nullable=True)
    nr_telefone = Column(String(80), nullable=True)
    nm_paciente = Column(String(255), nullable=True)
    nr_ddi = Column(String(3), nullable=True)
    nm_medico_externo = Column(String(60), nullable=True)

    # Resposta do paciente (preenchido quando webhook confirma/cancela)
    resposta_paciente = Column(String(10), nullable=True)  # '1' confirmado, '0' cancelado
    dt_resposta = Column(DateTime, nullable=True)

    class Config:
        pass


# Engine e sessão SQLite (inicializados em init_sqlite)
_sqlite_engine = None
_sqlite_session_factory = None


def init_sqlite() -> None:
    """Inicializa conexão e cria tabela no SQLite."""
    import os

    global _sqlite_engine, _sqlite_session_factory
    url = getattr(settings, "sqlite_url", "sqlite:///./data/envios_lembrete.db")
    if "/./data/" in url or "\\data\\" in url:
        os.makedirs("data", exist_ok=True)
    _sqlite_engine = create_engine(
        url,
        connect_args={"check_same_thread": False},
        echo=settings.debug,
    )
    SqliteBase.metadata.create_all(bind=_sqlite_engine)
    # Migração: adicionar coluna cd_agenda se a tabela já existia sem ela
    with _sqlite_engine.connect() as conn:
        r = conn.execute(
            text("SELECT 1 FROM pragma_table_info('envios_lembrete') WHERE name = 'cd_agenda'")
        )
        if r.scalar() is None:
            conn.execute(text("ALTER TABLE envios_lembrete ADD COLUMN cd_agenda INTEGER"))
            conn.commit()
    _sqlite_session_factory = sessionmaker(
        autocommit=False, autoflush=False, bind=_sqlite_engine
    )


def get_sqlite_session():
    """Retorna uma sessão do SQLite (context manager ou generator)."""
    if _sqlite_session_factory is None:
        init_sqlite()
    return _sqlite_session_factory()


def get_sqlite_db():
    """Generator para uso como dependência (yield session, close no finally)."""
    session = get_sqlite_session()
    try:
        yield session
    finally:
        session.close()
