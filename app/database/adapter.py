from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Any, TYPE_CHECKING
from datetime import datetime
from sqlalchemy.orm import Session
from loguru import logger

from app.config.config import DataBaseType

if TYPE_CHECKING:
    from app.database.models import (
        Paciente,
        Consulta,
        Confirmacao,
        StatusConfirmacao,
    )


class DatabaseAdapter(ABC):
    """Classe abstrata para adaptadores de banco de dados"""

    @abstractmethod
    def create_patient(self, patient_data: Dict[str, Any]) -> "Paciente":
        pass

    @abstractmethod
    def get_patient(self, patient_id: int) -> Optional["Paciente"]:
        pass

    @abstractmethod
    def get_patients(self, skip: int = 0, limit: int = 100) -> List["Paciente"]:
        pass

    @abstractmethod
    def create_appointment(self, appointment_data: Dict[str, Any]) -> "Consulta":
        pass

    @abstractmethod
    def get_appointment(self, appointment_id: int) -> Optional["Consulta"]:
        pass

    @abstractmethod
    def get_appointments(
        self, skip: int = 0, limit: int = 100, status_filter: Optional[str] = None
    ) -> List["Consulta"]:
        pass

    @abstractmethod
    def update_appointment_status(
        self, appointment_id: int, status: "StatusConfirmacao"
    ) -> bool:
        pass

    @abstractmethod
    def create_confirmation(self, confirmation_data: Dict[str, Any]) -> "Confirmacao":
        pass

    @abstractmethod
    def get_confirmations(self, appointment_id: int) -> List["Confirmacao"]:
        pass


class SQLAlchemyAdapter(DatabaseAdapter):
    """Adaptador para bancos SQL (Oracle, PostgreSQL e Firebird)"""

    def __init__(self, session: Session):
        self.session = session

    def create_patient(self, patient_data: Dict[str, Any]) -> "Paciente":
        from app.database.models import Paciente

        paciente = Paciente(**patient_data)
        self.session.add(paciente)
        self.session.commit()
        self.session.refresh(paciente)
        return paciente

    def get_patient(self, patient_id: int) -> Optional["Paciente"]:
        from app.database.models import Paciente

        return self.session.query(Paciente).filter(Paciente.id == patient_id).first()

    def get_patients(self, skip: int = 0, limit: int = 100) -> List["Paciente"]:
        from app.database.models import Paciente

        return self.session.query(Paciente).offset(skip).limit(limit).all()

    def create_appointment(self, appointment_data: Dict[str, Any]) -> "Consulta":
        from app.database.models import Consulta

        consulta = Consulta(**appointment_data)
        self.session.add(consulta)
        self.session.commit()
        self.session.refresh(consulta)
        return consulta

    def get_appointment(self, appointment_id: int) -> Optional["Consulta"]:
        from app.database.models import Consulta

        return (
            self.session.query(Consulta).filter(Consulta.id == appointment_id).first()
        )

    def get_appointments(
        self, skip: int = 0, limit: int = 100, status_filter: Optional[str] = None
    ) -> List["Consulta"]:
        from app.database.models import Consulta

        query = self.session.query(Consulta)
        if status_filter:
            query = query.filter(Consulta.status == status_filter)
        return query.offset(skip).limit(limit).all()

    def update_appointment_status(
        self, appointment_id: int, status: "StatusConfirmacao"
    ) -> bool:
        from app.database.models import Consulta

        consulta = (
            self.session.query(Consulta).filter(Consulta.id == appointment_id).first()
        )
        if consulta:
            consulta.status = status
            self.session.commit()
            return True
        return False

    def create_confirmation(self, confirmation_data: Dict[str, Any]) -> "Confirmacao":
        from app.database.models import Confirmacao

        confirmacao = Confirmacao(**confirmation_data)
        self.session.add(confirmacao)
        self.session.commit()
        self.session.refresh(confirmacao)
        return confirmacao

    def get_confirmations(self, appointment_id: int) -> List["Confirmacao"]:
        from app.database.models import Confirmacao

        return (
            self.session.query(Confirmacao)
            .filter(Confirmacao.consulta_id == appointment_id)
            .all()
        )


def get_database_adapter(database_type: DataBaseType, session_or_client):
    """Factory para criar o adaptador correto baseado no tipo de banco"""
    if database_type in [
        DataBaseType.ORACLE,
        DataBaseType.POSTGRESQL,
        DataBaseType.FIREBIRD,
    ]:
        return SQLAlchemyAdapter(session_or_client)
    else:
        raise ValueError(f"Tipo de banco de dados não suportado: {database_type}")
