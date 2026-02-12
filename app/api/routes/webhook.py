"""
Rotas para webhooks do Botconversa.

Este módulo contém os endpoints para receber e processar webhooks
enviados pelo Botconversa quando pacientes respondem às mensagens.
"""

import hmac
import json
from typing import Any, Dict

from fastapi import APIRouter, Depends, HTTPException, Request
from loguru import logger
from sqlalchemy.orm import Session

from app.config.config import settings
from app.database.manager import get_db
from app.schemas.schemas import BotconversaWebhook
from app.services.webhook_service import WebhookService

router = APIRouter(prefix="/webhook", tags=["webhook"])


def _validar_assinatura_webhook(body: bytes, signature_recebida: str, secret: str) -> bool:
    """Valida assinatura HMAC-SHA256 do body. Retorna True se válida."""
    try:
        esperado = hmac.new(
            secret.encode("utf-8"),
            body,
            "sha256",
        ).hexdigest().lower()
        # Pode vir com prefixo tipo "sha256=..." ou "v1=..."
        recebido = signature_recebida.strip().lower()
        if "=" in recebido:
            recebido = recebido.split("=", 1)[-1].strip()
        return hmac.compare_digest(esperado, recebido)
    except Exception:
        return False


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
        logger.info("=== INÍCIO DO PROCESSAMENTO DO WEBHOOK ===")

        # Lê o corpo bruto (necessário para validar assinatura e depois parsear JSON)
        body = await request.body()
        secret = getattr(settings, "botconversa_webhook_secret", None) or ""
        header_name = getattr(settings, "webhook_signature_header", "X-Webhook-Signature")
        signature_recebida = request.headers.get(header_name) or request.headers.get("X-Webhook-Signature") or ""

        # Validação opcional: só valida se o secret estiver configurado E o header de assinatura tiver vindo
        if secret and signature_recebida:
            if not _validar_assinatura_webhook(body, signature_recebida, secret):
                logger.warning("Webhook rejeitado: assinatura inválida")
                raise HTTPException(status_code=401, detail="Assinatura do webhook inválida")
            logger.info("Assinatura do webhook validada com sucesso")
        # Se secret não está setado ou não veio assinatura, segue normal (não quebra N8N nem fluxo atual)

        if not body:
            webhook_data = {}
        else:
            try:
                webhook_data = json.loads(body.decode("utf-8"))
            except json.JSONDecodeError as e:
                logger.error(f"Webhook com body JSON inválido: {e}")
                raise HTTPException(status_code=400, detail="Body JSON inválido")
        logger.info(f"Webhook recebido: {webhook_data}")

        # Cria instância do serviço
        logger.info("Criando instância do WebhookService...")
        webhook_service = WebhookService(db)
        logger.info("WebhookService criado com sucesso")

        # Detecta automaticamente se são dados do N8N
        # Dados do N8N têm: telefone, subscriber_id, resposta
        logger.info("Verificando tipo de dados...")
        if all(
            key in webhook_data for key in ["telefone", "subscriber_id", "resposta"]
        ):
            logger.info(
                "Detectados dados do N8N - processando com processar_n8n_webhook"
            )
            resultado = webhook_service.processar_n8n_webhook(webhook_data)
            logger.info(f"Resultado do processar_n8n_webhook: {resultado}")
        else:
            logger.info(
                "Dados tradicionais de webhook - processando com processar_webhook"
            )
            resultado = webhook_service.processar_webhook(webhook_data)
            logger.info(f"Resultado do processar_webhook: {resultado}")

        logger.info("Verificando resultado...")
        logger.info(f"Resultado completo: {resultado}")
        logger.info(f"Tipo do resultado: {type(resultado)}")
        logger.info(f"Resultado.get('success'): {resultado.get('success')}")
        
        if resultado and resultado.get("success"):
            logger.info(f"Webhook processado com sucesso: {resultado}")
            
            # Força o commit final para garantir que não haja rollback
            try:
                db.commit()
                logger.info("Commit final realizado com sucesso no webhook!")
            except Exception as commit_error:
                logger.error(f"Erro no commit final: {str(commit_error)}")
                db.rollback()
                raise HTTPException(
                    status_code=500,
                    detail=f"Erro ao finalizar processamento: {str(commit_error)}",
                )
            
            return {
                "success": True,
                "message": "Webhook processado com sucesso",
                "data": resultado,
            }
        else:
            error_msg = resultado.get('error', 'Erro desconhecido') if resultado else 'Resultado vazio ou None'
            logger.error(f"Erro ao processar webhook: {resultado}")
            logger.error(f"Mensagem de erro: {error_msg}")
            
            # Rollback em caso de erro
            try:
                db.rollback()
                logger.info("Rollback realizado devido a erro no processamento")
            except Exception as rollback_error:
                logger.error(f"Erro no rollback: {str(rollback_error)}")
            
            raise HTTPException(
                status_code=400,
                detail=f"Erro ao processar webhook: {error_msg}",
            )

    except Exception as e:
        logger.error(f"Erro ao processar webhook: {str(e)}")
        logger.error(f"Tipo do erro: {type(e).__name__}")
        logger.error(f"Traceback completo:", exc_info=True)
        
        # Rollback em caso de exceção
        try:
            db.rollback()
            logger.info("Rollback realizado devido a exceção")
        except Exception as rollback_error:
            logger.error(f"Erro no rollback: {str(rollback_error)}")
        
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
