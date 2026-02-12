"""
Módulo de banco de dados da aplicação.

Contém a configuração base do SQLAlchemy e os modelos do sistema.
"""

from .base import Base
from .models import (
    Paciente,
    Consulta,
    Confirmacao,
)
from app.config.config import DataBaseType

__all__ = [
    "Base",
    "Paciente",
    "Consulta",
    "Confirmacao",
    "DataBaseType",
]
