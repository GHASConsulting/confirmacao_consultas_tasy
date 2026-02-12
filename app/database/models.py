import enum

from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    Enum,
    ForeignKey,
    Integer,
    String,
    Text,
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.database.base import Base


class StatusConfirmacao(enum.Enum):
    """
    Enumeração dos possíveis status de confirmação de consultas.

    Attributes:
        PENDENTE: Consulta aguardando confirmação do paciente
        CONFIRMADO: Consulta confirmada pelo paciente
        CANCELADO: Consulta cancelada pelo paciente
        SEM_RESPOSTA: Consulta sem resposta do paciente
    """

    PENDENTE = "pendente"
    CONFIRMADO = "confirmado"
    CANCELADO = "cancelado"
    SEM_RESPOSTA = "sem_resposta"


class Atendimento(Base):
    """
    Modelo unificado para representar um atendimento completo no sistema.

    Este model consolida todos os dados necessários para o fluxo do Botconversa:
    - Dados do paciente
    - Dados da consulta
    - Dados do Botconversa (subscriber_id)
    - Campo de controle para confirmação
    - Status e histórico de respostas

    Attributes:
        id: Identificador único do atendimento
        nome_paciente: Nome completo do paciente
        telefone: Número de telefone (único)
        email: Endereço de email do paciente
        nome_medico: Nome do médico responsável
        especialidade: Especialidade médica
        data_consulta: Data e hora da consulta
        observacoes: Observações adicionais sobre a consulta
        status: Status atual da confirmação (campo de controle)
        subscriber_id: ID do subscriber no Botconversa
        mensagem_enviada: Mensagem enviada ao paciente
        resposta_paciente: Resposta recebida do paciente
        interpretacao_resposta: Interpretação da resposta
        enviado_em: Data/hora do envio da mensagem
        respondido_em: Data/hora da resposta do paciente
        lembrete_48h_enviado: Indica se o lembrete 48h foi enviado
        lembrete_12h_enviado: Indica se o lembrete 12h foi enviado
        ultimo_lembrete_enviado: Data/hora do último lembrete enviado
        tipo_ultimo_lembrete: Tipo do último lembrete ("48h" ou "12h")
        criado_em: Data/hora de criação do registro
        atualizado_em: Data/hora da última atualização
        nr_seq_agenda: Número sequencial da agenda (campo obrigatório)
    """

    __tablename__ = "ghas_tbl_pac_agendados"

    id = Column(Integer, primary_key=True, index=True)

    # Dados do paciente
    nome_paciente = Column(String(255), nullable=False)
    telefone = Column(String(20), nullable=False, index=True)
    email = Column(String(255))

    # Dados da consulta
    nome_medico = Column(String(255), nullable=False)
    especialidade = Column(String(255), nullable=False)
    data_consulta = Column(DateTime, nullable=False, index=True)
    observacoes = Column(Text)

    # Campo de controle para confirmação
    status_confirmacao= Column(
        Enum(StatusConfirmacao), default=StatusConfirmacao.PENDENTE, nullable=False
    )

    # Dados do Botconversa
    subscriber_id = Column(Integer, nullable=True, index=True)

    # Dados de mensagem e resposta
    mensagem_enviada = Column(Text)
    resposta_paciente = Column(Text)
    interpretacao_resposta = Column(
        String(50)
    )  # "confirmado", "cancelado", "indefinido"

    # Controle de frequência de lembretes
    lembrete_48h_enviado = Column(
        Boolean, default=False
    )  # Lembrete 48h antes foi enviado
    lembrete_12h_enviado = Column(
        Boolean, default=False
    )  # Lembrete 12h antes foi enviado
    ultimo_lembrete_enviado = Column(
        DateTime(timezone=True)
    )  # Data/hora do último lembrete
    tipo_ultimo_lembrete = Column(
        String(10)
    )  # Tipo do último lembrete ("48h" ou "12h")

    # Campo obrigatório para número sequencial da agenda
    nr_seq_agenda = Column(Integer, nullable=False)

    # Timestamps
    enviado_em = Column(DateTime(timezone=True))
    respondido_em = Column(DateTime(timezone=True))
    criado_em = Column(DateTime(timezone=True), server_default=func.now())
    atualizado_em = Column(DateTime(timezone=True), onupdate=func.now())


class Paciente(Base):
    """
    Modelo para representar um paciente no sistema.

    Armazena informações básicas do paciente como nome, telefone e email.
    Mantém relacionamento com as consultas do paciente.

    Attributes:
        id: Identificador único do paciente
        nome: Nome completo do paciente
        telefone: Número de telefone (único)
        email: Endereço de email do paciente
        criado_em: Data/hora de criação do registro
        atualizado_em: Data/hora da última atualização
        consultas: Relacionamento com as consultas do paciente
    """

    __tablename__ = "pacientes"

    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String(255), nullable=False)
    telefone = Column(String(20), unique=True, nullable=False, index=True)
    email = Column(String(255))
    criado_em = Column(DateTime(timezone=True), server_default=func.now())
    atualizado_em = Column(DateTime(timezone=True), onupdate=func.now())

    # Relação com o model Consulta para acessar as consultas do paciente
    # A relação é feita através da chave estrangeira paciente_id na tabela Consulta
    consultas = relationship("Consulta", back_populates="paciente")


class Consulta(Base):
    """
    Modelo para representar uma consulta médica no sistema.

    Armazena informações sobre consultas agendadas, incluindo médico,
    especialidade, data/hora e status de confirmação.

    Attributes:
        id: Identificador único da consulta
        paciente_id: ID do paciente (chave estrangeira)
        nome_medico: Nome do médico responsável
        especialidade: Especialidade médica
        data_consulta: Data e hora da consulta
        status: Status atual da confirmação
        observacoes: Observações adicionais sobre a consulta
        criado_em: Data/hora de criação do registro
        atualizado_em: Data/hora da última atualização
        paciente: Relacionamento com o paciente
        confirmacoes: Relacionamento com as confirmações da consulta
    """

    __tablename__ = "consultas"

    id = Column(Integer, primary_key=True, index=True)
    paciente_id = Column(Integer, ForeignKey("pacientes.id"), nullable=False)
    nome_medico = Column(String(255), nullable=False)
    especialidade = Column(String(255), nullable=False)
    data_consulta = Column(DateTime, nullable=False, index=True)
    status = Column(Enum(StatusConfirmacao), default=StatusConfirmacao.PENDENTE)
    observacoes = Column(Text)
    criado_em = Column(DateTime(timezone=True), server_default=func.now())
    atualizado_em = Column(DateTime(timezone=True), onupdate=func.now())

    paciente = relationship("Paciente", back_populates="consultas")
    confirmacoes = relationship("Confirmacao", back_populates="consulta")


class Confirmacao(Base):
    """
    Modelo para representar confirmações de consultas.

    Armazena o histórico de tentativas de confirmação e respostas
    dos pacientes para cada consulta.

    Attributes:
        id: Identificador único da confirmação
        consulta_id: ID da consulta (chave estrangeira)
        mensagem_enviada: Mensagem enviada ao paciente
        resposta_paciente: Resposta recebida do paciente
        interpretacao_resposta: Interpretação da resposta ("confirmado", "cancelado", "indefinido")
        enviado_em: Data/hora do envio da mensagem
        respondido_em: Data/hora da resposta do paciente
        consulta: Relacionamento com a consulta
    """

    __tablename__ = "confirmacoes"

    id = Column(Integer, primary_key=True, index=True)
    consulta_id = Column(Integer, ForeignKey("consultas.id"), nullable=False)
    mensagem_enviada = Column(Text, nullable=False)
    resposta_paciente = Column(Text)
    interpretacao_resposta = Column(
        String(50)
    )  # "confirmado", "cancelado", "indefinido"
    enviado_em = Column(DateTime(timezone=True), server_default=func.now())
    respondido_em = Column(DateTime(timezone=True))

    consulta = relationship("Consulta", back_populates="confirmacoes")
