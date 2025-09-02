"""
Serviço para processar webhooks do Botconversa.

Este serviço gerencia:
- Recebimento de webhooks
- Processamento de respostas dos pacientes
- Validação de dados
- Logging de eventos
"""

from datetime import datetime
from typing import Any, Dict, Optional

from loguru import logger
from sqlalchemy.orm import Session
from sqlalchemy import text

from app.database.models import (
    Atendimento,
    Confirmacao,
    Consulta,
    Paciente,
    StatusConfirmacao,
)

from .botconversa_service import BotconversaService


class WebhookService:
    """Serviço para processar webhooks do Botconversa"""

    def __init__(self, db: Session):
        self.db = db
        self.botconversa_service = BotconversaService(db)

    def processar_webhook(self, webhook_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Processa um webhook recebido do Botconversa.

        Args:
            webhook_data: Dados do webhook recebido

        Returns:
            Resultado do processamento
        """
        try:
            # Extrai dados do webhook
            webhook_type = webhook_data.get("type")

            if webhook_type == "message":
                return self._processar_mensagem(webhook_data)
            elif webhook_type == "status":
                return self._processar_status(webhook_data)
            else:
                logger.warning(f"Tipo de webhook não suportado: {webhook_type}")
                return {"success": False, "error": "Tipo de webhook não suportado"}

        except Exception as e:
            logger.error(f"Erro ao processar webhook: {str(e)}")
            return {"success": False, "error": str(e)}

    def _processar_mensagem(self, webhook_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Processa uma mensagem recebida via webhook.

        Args:
            webhook_data: Dados da mensagem

        Returns:
            Resultado do processamento
        """
        try:
            # Extrai dados da mensagem
            contact = webhook_data.get("contact", {})
            message = webhook_data.get("message", {})

            if not contact or not message:
                return {
                    "success": False,
                    "error": "Dados de contato ou mensagem ausentes",
                }

            # Extrai informações do contato
            phone = contact.get("phone", "").replace("+", "")
            full_name = contact.get("full_name", "")

            # Extrai conteúdo da mensagem
            content = message.get("content", "").strip()
            message_id = message.get("id", "")
            timestamp = message.get("timestamp", "")

            if not phone or not content:
                return {
                    "success": False,
                    "error": "Telefone ou conteúdo da mensagem ausentes",
                }

            logger.info(f"Processando mensagem de {phone}: {content}")

            # Processa a resposta do paciente
            success = self.botconversa_service.processar_resposta_paciente(
                phone, content
            )

            if success:
                return {
                    "success": True,
                    "message": "Resposta processada com sucesso",
                    "phone": phone,
                    "content": content,
                    "message_id": message_id,
                }
            else:
                return {
                    "success": False,
                    "error": "Erro ao processar resposta do paciente",
                }

        except Exception as e:
            logger.error(f"Erro ao processar mensagem: {str(e)}")
            return {"success": False, "error": str(e)}

    def _processar_status(self, webhook_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Processa um status recebido via webhook.

        Args:
            webhook_data: Dados do status

        Returns:
            Resultado do processamento
        """
        try:
            # Extrai dados do status
            status = webhook_data.get("status", "")
            contact = webhook_data.get("contact", {})

            if not status or not contact:
                return {
                    "success": False,
                    "error": "Dados de status ou contato ausentes",
                }

            phone = contact.get("phone", "").replace("+", "")

            logger.info(f"Processando status {status} para {phone}")

            # Por enquanto, apenas loga o status
            # Pode ser expandido para processar diferentes tipos de status
            return {
                "success": True,
                "message": "Status processado com sucesso",
                "status": status,
                "phone": phone,
            }

        except Exception as e:
            logger.error(f"Erro ao processar status: {str(e)}")
            return {"success": False, "error": str(e)}

    def validar_webhook(self, webhook_data: Dict[str, Any]) -> bool:
        """
        Valida os dados do webhook.

        Args:
            webhook_data: Dados do webhook

        Returns:
            True se válido, False caso contrário
        """
        try:
            # Verifica se tem os campos obrigatórios
            if "type" not in webhook_data:
                logger.error("Webhook sem tipo")
                return False

            webhook_type = webhook_data.get("type")

            if webhook_type == "message":
                # Valida dados da mensagem
                contact = webhook_data.get("contact", {})
                message = webhook_data.get("message", {})

                if not contact or not message:
                    logger.error("Webhook de mensagem sem dados de contato ou mensagem")
                    return False

                phone = contact.get("phone")
                content = message.get("content")

                if not phone or not content:
                    logger.error("Webhook de mensagem sem telefone ou conteúdo")
                    return False

            elif webhook_type == "status":
                # Valida dados do status
                status = webhook_data.get("status")
                contact = webhook_data.get("contact", {})

                if not status or not contact:
                    logger.error("Webhook de status sem dados de status ou contato")
                    return False

            else:
                logger.warning(f"Tipo de webhook não suportado: {webhook_type}")
                return False

            return True

        except Exception as e:
            logger.error(f"Erro ao validar webhook: {str(e)}")
            return False

    def registrar_webhook(
        self, webhook_data: Dict[str, Any], resultado: Dict[str, Any]
    ) -> None:
        """
        Registra o processamento do webhook no log.

        Args:
            webhook_data: Dados originais do webhook
            resultado: Resultado do processamento
        """
        try:
            # Extrai informações para log
            webhook_type = webhook_data.get("type", "unknown")
            contact = webhook_data.get("contact", {})
            phone = contact.get("phone", "unknown") if contact else "unknown"

            # Log do processamento
            if resultado.get("success"):
                logger.info(
                    f"Webhook {webhook_type} processado com sucesso para {phone}"
                )
            else:
                logger.error(
                    f"Erro ao processar webhook {webhook_type} para {phone}: {resultado.get('error')}"
                )

        except Exception as e:
            logger.error(f"Erro ao registrar webhook: {str(e)}")

    def processar_n8n_webhook(self, n8n_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Processa dados recebidos do N8N com respostas dos pacientes.

        Args:
            n8n_data: Dados do N8N com telefone, subscriber_id e resposta

        Returns:
            Resultado do processamento
        """
        try:
            # Extrai dados do N8N
            telefone = n8n_data.get("telefone")
            subscriber_id = n8n_data.get("subscriber_id")
            resposta = n8n_data.get("resposta")
            nome_paciente = n8n_data.get("nome_paciente")

            if not telefone or not subscriber_id or not resposta:
                return {
                    "success": False,
                    "error": "Telefone, subscriber_id ou resposta ausentes",
                }

            logger.info(
                f"Processando resposta N8N: {telefone} - {subscriber_id} - {resposta}"
            )

            # Busca atendimento por subscriber_id
            logger.info(f"🔍 Buscando atendimento para subscriber_id: {subscriber_id}")
            
            atendimento = (
                self.db.query(Atendimento)
                .filter(Atendimento.subscriber_id == subscriber_id)
                .first()
            )

            if not atendimento:
                logger.warning(
                    f"Atendimento não encontrado para subscriber_id: {subscriber_id}"
                )
                return {
                    "success": False,
                    "error": f"Atendimento não encontrado para subscriber_id: {subscriber_id}",
                }

            logger.info(f"✅ Atendimento encontrado: ID {atendimento.id} - {atendimento.nome_paciente} - {atendimento.data_consulta}")

            # Processa a resposta
            logger.info(f"Processando resposta: {resposta}")
            logger.info(f"Status atual do atendimento: {atendimento.status_confirmacao}")
            
            if resposta == "1":
                # Confirmação
                logger.info("Definindo status como CONFIRMADO")
                atendimento.status_confirmacao = StatusConfirmacao.CONFIRMADO
                mensagem_status = "CONFIRMADO"
                logger.info(f"Status definido: {atendimento.status_confirmacao}")
            elif resposta == "0":
                # Cancelamento
                logger.info("Definindo status como CANCELADO")
                atendimento.status_confirmacao = StatusConfirmacao.CANCELADO
                mensagem_status = "CANCELADO"
                logger.info(f"Status definido: {atendimento.status_confirmacao}")
            else:
                logger.warning(f"Resposta inválida: {resposta}")
                return {
                    "success": False,
                    "error": f"Resposta inválida: {resposta}. Esperado '1' ou '0'",
                }

            # Atualiza campos de controle
            logger.info("Atualizando campos de controle...")
            atendimento.respondido_em = datetime.now()
            atendimento.resposta_paciente = resposta
            atendimento.atualizado_em = datetime.now()
            logger.info(f"Campos atualizados. Status final: {atendimento.status_confirmacao}")

            # Salva no banco
            logger.info("Fazendo commit no banco...")
            logger.info(f"Status antes do commit: {atendimento.status_confirmacao}")
            logger.info(f"Status antes do commit (value): {atendimento.status_confirmacao.value if atendimento.status_confirmacao else 'None'}")
            
            # Força o flush para garantir que as mudanças sejam enviadas para o banco
            self.db.flush()
            logger.info("Flush realizado")
            
            # Faz o commit
            self.db.commit()
            logger.info("Commit realizado com sucesso!")
            
            #Chamar procedure Oracle para sincronizar com sistema legado
            try:
                logger.info(f"Chamando procedure Oracle para atendimento {atendimento.id}")
                logger.info(f"📅 Data/hora da consulta: {atendimento.data_consulta}")
                logger.info(f"👤 Nome do paciente: {atendimento.nome_paciente}")
                
                # Determina o status para a procedure
                status_procedure = "CONFIRMADO" if resposta == "1" else "CANCELADO"
                
                # Chama a procedure
                self.db.execute(
                    text("CALL ghas_prc_alt_status_age(:id_agenda_p, :status_p)"),
                    {
                        "id_agenda_p": atendimento.id,
                        "status_p": status_procedure
                    }
                )
                
                logger.info(f"Procedure Oracle executada com sucesso para atendimento {atendimento.id}")
                
            except Exception as proc_error:
                logger.error(f"Erro ao executar procedure Oracle: {str(proc_error)}")
                logger.warning("Atendimento foi salvo, mas procedure falhou - verificar manualmente")
                # Não faz rollback - atendimento já foi salvo com sucesso
            
            # Verifica se foi salvo
            self.db.refresh(atendimento)
            logger.info(f"Status após refresh: {atendimento.status_confirmacao}")
            logger.info(f"Status após refresh (value): {atendimento.status_confirmacao.value if atendimento.status_confirmacao else 'None'}")

            logger.info(
                f"Atendimento {atendimento.id} atualizado para {mensagem_status}"
            )

            return {
                "success": True,
                "message": f"Atendimento {mensagem_status} com sucesso",
                "atendimento_id": atendimento.id,
                "status": mensagem_status,
                "telefone": telefone,
                "subscriber_id": subscriber_id,
                "resposta": resposta,
            }

        except Exception as e:
            logger.error(f"Erro ao processar webhook N8N: {str(e)}")
            logger.error(f"Tipo do erro: {type(e).__name__}")
            logger.error("Traceback completo:", exc_info=True)
            
            # Rollback em caso de erro
            try:
                self.db.rollback()
                logger.info("Rollback realizado no WebhookService devido a erro")
            except Exception as rollback_error:
                logger.error(f"Erro no rollback do WebhookService: {str(rollback_error)}")
            
            return {"success": False, "error": str(e)}
