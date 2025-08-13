"""
Scheduler para automação de envio de mensagens e lembretes.

Este módulo gerencia:
- Monitoramento automático de novos atendimentos (a cada 30 minutos)
- Envio automático de confirmações 72h antes da consulta
- Lembretes automáticos para consultas não confirmadas
- Agendamento inteligente de tarefas
"""

from datetime import datetime, timedelta
from typing import Optional

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from apscheduler.triggers.interval import IntervalTrigger
from loguru import logger

from app.config.config import settings


class AppointmentScheduler:
    """
    Scheduler para automação de consultas médicas.

    Jobs implementados:
    1. Monitoramento de novos atendimentos (a cada 30 min)
    2. Verificação de confirmações (72h antes)
    3. Verificação de lembretes (48h e 12h antes)
    """

    def __init__(self):
        """Inicializa o scheduler"""
        self.scheduler = BackgroundScheduler()
        self.is_running = False

        # Configurações do scheduler
        self.scheduler.configure(
            job_defaults={
                "coalesce": True,  # Agrupa jobs similares
                "max_instances": 1,  # Máximo 1 instância por job
                "misfire_grace_time": 300,  # 5 minutos de tolerância
            }
        )

    def start(self):
        """Inicia o scheduler"""
        try:
            if not self.is_running:
                self.scheduler.start()
                self.is_running = True
                logger.info("Scheduler iniciado com sucesso")

                # Adiciona os jobs básicos
                self._adicionar_jobs_basicos()

        except Exception as e:
            logger.error(f"Erro ao iniciar scheduler: {str(e)}")
            raise e

    def stop(self):
        """Para o scheduler"""
        try:
            if self.is_running:
                self.scheduler.shutdown()
                self.is_running = False
                logger.info("Scheduler parado com sucesso")
        except Exception as e:
            logger.error(f"Erro ao parar scheduler: {str(e)}")

    def _adicionar_jobs_basicos(self):
        """Adiciona os jobs básicos ao scheduler baseado nas configurações do .env"""
        try:
            # Job 1: Verificar consultas para confirmação (configurável via .env)
            if settings.scheduler_enable_confirmation_job:
                self.scheduler.add_job(
                    func=self._job_verificar_confirmacoes,
                    trigger=CronTrigger(
                        hour=settings.scheduler_confirmation_hour,
                        minute=settings.scheduler_confirmation_minute,
                    ),
                    id="verificar_confirmacoes",
                    name=f"Verificar consultas para confirmação (às {settings.scheduler_confirmation_hour:02d}:{settings.scheduler_confirmation_minute:02d})",
                    replace_existing=True,
                )
                logger.info(
                    f"Job de confirmação agendado para {settings.scheduler_confirmation_hour:02d}:{settings.scheduler_confirmation_minute:02d}"
                )
            else:
                logger.info("Job de confirmação desabilitado via configuração")

            # Job 2: Verificar lembretes (configurável via .env)
            if settings.scheduler_enable_reminder_job:
                self.scheduler.add_job(
                    func=self._job_verificar_lembretes,
                    trigger=CronTrigger(
                        hour=settings.scheduler_reminder_hour,
                        minute=settings.scheduler_reminder_minute,
                    ),
                    id="verificar_lembretes",
                    name=f"Verificar lembretes pendentes (às {settings.scheduler_reminder_hour:02d}:{settings.scheduler_reminder_minute:02d})",
                    replace_existing=True,
                )
                logger.info(
                    f"Job de lembretes agendado para {settings.scheduler_reminder_hour:02d}:{settings.scheduler_reminder_minute:02d}"
                )
            else:
                logger.info("Job de lembretes desabilitado via configuração")

            # Job 3: Monitorar novos atendimentos (NOVO - executa a cada 30 minutos)
            self.scheduler.add_job(
                func=self._job_monitorar_novos_atendimentos,
                trigger=IntervalTrigger(minutes=30),  # A cada 30 minutos
                id="monitorar_novos_atendimentos",
                name="Monitorar novos atendimentos e executar workflow completo",
                replace_existing=True,
            )
            logger.info(
                "Job de monitoramento de novos atendimentos agendado (a cada 30 minutos)"
            )

            logger.info("Jobs básicos configurados com base nas configurações do .env")

        except Exception as e:
            logger.error(f"Erro ao adicionar jobs básicos: {str(e)}")

    def _job_verificar_confirmacoes(self):
        """
        Job para verificar consultas que precisam de confirmação.

        Este job roda diariamente às 9h e identifica consultas que estão
        a 72h de acontecer e precisam de confirmação.
        """
        try:
            logger.info("Executando job: verificar confirmações")

            # Importa o serviço do Botconversa
            from datetime import datetime, timedelta

            from app.database.manager import get_db
            from app.database.models import Atendimento, StatusConfirmacao
            from app.services.botconversa_service import BotconversaService

            # Obtém uma sessão do banco
            db = next(get_db())
            botconversa_service = BotconversaService(db)

            try:
                # Calcula a data limite (72h a partir de agora)
                data_limite = datetime.now() + timedelta(
                    hours=settings.confirmation_window_hours
                )

                # Busca consultas que estão a 72h de acontecer e ainda não foram enviadas
                consultas_para_confirmar = (
                    db.query(Atendimento)
                    .filter(
                        Atendimento.data_consulta <= data_limite,
                        Atendimento.data_consulta > datetime.now(),
                        Atendimento.status == StatusConfirmacao.PENDENTE,
                        Atendimento.subscriber_id.isnot(
                            None
                        ),  # Tem subscriber no Botconversa
                        Atendimento.mensagem_enviada.is_(
                            None
                        ),  # Mensagem ainda não foi enviada
                    )
                    .order_by(Atendimento.data_consulta.asc())
                    .all()
                )

                logger.info(
                    f"Encontradas {len(consultas_para_confirmar)} consultas para confirmação"
                )

                # Processa cada consulta
                for consulta in consultas_para_confirmar:
                    try:
                        logger.info(
                            f"Processando consulta {consulta.id} para {consulta.nome_paciente}"
                        )

                        # Envia mensagem de confirmação
                        sucesso = botconversa_service.enviar_mensagem_consulta(consulta)

                        if sucesso:
                            logger.info(
                                f"Mensagem de confirmação enviada para {consulta.nome_paciente}"
                            )
                        else:
                            logger.error(
                                f"Erro ao enviar mensagem para {consulta.nome_paciente}"
                            )

                    except Exception as e:
                        logger.error(
                            f"Erro ao processar consulta {consulta.id}: {str(e)}"
                        )
                        continue

                logger.info(
                    f"Job de confirmações concluído: {len(consultas_para_confirmar)} consultas processadas"
                )

            finally:
                db.close()

        except Exception as e:
            logger.error(f"Erro no job de confirmações: {str(e)}")

    def _job_verificar_lembretes(self):
        """
        Job para verificar lembretes pendentes.

        Este job roda diariamente às 14h e identifica consultas que
        precisam de lembretes (48h e 12h antes).
        """
        try:
            logger.info("Executando job: verificar lembretes")

            # Importa o serviço do Botconversa
            from datetime import datetime, timedelta

            from app.database.manager import get_db
            from app.database.models import Atendimento, StatusConfirmacao
            from app.services.botconversa_service import BotconversaService

            # Obtém uma sessão do banco
            db = next(get_db())
            botconversa_service = BotconversaService(db)

            try:
                # Calcula as datas para lembretes
                agora = datetime.now()
                lembrete_48h = agora + timedelta(hours=48)
                lembrete_12h = agora + timedelta(hours=12)

                # Busca consultas que precisam de lembretes
                consultas_para_lembrete = (
                    db.query(Atendimento)
                    .filter(
                        Atendimento.status == StatusConfirmacao.PENDENTE,
                        Atendimento.subscriber_id.isnot(
                            None
                        ),  # Tem subscriber no Botconversa
                        Atendimento.mensagem_enviada.isnot(
                            None
                        ),  # Mensagem inicial já foi enviada
                        Atendimento.resposta_paciente.is_(
                            None
                        ),  # Paciente ainda não respondeu
                    )
                    .order_by(Atendimento.data_consulta.asc())
                    .all()
                )

                logger.info(
                    f"Encontradas {len(consultas_para_lembrete)} consultas para lembretes"
                )

                # Processa cada consulta
                for consulta in consultas_para_lembrete:
                    try:
                        # Verifica se está na janela de lembrete
                        if (
                            consulta.data_consulta <= lembrete_48h
                            and consulta.data_consulta > agora
                        ):
                            # Lembrete 48h antes
                            if self._pode_enviar_lembrete(consulta, "48h"):
                                logger.info(
                                    f"Enviando lembrete 48h para {consulta.nome_paciente}"
                                )
                                self._enviar_lembrete(
                                    botconversa_service, consulta, "48h", db
                                )

                        elif (
                            consulta.data_consulta <= lembrete_12h
                            and consulta.data_consulta > agora
                        ):
                            # Lembrete 12h antes
                            if self._pode_enviar_lembrete(consulta, "12h"):
                                logger.info(
                                    f"Enviando lembrete 12h para {consulta.nome_paciente}"
                                )
                                self._enviar_lembrete(
                                    botconversa_service, consulta, "12h", db
                                )

                        elif consulta.data_consulta <= agora:
                            # Consulta passou sem confirmação
                            logger.info(
                                f"Marcando consulta {consulta.id} como SEM_RESPOSTA"
                            )
                            consulta.status = StatusConfirmacao.SEM_RESPOSTA
                            consulta.atualizado_em = agora
                            db.commit()

                    except Exception as e:
                        logger.error(
                            f"Erro ao processar lembrete para consulta {consulta.id}: {str(e)}"
                        )
                        continue

                logger.info(
                    f"Job de lembretes concluído: {len(consultas_para_lembrete)} consultas processadas"
                )

            finally:
                db.close()

        except Exception as e:
            logger.error(f"Erro no job de lembretes: {str(e)}")

    def _job_monitorar_novos_atendimentos(self):
        """
        Job para monitorar novos atendimentos e executar workflow completo.

        Este job roda a cada 30 minutos e identifica atendimentos que:
        - Não têm subscriber_id (não foram processados pelo Botconversa)
        - Precisam do workflow completo executado
        """
        try:
            logger.info("Executando job: monitorar novos atendimentos")

            # Importa o serviço do Botconversa
            from datetime import datetime

            from app.database.manager import get_db
            from app.database.models import Atendimento, StatusConfirmacao
            from app.services.botconversa_service import BotconversaService

            # Obtém uma sessão do banco
            db = next(get_db())
            botconversa_service = BotconversaService(db)

            try:
                # Busca atendimentos que não foram processados pelo Botconversa
                novos_atendimentos = (
                    db.query(Atendimento)
                    .filter(
                        Atendimento.subscriber_id.is_(None),  # Não tem subscriber_id
                        Atendimento.status
                        == StatusConfirmacao.PENDENTE,  # Status pendente
                        Atendimento.data_consulta
                        > datetime.now(),  # Consulta no futuro
                    )
                    .order_by(
                        Atendimento.criado_em.asc()
                    )  # Processa os mais antigos primeiro
                    .all()
                )

                logger.info(
                    f"Encontrados {len(novos_atendimentos)} novos atendimentos para processar"
                )

                # Processa cada novo atendimento
                for atendimento in novos_atendimentos:
                    try:
                        logger.info(
                            f"Processando novo atendimento {atendimento.id} para {atendimento.nome_paciente}"
                        )

                        # Executa o workflow completo
                        sucesso = self._executar_workflow_completo(
                            botconversa_service, atendimento, db
                        )

                        if sucesso:
                            logger.info(
                                f"Workflow completo executado com sucesso para {atendimento.nome_paciente}"
                            )
                        else:
                            logger.error(
                                f"Erro ao executar workflow para {atendimento.nome_paciente}"
                            )

                    except Exception as e:
                        logger.error(
                            f"Erro ao processar atendimento {atendimento.id}: {str(e)}"
                        )
                        continue

                logger.info(
                    f"Job de monitoramento concluído: {len(novos_atendimentos)} atendimentos processados"
                )

            finally:
                db.close()

        except Exception as e:
            logger.error(f"Erro no job de monitoramento: {str(e)}")

    def _executar_workflow_completo(self, botconversa_service, atendimento, db) -> bool:
        """
        Executa o workflow completo para um novo atendimento.

        Args:
            botconversa_service: Serviço do Botconversa
            atendimento: Objeto Atendimento
            db: Sessão do banco de dados

        Returns:
            True se executado com sucesso, False caso contrário
        """
        try:
            from datetime import datetime

            from app.database.models import StatusConfirmacao

            logger.info(f"Iniciando workflow completo para {atendimento.nome_paciente}")

            # PASSO 1: Criar subscriber no Botconversa
            logger.info(f"PASSO 1: Criando subscriber para {atendimento.nome_paciente}")
            subscriber_id = botconversa_service.criar_subscriber(
                atendimento.nome_paciente, atendimento.telefone
            )

            if not subscriber_id:
                logger.error(
                    f"Falha ao criar subscriber para {atendimento.nome_paciente}"
                )
                return False

            logger.info(f"Subscriber criado com ID: {subscriber_id}")

            # PASSO 2: Adicionar à campanha "Confirmação de Consultas"
            logger.info(f"PASSO 2: Adicionando à campanha")
            sucesso_campanha = botconversa_service.adicionar_subscriber_campanha(
                subscriber_id,
                campaign_id=289860,  # ID da campanha "Confirmação de Consultas"
            )

            if not sucesso_campanha:
                logger.error(
                    f"Falha ao adicionar à campanha: {atendimento.nome_paciente}"
                )
                # Continua mesmo assim, pois a mensagem pode ser enviada

            # PASSO 3: Enviar mensagem de confirmação
            logger.info(f"PASSO 3: Enviando mensagem de confirmação")
            sucesso_mensagem = botconversa_service.enviar_mensagem_consulta(atendimento)

            if not sucesso_mensagem:
                logger.error(
                    f"Falha ao enviar mensagem para {atendimento.nome_paciente}"
                )
                return False

            # PASSO 4: Enviar fluxo interativo
            logger.info(f"PASSO 4: Enviando fluxo interativo")
            sucesso_fluxo = botconversa_service.enviar_fluxo(subscriber_id)

            if not sucesso_fluxo:
                logger.warning(
                    f"Fluxo não enviado para {atendimento.nome_paciente}, mas continuando"
                )

            # PASSO 5: Atualizar banco de dados
            logger.info(f"PASSO 5: Atualizando banco de dados")
            atendimento.subscriber_id = subscriber_id
            atendimento.mensagem_enviada = "Workflow completo executado automaticamente"
            atendimento.atualizado_em = datetime.now()
            atendimento.status_confirmacao = StatusConfirmacao.PENDENTE

            # Commit das alterações
            db.commit()

            logger.info(
                f"Workflow completo executado com sucesso para {atendimento.nome_paciente}"
            )
            return True

        except Exception as e:
            logger.error(f"Erro ao executar workflow completo: {str(e)}")
            # Rollback em caso de erro
            try:
                db.rollback()
            except:
                pass
            return False

    def _pode_enviar_lembrete(self, consulta, tipo_lembrete: str) -> bool:
        """
        Verifica se pode enviar um lembrete para uma consulta.

        Args:
            consulta: Objeto Atendimento
            tipo_lembrete: Tipo do lembrete ("48h" ou "12h")

        Returns:
            True se pode enviar, False caso contrário
        """
        try:
            from datetime import datetime, timedelta

            # Verifica se o lembrete deste tipo já foi enviado
            if tipo_lembrete == "48h" and consulta.lembrete_48h_enviado:
                logger.info(f"Lembrete 48h já foi enviado para consulta {consulta.id}")
                return False

            if tipo_lembrete == "12h" and consulta.lembrete_12h_enviado:
                logger.info(f"Lembrete 12h já foi enviado para consulta {consulta.id}")
                return False

            # Verifica se há um lembrete recente (evita spam)
            if consulta.ultimo_lembrete_enviado:
                tempo_desde_ultimo = datetime.now() - consulta.ultimo_lembrete_enviado
                if tempo_desde_ultimo < timedelta(hours=24):
                    logger.info(
                        f"Lembrete enviado há menos de 24h para consulta {consulta.id}"
                    )
                    return False

            # Pode enviar o lembrete
            return True

        except Exception as e:
            logger.error(f"Erro ao verificar se pode enviar lembrete: {str(e)}")
            return False

    def _enviar_lembrete(
        self, botconversa_service, consulta, tipo_lembrete: str, db
    ) -> bool:
        """
        Envia um lembrete para uma consulta.

        Args:
            botconversa_service: Serviço do Botconversa
            consulta: Objeto Atendimento
            tipo_lembrete: Tipo do lembrete ("48h" ou "12h")
            db: Sessão do banco de dados

        Returns:
            True se enviado com sucesso, False caso contrário
        """
        try:
            from datetime import datetime

            from app.config.config import settings

            # Formata a data da consulta
            data_formatada = consulta.data_consulta.strftime("%d/%m/%Y")
            hora_formatada = consulta.data_consulta.strftime("%H:%M")

            # Obtém as configurações do hospital
            hospital_name = settings.hospital_name or "Santa Casa de Belo Horizonte"
            hospital_phone = settings.hospital_phone or "(31) 3238-8100"

            # Cria mensagem de lembrete baseada no tipo
            if tipo_lembrete == "48h":
                mensagem = f"""🔔 **LEMBRETE IMPORTANTE**, {consulta.nome_paciente}!

        Sua consulta está marcada para **AMANHÃ**:
        📅 {data_formatada} às {hora_formatada}
        👨‍⚕️ Dr. {consulta.nome_medico}
        🏥 {consulta.especialidade}

        Por favor, confirme sua presença:
        ✅ SIM - Vou comparecer
        ❌ NÃO - Preciso cancelar

        📞 Para dúvidas: {hospital_phone}"""

            elif tipo_lembrete == "12h":
                mensagem = f"""⚠️ **ÚLTIMO LEMBRETE**, {consulta.nome_paciente}!

        Sua consulta é **HOJE** às {hora_formatada}:
        👨‍⚕️ Dr. {consulta.nome_medico}
        🏥 {consulta.especialidade}

        Confirme sua presença AGORA:
        ✅ SIM - Vou comparecer
        ❌ NÃO - Preciso cancelar

        📞 Para dúvidas: {hospital_phone}"""

            else:
                logger.error(f"Tipo de lembrete inválido: {tipo_lembrete}")
                return False

            # Envia a mensagem
            sucesso = botconversa_service.enviar_mensagem(
                consulta.subscriber_id, mensagem
            )

            if sucesso:
                # Atualiza o atendimento com informação do lembrete e controle de frequência
                consulta.mensagem_enviada = f"Lembrete {tipo_lembrete}: {mensagem}"
                consulta.atualizado_em = datetime.now()

                # Marca o lembrete como enviado
                if tipo_lembrete == "48h":
                    consulta.lembrete_48h_enviado = True
                elif tipo_lembrete == "12h":
                    consulta.lembrete_12h_enviado = True

                # Atualiza informações do último lembrete
                consulta.ultimo_lembrete_enviado = datetime.now()
                consulta.tipo_ultimo_lembrete = tipo_lembrete

                # Commit das alterações
                db.commit()

                logger.info(
                    f"Lembrete {tipo_lembrete} enviado para {consulta.nome_paciente}"
                )
                return True
            else:
                logger.error(
                    f"Erro ao enviar lembrete {tipo_lembrete} para {consulta.nome_paciente}"
                )
                return False

        except Exception as e:
            logger.error(f"Erro ao enviar lembrete {tipo_lembrete}: {str(e)}")
            return False

    def get_status(self) -> dict:
        """Retorna o status atual do scheduler"""
        try:
            jobs = self.scheduler.get_jobs()
            job_details = []

            for job in jobs:
                job_details.append(
                    {
                        "id": job.id,
                        "name": job.name,
                        "next_run": (
                            job.next_run_time.isoformat() if job.next_run_time else None
                        ),
                        "trigger": str(job.trigger),
                    }
                )

            return {
                "is_running": self.is_running,
                "jobs_count": len(jobs),
                "jobs": job_details,
                "next_run_time": self._get_next_run_time(),
                "monitoring_enabled": any(
                    job.id == "monitorar_novos_atendimentos" for job in jobs
                ),
                "confirmation_enabled": any(
                    job.id == "verificar_confirmacoes" for job in jobs
                ),
                "reminder_enabled": any(
                    job.id == "verificar_lembretes" for job in jobs
                ),
            }
        except Exception as e:
            logger.error(f"Erro ao obter status do scheduler: {str(e)}")
            return {"is_running": self.is_running, "jobs_count": 0, "error": str(e)}

    def _get_next_run_time(self) -> Optional[str]:
        """Retorna a próxima execução programada"""
        try:
            jobs = self.scheduler.get_jobs()
            if jobs:
                next_job = min(jobs, key=lambda x: x.next_run_time)
                return (
                    next_job.next_run_time.isoformat()
                    if next_job.next_run_time
                    else None
                )
            return None
        except Exception as e:
            logger.error(f"Erro ao obter próxima execução: {str(e)}")
            return None


# Instância global do scheduler
scheduler = AppointmentScheduler()


def iniciar_scheduler():
    """Função para iniciar o scheduler"""
    try:
        scheduler.start()
        return True
    except Exception as e:
        logger.error(f"Erro ao iniciar scheduler: {str(e)}")
        return False


def parar_scheduler():
    """Função para parar o scheduler"""
    try:
        scheduler.stop()
        return True
    except Exception as e:
        logger.error(f"Erro ao parar scheduler: {str(e)}")
        return False


def obter_status_scheduler() -> dict:
    """Função para obter status do scheduler"""
    return scheduler.get_status()
