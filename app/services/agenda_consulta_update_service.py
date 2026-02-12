"""
Atualização da tabela agenda_consulta no banco principal (Oracle).

Usado quando o paciente responde à confirmação (SIM/NÃO) no webhook:
atualiza DT_CONFIRMACAO, DS_CONFIRMACAO e outros campos relevantes.
"""

from datetime import datetime

from loguru import logger
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.config.config import settings


def atualizar_confirmacao_agenda_consulta(
    db: Session,
    cd_agenda: int,
    confirmado: bool,
) -> bool:
    """
    Atualiza a tabela agenda_consulta com data e texto de confirmação.

    Usa CD_AGENDA (nr_sequencia_agenda) no WHERE para não alterar agenda errada,
    já que o mesmo paciente pode ter várias agendas.

    Args:
        db: Sessão do banco principal (Oracle).
        cd_agenda: Chave da agenda (CD_AGENDA / nr_sequencia_agenda).
        confirmado: True = confirmado ('1'), False = cancelado ('0').

    Returns:
        True se o UPDATE afetou alguma linha, False caso contrário.
    """
    tabela = getattr(settings, "tabela_agenda_consulta", "TASY.AGENDA_CONSULTA")
    dt_confirmacao = datetime.now()
    ds_confirmacao = "Confirmado" if confirmado else "Cancelado"

    try:
        sql = text(
            f"UPDATE {tabela} SET DT_CONFIRMACAO = :dt_confirmacao, DS_CONFIRMACAO = :ds_confirmacao WHERE CD_AGENDA = :cd_agenda"
        )
        result = db.execute(
            sql,
            {
                "dt_confirmacao": dt_confirmacao,
                "ds_confirmacao": ds_confirmacao,
                "cd_agenda": cd_agenda,
            },
        )
        db.commit()
        rowcount = result.rowcount
        logger.info(
            f"agenda_consulta atualizada: cd_agenda={cd_agenda}, "
            f"confirmado={confirmado}, rowcount={rowcount}"
        )
        return rowcount is not None and rowcount > 0
    except Exception as e:
        logger.error(f"Erro ao atualizar agenda_consulta cd_agenda={cd_agenda}: {e}")
        db.rollback()
        raise
