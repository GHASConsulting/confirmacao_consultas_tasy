"""
Rotas para teste da integração com o Botconversa.

Este módulo contém endpoints para testar:
- Conexão com a API do Botconversa
- Criação de subscribers
- Busca de subscribers
- Criação de atendimentos
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Dict, Any, List, Optional
from datetime import datetime

from app.database.manager import get_db
from app.services.botconversa_service import BotconversaService
from app.database.models import Atendimento, StatusConfirmacao

router = APIRouter(prefix="/test", tags=["Teste Botconversa"])


@router.get("/conexao")
async def testar_conexao(db: Session = Depends(get_db)) -> Dict[str, Any]:
    """
    Testa a conexão com a API do Botconversa.

    Returns:
        Resultado do teste de conexão
    """
    try:
        service = BotconversaService(db)
        resultado = service.testar_conexao()
        return resultado
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao testar conexão: {str(e)}")


@router.post("/subscriber")
async def criar_subscriber(
    telefone: str, nome: str, sobrenome: str = "", db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    Cria um subscriber no Botconversa.

    Args:
        telefone: Número do telefone (formato: 5531999629004)
        nome: Primeiro nome
        sobrenome: Sobrenome (opcional)

    Returns:
        Dados do subscriber criado
    """
    try:
        service = BotconversaService(db)
        subscriber = service.criar_subscriber(telefone, nome, sobrenome)

        if subscriber:
            return {
                "success": True,
                "message": "Subscriber criado com sucesso",
                "subscriber": subscriber,
            }
        else:
            raise HTTPException(status_code=400, detail="Erro ao criar subscriber")

    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Erro ao criar subscriber: {str(e)}"
        )


@router.get("/subscriber/{telefone}")
async def buscar_subscriber(
    telefone: str, db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    Busca um subscriber pelo telefone.

    Args:
        telefone: Número do telefone

    Returns:
        Dados do subscriber encontrado
    """
    try:
        service = BotconversaService(db)
        subscriber = service.buscar_subscriber(telefone)

        if subscriber:
            return {
                "success": True,
                "message": "Subscriber encontrado",
                "subscriber": subscriber,
            }
        else:
            return {
                "success": False,
                "message": "Subscriber não encontrado",
                "subscriber": None,
            }

    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Erro ao buscar subscriber: {str(e)}"
        )


@router.post("/atendimento")
async def criar_atendimento(
    dados: Dict[str, Any], db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    Cria um novo atendimento e registra no Botconversa.

    Args:
        dados: Dados do atendimento (nome_paciente, telefone, email, nome_medico, especialidade, data_consulta, observacoes)

    Returns:
        Dados do atendimento criado
    """
    try:
        service = BotconversaService(db)
        atendimento = service.criar_atendimento(dados)

        if atendimento:
            return {
                "success": True,
                "message": "Atendimento criado com sucesso",
                "atendimento": {
                    "id": atendimento.id,
                    "nome_paciente": atendimento.nome_paciente,
                    "telefone": atendimento.telefone,
                    "nome_medico": atendimento.nome_medico,
                    "especialidade": atendimento.especialidade,
                    "data_consulta": atendimento.data_consulta,
                    "status": atendimento.status.value,  # Campo de controle
                    "subscriber_id": atendimento.subscriber_id,
                    "criado_em": atendimento.criado_em,
                },
            }
        else:
            raise HTTPException(status_code=400, detail="Erro ao criar atendimento")

    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Erro ao criar atendimento: {str(e)}"
        )


@router.get("/atendimentos/pendentes")
async def listar_atendimentos_pendentes(
    db: Session = Depends(get_db),
) -> Dict[str, Any]:
    """
    Lista todos os atendimentos pendentes (campo de controle = PENDENTE).

    Returns:
        Lista de atendimentos pendentes
    """
    try:
        service = BotconversaService(db)
        atendimentos = service.listar_atendimentos_pendentes()

        return {
            "success": True,
            "message": f"Encontrados {len(atendimentos)} atendimentos pendentes",
            "atendimentos": [
                {
                    "id": a.id,
                    "nome_paciente": a.nome_paciente,
                    "telefone": a.telefone,
                    "nome_medico": a.nome_medico,
                    "especialidade": a.especialidade,
                    "data_consulta": a.data_consulta,
                    "status": a.status.value,  # Campo de controle
                    "subscriber_id": a.subscriber_id,
                    "criado_em": a.criado_em,
                }
                for a in atendimentos
            ],
        }

    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Erro ao listar atendimentos: {str(e)}"
        )


@router.get("/atendimento/{telefone}")
async def buscar_atendimento_por_telefone(
    telefone: str, db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    Busca um atendimento pelo telefone.

    Args:
        telefone: Número do telefone

    Returns:
        Dados do atendimento encontrado
    """
    try:
        service = BotconversaService(db)
        atendimento = service.buscar_atendimento_por_telefone(telefone)

        if atendimento:
            return {
                "success": True,
                "message": "Atendimento encontrado",
                "atendimento": {
                    "id": atendimento.id,
                    "nome_paciente": atendimento.nome_paciente,
                    "telefone": atendimento.telefone,
                    "nome_medico": atendimento.nome_medico,
                    "especialidade": atendimento.especialidade,
                    "data_consulta": atendimento.data_consulta,
                    "status": atendimento.status.value,  # Campo de controle
                    "subscriber_id": atendimento.subscriber_id,
                    "criado_em": atendimento.criado_em,
                    "resposta_paciente": atendimento.resposta_paciente,
                    "interpretacao_resposta": atendimento.interpretacao_resposta,
                    "respondido_em": atendimento.respondido_em,
                },
            }
        else:
            return {
                "success": False,
                "message": "Atendimento não encontrado",
                "atendimento": None,
            }

    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Erro ao buscar atendimento: {str(e)}"
        )


@router.put("/atendimento/{atendimento_id}/status")
async def atualizar_status_atendimento(
    atendimento_id: int, status: StatusConfirmacao, db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    Atualiza o campo de controle (status) de um atendimento.

    Args:
        atendimento_id: ID do atendimento
        status: Novo status (pendente, confirmado, cancelado, sem_resposta)

    Returns:
        Resultado da atualização
    """
    try:
        service = BotconversaService(db)
        success = service.atualizar_status_atendimento(atendimento_id, status)

        if success:
            return {
                "success": True,
                "message": f"Status do atendimento {atendimento_id} atualizado para {status.value}",
                "atendimento_id": atendimento_id,
                "novo_status": status.value,
            }
        else:
            raise HTTPException(
                status_code=400, detail="Erro ao atualizar status do atendimento"
            )

    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Erro ao atualizar status: {str(e)}"
        )


@router.get("/campanhas")
async def listar_campanhas(db: Session = Depends(get_db)) -> Dict[str, Any]:
    """
    Lista todas as campanhas ativas no Botconversa.

    Returns:
        Lista de campanhas ativas
    """
    try:
        service = BotconversaService(db)
        campanhas = service.listar_campanhas()

        if campanhas is not None:
            return {
                "success": True,
                "message": f"Campanhas encontradas: {len(campanhas)}",
                "campanhas": campanhas,
            }
        else:
            raise HTTPException(status_code=400, detail="Erro ao listar campanhas")

    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Erro ao listar campanhas: {str(e)}"
        )


@router.get("/fluxos")
async def listar_fluxos(db: Session = Depends(get_db)) -> Dict[str, Any]:
    """
    Lista todos os fluxos disponíveis no Botconversa.

    Returns:
        Lista de fluxos disponíveis
    """
    try:
        service = BotconversaService(db)
        fluxos = service.listar_fluxos()

        if fluxos is not None:
            return {
                "success": True,
                "message": f"Fluxos encontrados: {len(fluxos)}",
                "fluxos": fluxos,
            }
        else:
            raise HTTPException(status_code=400, detail="Erro ao listar fluxos")

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao listar fluxos: {str(e)}")


@router.post("/subscriber/{subscriber_id}/campaigns/{campaign_id}")
async def adicionar_subscriber_campanha(
    subscriber_id: int, campaign_id: int = 289860, db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    Adiciona um subscriber à campanha de confirmação de consultas.

    Args:
        subscriber_id: ID do subscriber no Botconversa
        campaign_id: ID da campanha (padrão: 289860 - Confirmação de Consultas)

    Returns:
        Resultado da operação
    """
    try:
        service = BotconversaService(db)
        sucesso = service.adicionar_subscriber_campanha(subscriber_id, campaign_id)

        if sucesso:
            return {
                "success": True,
                "message": f"Subscriber {subscriber_id} adicionado à campanha {campaign_id} com sucesso",
            }
        else:
            raise HTTPException(
                status_code=400, detail="Erro ao adicionar subscriber à campanha"
            )

    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Erro ao adicionar subscriber à campanha: {str(e)}"
        )


@router.post("/subscriber/{subscriber_id}/send_flow")
async def enviar_fluxo(
    subscriber_id: int, flow_id: Optional[int] = None, db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    Envia um fluxo para um subscriber.

    Args:
        subscriber_id: ID do subscriber no Botconversa
        flow_id: ID do fluxo (opcional - se não informado, usa o fluxo padrão da campanha)

    Returns:
        Resultado da operação
    """
    try:
        service = BotconversaService(db)
        sucesso = service.enviar_fluxo(subscriber_id, flow_id)

        if sucesso:
            return {
                "success": True,
                "message": f"Fluxo enviado com sucesso para subscriber {subscriber_id}",
                "subscriber_id": subscriber_id,
                "flow_id": flow_id,
            }
        else:
            raise HTTPException(status_code=400, detail="Erro ao enviar fluxo")

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao enviar fluxo: {str(e)}")


@router.post("/workflow/{atendimento_id}")
async def executar_workflow_consulta(
    atendimento_id: int, db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    Executa o workflow completo para uma consulta:
    1. Envia mensagem personalizada
    2. Adiciona à campanha
    3. Envia fluxo

    Args:
        atendimento_id: ID do atendimento

    Returns:
        Resultado do workflow
    """
    try:
        service = BotconversaService(db)
        resultado = service.executar_workflow_consulta(atendimento_id)

        if resultado.get("success"):
            return {
                "success": True,
                "message": "Workflow executado com sucesso",
                "data": resultado,
            }
        else:
            raise HTTPException(
                status_code=400,
                detail=f"Erro no workflow: {resultado.get('error', 'Erro desconhecido')}",
            )

    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Erro ao executar workflow: {str(e)}"
        )
