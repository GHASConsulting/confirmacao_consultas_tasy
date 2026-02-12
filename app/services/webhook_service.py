"""
Serviço para processar webhooks do Botconversa.

Este serviço gerencia:
- Recebimento de webhooks
- Processamento de respostas dos pacientes (incl. UPDATE em agenda_consulta por nr_sequencia)
- Validação de dados
- Logging de eventos
"""

from datetime import datetime
from typing import Any, Dict, Optional

from loguru import logger
from sqlalchemy.orm import Session

from app.database.models import (
    Atendimento,
    Confirmacao,
    Consulta,
    Paciente,
    StatusConfirmacao,
)
from app.database.sqlite_envios import get_sqlite_session
from app.services.agenda_consulta_update_service import atualizar_confirmacao_agenda_consulta
from app.services.envios_lembrete_service import (
    buscar_ultimo_envio_sem_resposta_por_telefone,
    registrar_resposta_envio,
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

        Aceita nr_sequencia no payload; se não vier, tenta obter do SQLite
        (último envio 48h/12h para aquele telefone sem resposta).
        Atualiza a tabela agenda_consulta (DT_CONFIRMACAO, DS_CONFIRMACAO)
        e registra a resposta no SQLite.
        """
        try:
            telefone = n8n_data.get("telefone")
            subscriber_id = n8n_data.get("subscriber_id")
            resposta = n8n_data.get("resposta")
            nome_paciente = n8n_data.get("nome_paciente")
            nr_sequencia = n8n_data.get("nr_sequencia")  # opcional
            nr_sequencia_agenda = n8n_data.get("nr_sequencia_agenda")  # opcional; cd_agenda para UPDATE

            if not telefone or not subscriber_id or not resposta:
                return {
                    "success": False,
                    "error": "Telefone, subscriber_id ou resposta ausentes",
                }

            if resposta not in ("1", "0"):
                return {
                    "success": False,
                    "error": "Resposta inválida. Esperado '1' (sim) ou '0' (não)",
                }

            confirmado = resposta == "1"
            mensagem_status = "CONFIRMADO" if confirmado else "CANCELADO"

            logger.info(
                f"Processando resposta N8N: telefone={telefone}, nr_sequencia={nr_sequencia}, "
                f"nr_sequencia_agenda={nr_sequencia_agenda}, resposta={resposta}"
            )

            # Obter nr_sequencia e cd_agenda: do payload ou do SQLite (último envio sem resposta)
            cd_agenda = nr_sequencia_agenda  # payload pode trazer nr_sequencia_agenda
            if nr_sequencia is None or cd_agenda is None:
                sqlite_session = get_sqlite_session()
                try:
                    envio = buscar_ultimo_envio_sem_resposta_por_telefone(
                        sqlite_session, telefone
                    )
                    if envio:
                        if nr_sequencia is None:
                            nr_sequencia = envio.nr_sequencia
                            logger.info(f"nr_sequencia obtido do SQLite: {nr_sequencia}")
                        if cd_agenda is None and getattr(envio, "cd_agenda", None) is not None:
                            cd_agenda = envio.cd_agenda
                            logger.info(f"cd_agenda (nr_sequencia_agenda) obtido do SQLite: {cd_agenda}")
                finally:
                    sqlite_session.close()

            # Atualizar agenda_consulta no banco principal (por cd_agenda para não alterar agenda errada)
            if cd_agenda is not None:
                atualizar_confirmacao_agenda_consulta(
                    self.db, cd_agenda, confirmado
                )
            else:
                logger.warning(
                    "nr_sequencia_agenda/cd_agenda ausente no payload e no SQLite; "
                    "agenda_consulta não atualizada (evitar alterar agenda errada)"
                )

            # Registrar resposta no SQLite (por nr_sequencia), quando tivermos nr_sequencia
            if nr_sequencia is not None:
                sqlite_session = get_sqlite_session()
                try:
                    registrar_resposta_envio(sqlite_session, nr_sequencia, resposta)
                finally:
                    sqlite_session.close()

            # Sucesso se atualizamos a agenda (cd_agenda) e/ou registramos resposta (nr_sequencia)
            if cd_agenda is not None or nr_sequencia is not None:
                return {
                    "success": True,
                    "message": f"Confirmação registrada: {mensagem_status}",
                    "nr_sequencia": nr_sequencia,
                    "nr_sequencia_agenda": cd_agenda,
                    "status": mensagem_status,
                    "telefone": telefone,
                    "subscriber_id": subscriber_id,
                    "resposta": resposta,
                }

            # Fallback: fluxo antigo por subscriber_id (tabela Atendimento)
            atendimento = (
                self.db.query(Atendimento)
                .filter(Atendimento.subscriber_id == subscriber_id)
                .first()
            )
            if not atendimento:
                return {
                    "success": False,
                    "error": "Nenhum nr_sequencia (payload ou SQLite) e atendimento não encontrado para subscriber_id",
                }

            if confirmado:
                atendimento.status = StatusConfirmacao.CONFIRMADO
            else:
                atendimento.status = StatusConfirmacao.CANCELADO
            atendimento.respondido_em = datetime.now()
            atendimento.resposta_paciente = resposta
            atendimento.atualizado_em = datetime.now()
            self.db.commit()

            return {
                "success": True,
                "message": f"Atendimento {mensagem_status} (fluxo legado)",
                "atendimento_id": atendimento.id,
                "status": mensagem_status,
                "telefone": telefone,
                "subscriber_id": subscriber_id,
                "resposta": resposta,
            }

        except Exception as e:
            logger.error(f"Erro ao processar webhook N8N: {str(e)}")
            self.db.rollback()
            return {"success": False, "error": str(e)}
