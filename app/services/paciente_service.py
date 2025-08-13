"""
Serviço para gestão de pacientes.

Este serviço gerencia:
- CRUD de pacientes
- Busca por telefone
- Validação de dados
- Relacionamentos com consultas
"""

from typing import List, Optional, Dict, Any
from datetime import datetime
from loguru import logger
from sqlalchemy.orm import Session
from sqlalchemy import and_

from app.database.models import Paciente, Consulta, StatusConfirmacao


class PacienteService:
    """Serviço para gestão de pacientes"""

    def __init__(self, db: Session):
        self.db = db

    def criar_paciente(self, dados: Dict[str, Any]) -> Optional[Paciente]:
        """
        Cria um novo paciente.

        Args:
            dados: Dados do paciente (nome, telefone, email)

        Returns:
            Paciente criado ou None se erro
        """
        try:
            # Verifica se já existe paciente com o telefone
            paciente_existente = (
                self.db.query(Paciente)
                .filter(Paciente.telefone == dados["telefone"])
                .first()
            )

            if paciente_existente:
                logger.warning(f"Paciente já existe com telefone: {dados['telefone']}")
                return paciente_existente

            # Cria novo paciente
            paciente = Paciente(
                nome=dados["nome"], telefone=dados["telefone"], email=dados.get("email")
            )

            self.db.add(paciente)
            self.db.commit()
            self.db.refresh(paciente)

            logger.info(f"Paciente criado com sucesso: {paciente.id}")
            return paciente

        except Exception as e:
            logger.error(f"Erro ao criar paciente: {str(e)}")
            self.db.rollback()
            return None

    def buscar_paciente(self, paciente_id: int) -> Optional[Paciente]:
        """
        Busca um paciente por ID.

        Args:
            paciente_id: ID do paciente

        Returns:
            Paciente encontrado ou None
        """
        try:
            paciente = (
                self.db.query(Paciente).filter(Paciente.id == paciente_id).first()
            )
            return paciente
        except Exception as e:
            logger.error(f"Erro ao buscar paciente {paciente_id}: {str(e)}")
            return None

    def buscar_paciente_por_telefone(self, telefone: str) -> Optional[Paciente]:
        """
        Busca um paciente por telefone.

        Args:
            telefone: Número do telefone

        Returns:
            Paciente encontrado ou None
        """
        try:
            paciente = (
                self.db.query(Paciente).filter(Paciente.telefone == telefone).first()
            )
            return paciente
        except Exception as e:
            logger.error(f"Erro ao buscar paciente por telefone {telefone}: {str(e)}")
            return None

    def listar_pacientes(self, skip: int = 0, limit: int = 100) -> List[Paciente]:
        """
        Lista pacientes com paginação.

        Args:
            skip: Número de registros para pular
            limit: Número máximo de registros

        Returns:
            Lista de pacientes
        """
        try:
            pacientes = self.db.query(Paciente).offset(skip).limit(limit).all()
            return pacientes
        except Exception as e:
            logger.error(f"Erro ao listar pacientes: {str(e)}")
            return []

    def atualizar_paciente(
        self, paciente_id: int, dados: Dict[str, Any]
    ) -> Optional[Paciente]:
        """
        Atualiza dados de um paciente.

        Args:
            paciente_id: ID do paciente
            dados: Novos dados do paciente

        Returns:
            Paciente atualizado ou None se erro
        """
        try:
            paciente = self.buscar_paciente(paciente_id)
            if not paciente:
                logger.error(f"Paciente não encontrado: {paciente_id}")
                return None

            # Atualiza campos
            if "nome" in dados:
                paciente.nome = dados["nome"]
            if "telefone" in dados:
                paciente.telefone = dados["telefone"]
            if "email" in dados:
                paciente.email = dados["email"]

            paciente.atualizado_em = datetime.now()

            self.db.commit()
            self.db.refresh(paciente)

            logger.info(f"Paciente atualizado com sucesso: {paciente_id}")
            return paciente

        except Exception as e:
            logger.error(f"Erro ao atualizar paciente {paciente_id}: {str(e)}")
            self.db.rollback()
            return None

    def deletar_paciente(self, paciente_id: int) -> bool:
        """
        Deleta um paciente.

        Args:
            paciente_id: ID do paciente

        Returns:
            True se deletado com sucesso, False caso contrário
        """
        try:
            paciente = self.buscar_paciente(paciente_id)
            if not paciente:
                logger.error(f"Paciente não encontrado: {paciente_id}")
                return False

            # Verifica se tem consultas
            consultas = (
                self.db.query(Consulta)
                .filter(Consulta.paciente_id == paciente_id)
                .count()
            )
            if consultas > 0:
                logger.error(
                    f"Paciente {paciente_id} tem {consultas} consultas associadas"
                )
                return False

            self.db.delete(paciente)
            self.db.commit()

            logger.info(f"Paciente deletado com sucesso: {paciente_id}")
            return True

        except Exception as e:
            logger.error(f"Erro ao deletar paciente {paciente_id}: {str(e)}")
            self.db.rollback()
            return False

    def buscar_consultas_paciente(self, paciente_id: int) -> List[Consulta]:
        """
        Busca todas as consultas de um paciente.

        Args:
            paciente_id: ID do paciente

        Returns:
            Lista de consultas do paciente
        """
        try:
            consultas = (
                self.db.query(Consulta)
                .filter(Consulta.paciente_id == paciente_id)
                .order_by(Consulta.data_consulta.desc())
                .all()
            )
            return consultas
        except Exception as e:
            logger.error(
                f"Erro ao buscar consultas do paciente {paciente_id}: {str(e)}"
            )
            return []

    def buscar_consultas_pendentes_paciente(self, paciente_id: int) -> List[Consulta]:
        """
        Busca consultas pendentes de um paciente.

        Args:
            paciente_id: ID do paciente

        Returns:
            Lista de consultas pendentes
        """
        try:
            consultas = (
                self.db.query(Consulta)
                .filter(
                    and_(
                        Consulta.paciente_id == paciente_id,
                        Consulta.status == StatusConfirmacao.PENDENTE,
                    )
                )
                .order_by(Consulta.data_consulta.asc())
                .all()
            )
            return consultas
        except Exception as e:
            logger.error(
                f"Erro ao buscar consultas pendentes do paciente {paciente_id}: {str(e)}"
            )
            return []

    def validar_dados_paciente(self, dados: Dict[str, Any]) -> Dict[str, Any]:
        """
        Valida dados de um paciente.

        Args:
            dados: Dados do paciente

        Returns:
            Dicionário com resultado da validação
        """
        errors = []

        # Valida nome
        if not dados.get("nome"):
            errors.append("Nome é obrigatório")
        elif len(dados["nome"].strip()) < 2:
            errors.append("Nome deve ter pelo menos 2 caracteres")

        # Valida telefone
        if not dados.get("telefone"):
            errors.append("Telefone é obrigatório")
        elif len(dados["telefone"].strip()) < 10:
            errors.append("Telefone deve ter pelo menos 10 dígitos")

        # Valida email (se fornecido)
        if dados.get("email"):
            email = dados["email"].strip()
            if "@" not in email or "." not in email:
                errors.append("Email inválido")

        return {"valid": len(errors) == 0, "errors": errors}
