from datetime import datetime
from typing import Optional

from pydantic import BaseModel

from app.database.models import StatusConfirmacao


class PacienteBase(BaseModel):
    nome: str
    telefone: str
    email: Optional[str] = None


class Paciente(PacienteBase):
    id: int
    criado_em: datetime
    atualizado_em: Optional[datetime]

    class Config:
        from_attributes = True


class AgendamentoBase(BaseModel):
    nome_medico: str
    especialidade: str
    data_consulta: datetime
    observacoes: Optional[str] = None


class AgendamentoCreate(AgendamentoBase):
    paciente_id: int


class Agendamento(AgendamentoBase):
    id: int
    paciente_id: int
    status: StatusConfirmacao
    criado_em: datetime
    atualizado_em: Optional[datetime] = None
    paciente: Paciente

    class Config:
        from_attributes = True


class ConfirmacaoBase(BaseModel):
    mensagem_enviada: str
    resposta_paciente: Optional[str] = None
    interpretacao_resposta: Optional[str] = None


class ConfirmacaoCreate(ConfirmacaoBase):
    consulta_id: int


class Confirmacao(ConfirmacaoBase):
    id: int
    consulta_id: int
    enviado_em: datetime
    respondido_em: Optional[datetime] = None

    class Config:
        from_attributes = True


class BotconversaWebhook(BaseModel):
    """Schema para receber webhooks do Botconversa."""

    type: str  # "message" ou "status"
    contact: Optional[dict] = None  # Dados do contato
    message: Optional[dict] = None  # Dados da mensagem
    status: Optional[str] = None  # Status de entrega


class BotconversaMessage(BaseModel):
    """Schema para enviar mensagens via Botconversa."""

    phone: str
    message: str


class N8NWebhookData(BaseModel):
    """Schema para receber dados do N8N com respostas dos pacientes."""

    telefone: str
    subscriber_id: int
    resposta: str  # "1" para SIM, "0" para NÃO
    nome_paciente: Optional[str] = None
    mensagem_original: Optional[str] = None
