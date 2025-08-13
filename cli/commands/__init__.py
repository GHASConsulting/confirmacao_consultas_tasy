"""
Comandos da CLI

Este módulo contém todos os comandos da interface de linha de comando.
"""

from .database import test_connection
from .botconversa import (
    test_conexao,
    listar_atendimentos,
    buscar_atendimento,
    enviar_mensagem,
    executar_workflow,
    processar_resposta,
    criar_atendimento,
    adicionar_botconversa,
    adicionar_campanha,
)

__all__ = [
    "test_connection",
    "test_conexao",
    "listar_atendimentos",
    "buscar_atendimento",
    "enviar_mensagem",
    "executar_workflow",
    "processar_resposta",
    "criar_atendimento",
    "adicionar_botconversa",
    "adicionar_campanha",
]
