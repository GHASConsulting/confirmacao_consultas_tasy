"""
Orquestração dos lembretes 48h e 12h: view + SQLite + Botconversa.

- 48h: lê da view → compara com SQLite → envia → grava no SQLite.
- 12h: lê só do SQLite (quem já recebeu 48h e está na janela 12h) → envia → grava 12h no SQLite.
"""

from datetime import datetime, timedelta
from typing import Optional

from loguru import logger
from sqlalchemy.orm import Session

from app.config.config import settings
from app.database.manager import get_db
from app.database.sqlite_envios import get_sqlite_session
from app.services.botconversa_service import BotconversaService
from app.services.envios_lembrete_service import (
    listar_para_lembrete_12h,
    nr_sequencias_ja_enviados_48h,
    registrar_envio_48h,
    registrar_envio_12h,
)
from app.services.view_confirmacao_service import listar_view_confirmacao_48h
from app.utils.telefone import telefone_para_envio


def _mensagem_lembrete_48h(nome: str, dt_agenda: Optional[datetime], medico: Optional[str]) -> str:
    hospital_phone = settings.hospital_phone or "(31) 3238-8100"
    data_fmt = dt_agenda.strftime("%d/%m/%Y") if dt_agenda else ""
    hora_fmt = dt_agenda.strftime("%H:%M") if dt_agenda else ""
    medico_txt = f"Dr. {medico}" if medico else "médico"
    return f"""🔔 **LEMBRETE IMPORTANTE**, {nome or 'Paciente'}!

Sua consulta está marcada para **AMANHÃ**:
📅 {data_fmt} às {hora_fmt}
👨‍⚕️ {medico_txt}

Por favor, confirme sua presença:
✅ SIM - Vou comparecer
❌ NÃO - Preciso cancelar

📞 Para dúvidas: {hospital_phone}"""


def _mensagem_lembrete_12h(nome: str, dt_agenda: Optional[datetime], medico: Optional[str]) -> str:
    hospital_phone = settings.hospital_phone or "(31) 3238-8100"
    hora_fmt = dt_agenda.strftime("%H:%M") if dt_agenda else ""
    medico_txt = f"Dr. {medico}" if medico else "médico"
    return f"""⚠️ **ÚLTIMO LEMBRETE**, {nome or 'Paciente'}!

Sua consulta é **HOJE** às {hora_fmt}:
👨‍⚕️ {medico_txt}

Confirme sua presença AGORA:
✅ SIM - Vou comparecer
❌ NÃO - Preciso cancelar

📞 Para dúvidas: {hospital_phone}"""


def _na_janela_48h(dt: Optional[datetime], horas_min: int = 36, horas_max: int = 50) -> bool:
    """True se dt está na janela de lembrete 48h (entre horas_min e horas_max à frente)."""
    if not dt:
        return False
    # Considera dt sem timezone; compara com now local
    agora = datetime.now()
    limite_inf = agora + timedelta(hours=horas_min)
    limite_sup = agora + timedelta(hours=horas_max)
    return limite_inf <= dt <= limite_sup


def executar_job_lembretes_48h() -> None:
    """
    Job 48h: view → filtrar janela 48h → diff SQLite → enviar → gravar no SQLite.
    """
    db_main = next(get_db())
    sqlite_session = get_sqlite_session()
    bot = BotconversaService(db_main)
    try:
        linhas_view = listar_view_confirmacao_48h(db_main)
        # Só processar quem está na janela de 48h (evita enviar para consulta daqui a 7 dias)
        na_janela = [r for r in linhas_view if _na_janela_48h(r.dt_agenda or r.dt_consulta)]
        ja_48h = nr_sequencias_ja_enviados_48h(sqlite_session)
        a_enviar = [r for r in na_janela if r.nr_sequencia not in ja_48h]
        logger.info(
            f"Lembretes 48h: view={len(linhas_view)}, na_janela_48h={len(na_janela)}, "
            f"já enviados={len(ja_48h)}, a enviar={len(a_enviar)}"
        )
        for row in a_enviar:
            telefone = telefone_para_envio(row.nr_telefone, row.nr_ddi)
            if not telefone:
                logger.warning(f"nr_sequencia={row.nr_sequencia} sem telefone, ignorando")
                continue
            mensagem = _mensagem_lembrete_48h(
                row.nm_paciente, row.dt_agenda or row.dt_consulta, row.nm_medico_externo
            )
            cd_agenda = getattr(row, "cd_agenda", None)
            if bot.enviar_mensagem_por_telefone_com_nr_sequencia(
                telefone,
                row.nm_paciente or "Paciente",
                mensagem,
                row.nr_sequencia,
                nr_sequencia_agenda=cd_agenda,
            ):
                registrar_envio_48h(
                    sqlite_session,
                    nr_sequencia=row.nr_sequencia,
                    dt_agenda=row.dt_agenda or row.dt_consulta,
                    nr_telefone=row.nr_telefone,
                    nm_paciente=row.nm_paciente,
                    nr_ddi=row.nr_ddi,
                    nm_medico_externo=row.nm_medico_externo,
                    cd_agenda=cd_agenda,
                )
            else:
                logger.error(f"Falha ao enviar 48h nr_sequencia={row.nr_sequencia}")
    finally:
        db_main.close()
        sqlite_session.close()


def executar_job_lembretes_12h() -> None:
    """
    Job 12h: só SQLite → enviar → gravar 12h no SQLite.
    """
    db_main = next(get_db())
    sqlite_session = get_sqlite_session()
    bot = BotconversaService(db_main)
    try:
        lista = listar_para_lembrete_12h(sqlite_session, horas_janela=12)
        logger.info(f"Lembretes 12h a enviar: {len(lista)}")
        for env in lista:
            telefone = telefone_para_envio(env.nr_telefone, env.nr_ddi)
            if not telefone:
                logger.warning(f"nr_sequencia={env.nr_sequencia} sem telefone, ignorando")
                continue
            mensagem = _mensagem_lembrete_12h(
                env.nm_paciente, env.dt_agenda, env.nm_medico_externo
            )
            cd_agenda = getattr(env, "cd_agenda", None)
            if bot.enviar_mensagem_por_telefone_com_nr_sequencia(
                telefone,
                env.nm_paciente or "Paciente",
                mensagem,
                env.nr_sequencia,
                nr_sequencia_agenda=cd_agenda,
            ):
                registrar_envio_12h(
                    sqlite_session,
                    nr_sequencia=env.nr_sequencia,
                    dt_agenda=env.dt_agenda,
                    nr_telefone=env.nr_telefone,
                    nm_paciente=env.nm_paciente,
                    nr_ddi=env.nr_ddi,
                    nm_medico_externo=env.nm_medico_externo,
                    cd_agenda=cd_agenda,
                )
            else:
                logger.error(f"Falha ao enviar 12h nr_sequencia={env.nr_sequencia}")
    finally:
        db_main.close()
        sqlite_session.close()
