"""
Rotas para webhooks do Botconversa.

Este módulo contém os endpoints para receber e processar webhooks
enviados pelo Botconversa quando pacientes respondem às mensagens.
"""

from typing import Any, Dict

from fastapi import APIRouter, Depends, HTTPException, Request
from loguru import logger
from sqlalchemy.orm import Session

from app.database.manager import get_db
from app.schemas.schemas import BotconversaWebhook
from app.services.webhook_service import WebhookService

router = APIRouter(prefix="/webhook", tags=["webhook"])


@router.post("/botconversa")
async def botconversa_webhook(
    request: Request, db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    Endpoint para receber webhooks do Botconversa e dados do N8N.

    Este endpoint detecta automaticamente se são dados do N8N ou webhook tradicional
    e processa adequadamente cada tipo de dados.
    """
    try:
        # Lê o corpo da requisição
        webhook_data = await request.json()
        logger.info(f"Webhook recebido: {webhook_data}")

        # Cria instância do serviço
        webhook_service = WebhookService(db)

        # Detecta automaticamente se são dados do N8N
        # Dados do N8N têm: telefone, subscriber_id, resposta
        if all(
            key in webhook_data for key in ["telefone", "subscriber_id", "resposta"]
        ):
            logger.info(
                "Detectados dados do N8N - processando com processar_n8n_webhook"
            )
            resultado = webhook_service.processar_n8n_webhook(webhook_data)
        else:
            logger.info(
                "Dados tradicionais de webhook - processando com processar_webhook"
            )
            resultado = webhook_service.processar_webhook(webhook_data)

        if resultado.get("success"):
            logger.info(f"Webhook processado com sucesso: {resultado}")
            return {
                "success": True,
                "message": "Webhook processado com sucesso",
                "data": resultado,
            }
        else:
            logger.error(f"Erro ao processar webhook: {resultado}")
            raise HTTPException(
                status_code=400,
                detail=f"Erro ao processar webhook: {resultado.get('error', 'Erro desconhecido')}",
            )

    except Exception as e:
        logger.error(f"Erro ao processar webhook: {str(e)}")
        raise HTTPException(
            status_code=500, detail=f"Erro interno ao processar webhook: {str(e)}"
        )


@router.get("/botconversa/health")
async def webhook_health() -> Dict[str, Any]:
    """
    Endpoint de saúde para verificar se o webhook está funcionando.
    """
    return {
        "success": True,
        "message": "Webhook endpoint está funcionando",
        "status": "healthy",
    }
