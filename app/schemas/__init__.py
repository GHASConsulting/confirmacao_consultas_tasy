"""
Schemas Pydantic para validação de dados da aplicação.

Este módulo contém todos os schemas utilizados para:
- Validação de entrada da API
- Serialização de respostas
- Documentação automática do Swagger
"""

from .schemas import (
    # Paciente schemas
    PacienteBase,
    Paciente,
    # Agendamento schemas
    AgendamentoBase,
    AgendamentoCreate,
    Agendamento,
    # Confirmacao schemas
    ConfirmacaoBase,
    ConfirmacaoCreate,
    Confirmacao,
    # Botconversa schemas
    BotconversaWebhook,
    BotconversaMessage,
)

__all__ = [
    # Paciente schemas
    "PacienteBase",
    "Paciente",
    # Agendamento schemas
    "AgendamentoBase",
    "AgendamentoCreate",
    "Agendamento",
    # Confirmacao schemas
    "ConfirmacaoBase",
    "ConfirmacaoCreate",
    "Confirmacao",
    # Botconversa schemas
    "BotconversaWebhook",
    "BotconversaMessage",
]
