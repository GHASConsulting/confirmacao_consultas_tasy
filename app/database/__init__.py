"""
Módulo de banco de dados da aplicação.

Este módulo contém adaptadores para diferentes tipos de banco de dados
e os modelos principais do sistema.

Módulos:
    base: Configuração base do SQLAlchemy
    models: Modelos de dados (Paciente, Consulta, Confirmacao)
    adapter: Adaptadores para diferentes tipos de banco

Classes:
    Base: Classe base para modelos declarativos do SQLAlchemy
    Paciente: Modelo para representar pacientes
    Consulta: Modelo para representar consultas médicas
    Confirmacao: Modelo para representar confirmações de consultas
    DataBaseType: Enum com tipos de banco suportados (ORACLE, POSTGRESQL, FIREBIRD)
    DatabaseAdapter: Classe abstrata base para adaptadores
    SQLAlchemyAdapter: Adaptador para Oracle, PostgreSQL e Firebird

Funções:
    get_database_adapter: Factory para criar adaptadores baseado no tipo de banco
"""

from .base import Base
from .models import (
    Paciente,
    Consulta,
    Confirmacao,
)
from .adapter import (
    DatabaseAdapter,
    SQLAlchemyAdapter,
    get_database_adapter,
)
from app.config.config import DataBaseType

__all__ = [
    # Base
    "Base",
    # Models
    "Paciente",
    "Consulta",
    "Confirmacao",
    # Database Types
    "DataBaseType",
    # Adapters
    "DatabaseAdapter",
    "SQLAlchemyAdapter",
    # Factory
    "get_database_adapter",
]
