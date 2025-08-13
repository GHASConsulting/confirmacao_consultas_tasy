"""
Serviço para gestão de consultas.

Este serviço gerencia:
- CRUD de consultas
- Busca por status
- Relacionamentos com pacientes
- Processamento de confirmações
"""

from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
from loguru import logger
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_

from app.database.models import Consulta, Paciente, StatusConfirmacao, Confirmacao


class ConsultaService:
    """Serviço para gestão de consultas"""

    def __init__(self, db: Session):
        self.db = db

    def criar_consulta(self, dados: Dict[str, Any]) -> Optional[Consulta]:
        """
        Cria uma nova consulta.

        Args:
            dados: Dados da consulta (paciente_id, nome_medico, especialidade, data_consulta, observacoes)

        Returns:
            Consulta criada ou None se erro
        """
        try:
            # Verifica se o paciente existe
            paciente = (
                self.db.query(Paciente)
                .filter(Paciente.id == dados["paciente_id"])
                .first()
            )
            if not paciente:
                logger.error(f"Paciente não encontrado: {dados['paciente_id']}")
                return None

            # Cria nova consulta
            consulta = Consulta(
                paciente_id=dados["paciente_id"],
                nome_medico=dados["nome_medico"],
                especialidade=dados["especialidade"],
                data_consulta=dados["data_consulta"],
                observacoes=dados.get("observacoes"),
                status=StatusConfirmacao.PENDENTE,
            )

            self.db.add(consulta)
            self.db.commit()
            self.db.refresh(consulta)

            logger.info(f"Consulta criada com sucesso: {consulta.id}")
            return consulta

        except Exception as e:
            logger.error(f"Erro ao criar consulta: {str(e)}")
            self.db.rollback()
            return None

    def buscar_consulta(self, consulta_id: int) -> Optional[Consulta]:
        """
        Busca uma consulta por ID.

        Args:
            consulta_id: ID da consulta

        Returns:
            Consulta encontrada ou None
        """
        try:
            consulta = (
                self.db.query(Consulta).filter(Consulta.id == consulta_id).first()
            )
            return consulta
        except Exception as e:
            logger.error(f"Erro ao buscar consulta {consulta_id}: {str(e)}")
            return None

    def listar_consultas(
        self,
        skip: int = 0,
        limit: int = 100,
        status: Optional[StatusConfirmacao] = None,
    ) -> List[Consulta]:
        """
        Lista consultas com filtros opcionais.

        Args:
            skip: Número de registros para pular
            limit: Número máximo de registros
            status: Filtro por status

        Returns:
            Lista de consultas
        """
        try:
            query = self.db.query(Consulta)

            if status:
                query = query.filter(Consulta.status == status)

            consultas = query.offset(skip).limit(limit).all()
            return consultas
        except Exception as e:
            logger.error(f"Erro ao listar consultas: {str(e)}")
            return []

    def buscar_consultas_pendentes(self) -> List[Consulta]:
        """
        Busca todas as consultas pendentes.

        Returns:
            Lista de consultas pendentes
        """
        try:
            consultas = (
                self.db.query(Consulta)
                .filter(Consulta.status == StatusConfirmacao.PENDENTE)
                .order_by(Consulta.data_consulta.asc())
                .all()
            )
            return consultas
        except Exception as e:
            logger.error(f"Erro ao buscar consultas pendentes: {str(e)}")
            return []

    def buscar_consultas_por_paciente(self, paciente_id: int) -> List[Consulta]:
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

    def atualizar_consulta(
        self, consulta_id: int, dados: Dict[str, Any]
    ) -> Optional[Consulta]:
        """
        Atualiza dados de uma consulta.

        Args:
            consulta_id: ID da consulta
            dados: Novos dados da consulta

        Returns:
            Consulta atualizada ou None se erro
        """
        try:
            consulta = self.buscar_consulta(consulta_id)
            if not consulta:
                logger.error(f"Consulta não encontrada: {consulta_id}")
                return None

            # Atualiza campos
            if "nome_medico" in dados:
                consulta.nome_medico = dados["nome_medico"]
            if "especialidade" in dados:
                consulta.especialidade = dados["especialidade"]
            if "data_consulta" in dados:
                consulta.data_consulta = dados["data_consulta"]
            if "observacoes" in dados:
                consulta.observacoes = dados["observacoes"]
            if "status" in dados:
                consulta.status = dados["status"]

            consulta.atualizado_em = datetime.now()

            self.db.commit()
            self.db.refresh(consulta)

            logger.info(f"Consulta atualizada com sucesso: {consulta_id}")
            return consulta

        except Exception as e:
            logger.error(f"Erro ao atualizar consulta {consulta_id}: {str(e)}")
            self.db.rollback()
            return None

    def atualizar_status_consulta(
        self, consulta_id: int, novo_status: StatusConfirmacao
    ) -> bool:
        """
        Atualiza o status de uma consulta.

        Args:
            consulta_id: ID da consulta
            novo_status: Novo status

        Returns:
            True se atualizado com sucesso, False caso contrário
        """
        try:
            consulta = self.buscar_consulta(consulta_id)
            if not consulta:
                logger.error(f"Consulta não encontrada: {consulta_id}")
                return False

            consulta.status = novo_status
            consulta.atualizado_em = datetime.now()

            self.db.commit()

            logger.info(
                f"Status da consulta {consulta_id} atualizado para {novo_status.value}"
            )
            return True

        except Exception as e:
            logger.error(
                f"Erro ao atualizar status da consulta {consulta_id}: {str(e)}"
            )
            self.db.rollback()
            return False

    def deletar_consulta(self, consulta_id: int) -> bool:
        """
        Deleta uma consulta.

        Args:
            consulta_id: ID da consulta

        Returns:
            True se deletada com sucesso, False caso contrário
        """
        try:
            consulta = self.buscar_consulta(consulta_id)
            if not consulta:
                logger.error(f"Consulta não encontrada: {consulta_id}")
                return False

            # Verifica se tem confirmações
            confirmacoes = (
                self.db.query(Confirmacao)
                .filter(Confirmacao.consulta_id == consulta_id)
                .count()
            )
            if confirmacoes > 0:
                logger.error(
                    f"Consulta {consulta_id} tem {confirmacoes} confirmações associadas"
                )
                return False

            self.db.delete(consulta)
            self.db.commit()

            logger.info(f"Consulta deletada com sucesso: {consulta_id}")
            return True

        except Exception as e:
            logger.error(f"Erro ao deletar consulta {consulta_id}: {str(e)}")
            self.db.rollback()
            return False

    def buscar_consultas_proximas(self, dias: int = 7) -> List[Consulta]:
        """
        Busca consultas nas próximas X dias.

        Args:
            dias: Número de dias para frente

        Returns:
            Lista de consultas próximas
        """
        try:
            data_limite = datetime.now() + timedelta(days=dias)

            consultas = (
                self.db.query(Consulta)
                .filter(
                    and_(
                        Consulta.data_consulta >= datetime.now(),
                        Consulta.data_consulta <= data_limite,
                    )
                )
                .order_by(Consulta.data_consulta.asc())
                .all()
            )
            return consultas
        except Exception as e:
            logger.error(f"Erro ao buscar consultas próximas: {str(e)}")
            return []

    def buscar_consultas_por_periodo(
        self, data_inicio: datetime, data_fim: datetime
    ) -> List[Consulta]:
        """
        Busca consultas em um período específico.

        Args:
            data_inicio: Data de início
            data_fim: Data de fim

        Returns:
            Lista de consultas no período
        """
        try:
            consultas = (
                self.db.query(Consulta)
                .filter(
                    and_(
                        Consulta.data_consulta >= data_inicio,
                        Consulta.data_consulta <= data_fim,
                    )
                )
                .order_by(Consulta.data_consulta.asc())
                .all()
            )
            return consultas
        except Exception as e:
            logger.error(f"Erro ao buscar consultas por período: {str(e)}")
            return []

    def validar_dados_consulta(self, dados: Dict[str, Any]) -> Dict[str, Any]:
        """
        Valida dados de uma consulta.

        Args:
            dados: Dados da consulta

        Returns:
            Dicionário com resultado da validação
        """
        errors = []

        # Valida paciente_id
        if not dados.get("paciente_id"):
            errors.append("ID do paciente é obrigatório")

        # Valida nome_medico
        if not dados.get("nome_medico"):
            errors.append("Nome do médico é obrigatório")
        elif len(dados["nome_medico"].strip()) < 2:
            errors.append("Nome do médico deve ter pelo menos 2 caracteres")

        # Valida especialidade
        if not dados.get("especialidade"):
            errors.append("Especialidade é obrigatória")
        elif len(dados["especialidade"].strip()) < 2:
            errors.append("Especialidade deve ter pelo menos 2 caracteres")

        # Valida data_consulta
        if not dados.get("data_consulta"):
            errors.append("Data da consulta é obrigatória")
        elif isinstance(dados["data_consulta"], datetime):
            if dados["data_consulta"] < datetime.now():
                errors.append("Data da consulta não pode ser no passado")

        return {"valid": len(errors) == 0, "errors": errors}
