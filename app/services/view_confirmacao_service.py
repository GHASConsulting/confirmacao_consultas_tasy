"""
Serviço para leitura da view de confirmação de consulta (janela 48h).

Lê da view no banco principal (Oracle) e retorna linhas para comparação com SQLite.
"""

from typing import List

from loguru import logger
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.config.config import settings
from app.schemas.schemas import ViewConfirmacaoConsulta


def _row_to_dict(row) -> dict:
    """Converte linha do banco (colunas em maiúsculas) para dict em minúsculas."""
    if hasattr(row, "_mapping"):
        return {str(k).lower(): v for k, v in row._mapping.items()}
    return {str(k).lower(): v for k, v in row.items()} if hasattr(row, "items") else dict(row)


def listar_view_confirmacao_48h(db: Session) -> List[ViewConfirmacaoConsulta]:
    """
    Lê da view de confirmação (janela 48h) no banco principal.

    A view deve retornar apenas registros na janela de 48h.
    Retorna lista de ViewConfirmacaoConsulta para comparação com SQLite.
    """
    view_name = getattr(settings, "view_confirmacao_nome", "TASY.AVA_CONFIRMACAO_CONSULTA")
    query = text(f"SELECT * FROM {view_name}")
    try:
        result = db.execute(query)
        rows = result.fetchall()
        out = []
        for row in rows:
            d = _row_to_dict(row)
            # Só incluir campos que existem no schema
            allowed = {
                "nr_sequencia", "cd_agenda", "dt_agenda", "dt_consulta",
                "nm_paciente", "nr_telefone", "nr_ddi", "ds_email",
                "nm_medico_externo", "cd_especialidade", "ds_observacao", "ie_status_agenda",
            }
            filtered = {k: v for k, v in d.items() if k in allowed}
            try:
                out.append(ViewConfirmacaoConsulta(**filtered))
            except Exception as e:
                logger.warning(f"Ignorando linha da view (erro de parsing): {e}")
                continue
        logger.info(f"View {view_name}: {len(out)} registros (48h)")
        return out
    except Exception as e:
        logger.error(f"Erro ao ler view {view_name}: {e}")
        raise
