"""
Serviço para o SQLite de envios de lembrete (48h e 12h).

- Consulta quem já foi enviado (por nr_sequencia e tipo).
- Insere novo envio após enviar via Botconversa.
- Lista registros 48h que entram na janela de 12h e ainda não têm 12h enviado.
"""

from datetime import datetime, timedelta
from typing import List, Set

from loguru import logger
from sqlalchemy import and_, select
from sqlalchemy.orm import Session

from app.database.sqlite_envios import EnvioLembrete
from app.utils.telefone import normalizar_telefone


def nr_sequencias_ja_enviados_48h(session: Session) -> Set[int]:
    """Retorna set de nr_sequencia que já tiveram lembrete 48H enviado."""
    try:
        result = session.execute(
            select(EnvioLembrete.nr_sequencia).where(
                EnvioLembrete.tipo_lembrete == "48H"
            )
        )
        return {r[0] for r in result.fetchall()}
    except Exception as e:
        logger.error(f"Erro ao listar já enviados 48h: {e}")
        return set()


def registrar_envio_48h(
    session: Session,
    nr_sequencia: int,
    dt_agenda: datetime | None,
    nr_telefone: str | None,
    nm_paciente: str | None,
    nr_ddi: str | None = None,
    nm_medico_externo: str | None = None,
    cd_agenda: int | None = None,
) -> None:
    """Registra envio de lembrete 48H no SQLite."""
    try:
        env = EnvioLembrete(
            nr_sequencia=nr_sequencia,
            cd_agenda=cd_agenda,
            tipo_lembrete="48H",
            enviado_em=datetime.utcnow(),
            dt_agenda=dt_agenda,
            nr_telefone=nr_telefone,
            nm_paciente=nm_paciente,
            nr_ddi=nr_ddi,
            nm_medico_externo=nm_medico_externo,
        )
        session.add(env)
        session.commit()
        logger.info(f"Registrado envio 48H nr_sequencia={nr_sequencia}")
    except Exception as e:
        logger.error(f"Erro ao registrar envio 48H: {e}")
        session.rollback()
        raise


def nr_sequencias_ja_enviados_12h(session: Session) -> Set[int]:
    """Retorna set de nr_sequencia que já tiveram lembrete 12H enviado."""
    try:
        result = session.execute(
            select(EnvioLembrete.nr_sequencia).where(
                EnvioLembrete.tipo_lembrete == "12H"
            )
        )
        return {r[0] for r in result.fetchall()}
    except Exception as e:
        logger.error(f"Erro ao listar já enviados 12h: {e}")
        return set()


def listar_para_lembrete_12h(
    session: Session,
    horas_janela: int = 12,
) -> List[EnvioLembrete]:
    """
    Lista registros que já receberam 48H, estão na janela de 12h e ainda não receberam 12H.

    Janela: dt_agenda entre agora e agora + horas_janela.
    """
    agora = datetime.utcnow()
    limite = agora + timedelta(hours=horas_janela)
    try:
        ja_12h = nr_sequencias_ja_enviados_12h(session)
        result = (
            session.query(EnvioLembrete)
            .where(
                and_(
                    EnvioLembrete.tipo_lembrete == "48H",
                    EnvioLembrete.dt_agenda.isnot(None),
                    EnvioLembrete.dt_agenda >= agora,
                    EnvioLembrete.dt_agenda <= limite,
                )
            )
            .order_by(EnvioLembrete.dt_agenda.asc())
            .all()
        )
        # Excluir os que já receberam 12H
        if ja_12h:
            result = [r for r in result if r.nr_sequencia not in ja_12h]
        logger.info(f"Lembretes 12h a enviar: {len(result)}")
        return result
    except Exception as e:
        logger.error(f"Erro ao listar para lembrete 12h: {e}")
        return []


def buscar_ultimo_envio_sem_resposta_por_telefone(
    session: Session, telefone: str
) -> EnvioLembrete | None:
    """
    Retorna o envio mais recente (48H ou 12H) para este telefone que ainda não tem resposta.
    Usado pelo webhook para obter nr_sequencia quando não vem no payload.
    """
    try:
        tel_norm = normalizar_telefone(telefone)
        if not tel_norm:
            return None
        # Busca por nr_telefone normalizado (só dígitos) para aceitar qualquer formatação
        todos = (
            session.query(EnvioLembrete)
            .where(EnvioLembrete.dt_resposta.is_(None))
            .order_by(EnvioLembrete.enviado_em.desc())
            .all()
        )
        for env in todos:
            if normalizar_telefone(env.nr_telefone) == tel_norm:
                return env
        return None
    except Exception as e:
        logger.error(f"Erro ao buscar envio sem resposta por telefone: {e}")
        return None


def registrar_resposta_envio(
    session: Session, nr_sequencia: int, resposta: str
) -> None:
    """Marca o envio como respondido (resposta 1 ou 0)."""
    try:
        from datetime import datetime

        env = (
            session.query(EnvioLembrete)
            .where(EnvioLembrete.nr_sequencia == nr_sequencia)
            .order_by(EnvioLembrete.enviado_em.desc())
            .first()
        )
        if env:
            env.resposta_paciente = resposta
            env.dt_resposta = datetime.utcnow()
            session.commit()
            logger.info(f"Resposta registrada para nr_sequencia={nr_sequencia}")
    except Exception as e:
        logger.error(f"Erro ao registrar resposta do envio: {e}")
        session.rollback()
        raise


def registrar_envio_12h(
    session: Session,
    nr_sequencia: int,
    dt_agenda: datetime | None,
    nr_telefone: str | None,
    nm_paciente: str | None,
    nr_ddi: str | None = None,
    nm_medico_externo: str | None = None,
    cd_agenda: int | None = None,
) -> None:
    """Registra envio de lembrete 12H no SQLite."""
    try:
        env = EnvioLembrete(
            nr_sequencia=nr_sequencia,
            cd_agenda=cd_agenda,
            tipo_lembrete="12H",
            enviado_em=datetime.utcnow(),
            dt_agenda=dt_agenda,
            nr_telefone=nr_telefone,
            nm_paciente=nm_paciente,
            nr_ddi=nr_ddi,
            nm_medico_externo=nm_medico_externo,
        )
        session.add(env)
        session.commit()
        logger.info(f"Registrado envio 12H nr_sequencia={nr_sequencia}")
    except Exception as e:
        logger.error(f"Erro ao registrar envio 12H: {e}")
        session.rollback()
        raise
