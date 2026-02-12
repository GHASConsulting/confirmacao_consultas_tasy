"""
Módulo de serviços da aplicação.

Este módulo contém a lógica de negócio para:
- Integração com Botconversa
- Processamento de webhooks (N8N)
- Lembretes 48h/12h (view + SQLite)
"""

from .botconversa_service import BotconversaService
from .webhook_service import WebhookService

__all__ = [
    "BotconversaService",
    "WebhookService",
]
