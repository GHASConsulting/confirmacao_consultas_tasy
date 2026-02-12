#!/usr/bin/env python3
"""
🏥 CLI - Sistema de Confirmação de Consultas

Interface de linha de comando para gerenciar e testar o sistema.
"""

import click
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

console = Console()

# Importações dos comandos
from cli.commands.database import test_connection
from cli.commands.botconversa import (
    test_conexao,
    listar_atendimentos,
    buscar_atendimento,
    enviar_mensagem,
    executar_workflow,
    processar_resposta,
    criar_atendimento,
    adicionar_botconversa,
    adicionar_campanha,
    adicionar_etiqueta,
    adicionar_campo_personalizado
)


@click.group()
@click.version_option(version="1.0.0", prog_name="🏥 Hospital CLI")
def cli():
    """
    🏥 Sistema de Confirmação de Consultas

    Interface de linha de comando para gerenciar e testar o sistema.

    Exemplos:
        python -m cli status                    # Ver status do sistema
        python -m cli test-db                   # Testar conexão com banco
        python -m cli listar-atendimentos       # Listar atendimentos
        python -m cli criar-atendimento         # Criar novo atendimento
        python -m cli test-conexao              # Testar Botconversa
        python -m cli executar-workflow         # Executar workflow
        python -m cli adicionar-etiqueta        # Adicionar etiqueta subscriber_id
        python -m cli adicionar-campo-personalizado # Adicionar campo personalizado
    """
    pass


# Comandos principais
cli.add_command(test_connection, name="test-db")

# Comandos Botconversa
cli.add_command(test_conexao, name="test-conexao")
cli.add_command(listar_atendimentos, name="listar-atendimentos")
cli.add_command(buscar_atendimento, name="buscar-atendimento")
cli.add_command(enviar_mensagem, name="enviar-mensagem")
cli.add_command(executar_workflow, name="executar-workflow")
cli.add_command(processar_resposta, name="processar-resposta")
cli.add_command(criar_atendimento, name="criar-atendimento")
cli.add_command(adicionar_botconversa, name="adicionar-botconversa")
cli.add_command(adicionar_campanha, name="adicionar-campanha")
cli.add_command(adicionar_etiqueta, name="adicionar-etiqueta")
cli.add_command(adicionar_campo_personalizado, name="adicionar-campo-personalizado")


@cli.command()
def status():
    """Mostra status do sistema"""
    try:
        from app.config.config import settings

        console.print(
            Panel(
                f"Hospital: {settings.hospital_name or 'Não configurado'}\n"
                f"Tipo de Banco: {settings.database_type}\n"
                f"Debug: {settings.debug}\n"
                f"Log Level: {settings.log_level}\n"
                f"Botconversa API: {'✅' if settings.botconversa_api_key else '❌'}",
                title="📊 Status do Sistema",
            )
        )

    except Exception as e:
        console.print(f"❌ Erro: {str(e)}")


@cli.command()
def atendimentos():
    """Lista todos os atendimentos"""
    db = None
    try:
        from app.database.manager import get_db, initialize_database
        from app.database.models import Atendimento

        initialize_database()
        db = next(get_db())

        atendimentos = db.query(Atendimento).all()

        if not atendimentos:
            console.print("📭 Nenhum atendimento encontrado")
            return

        table = Table(title="🏥 Atendimentos Cadastrados")
        table.add_column("ID", style="cyan")
        table.add_column("Paciente", style="green")
        table.add_column("Telefone", style="blue")
        table.add_column("Médico", style="yellow")
        table.add_column("Especialidade", style="magenta")
        table.add_column("Data", style="cyan")
        table.add_column("Status", style="red")
        table.add_column("Subscriber ID", style="blue")

        for a in atendimentos:
            table.add_row(
                str(a.id),
                a.nome_paciente,
                a.telefone,
                a.nome_medico,
                a.especialidade,
                a.data_consulta.strftime("%d/%m/%Y %H:%M") if a.data_consulta else "N/A",
                a.status.value if a.status else "N/A",
                str(a.subscriber_id) if a.subscriber_id else "N/A",
            )

        console.print(table)

    except Exception as e:
        console.print(f"❌ Erro: {str(e)}")
    finally:
        if db:
            try:
                db.close()
            except Exception:
                pass


@cli.command()
def help():
    """
    Mostra ajuda detalhada sobre os comandos disponíveis.
    """
    help_text = """
[bold blue]🏥 SISTEMA DE CONFIRMAÇÃO DE CONSULTAS - CLI[/bold blue]

[bold green]Comandos Disponíveis:[/bold green]

[bold]📊 Status e Configuração:[/bold]
  status                    - Ver status atual do sistema
  test-db                   - Testar conexão com banco de dados

[bold]🏥 Gerenciamento de Atendimentos:[/bold]
  atendimentos              - Listar todos os atendimentos cadastrados
  listar-atendimentos       - Listar atendimentos pendentes de confirmação
  buscar-atendimento        - Buscar atendimento específico por telefone
  criar-atendimento         - Criar novo atendimento completo

[bold]🤖 Integração Botconversa:[/bold]
  test-conexao              - Testar conexão com API Botconversa
  adicionar-botconversa     - Adicionar paciente como subscriber no Botconversa
  enviar-mensagem           - Enviar mensagem personalizada para paciente
  executar-workflow         - Executar workflow completo de confirmação
  processar-resposta        - Processar resposta do paciente
  adicionar-campanha        - Adicionar paciente na campanha do Botconversa
  adicionar-etiqueta        - Adicionar etiqueta subscriber_id a contato existente

[bold]🎯 Exemplos de Uso:[/bold]

[bold]📊 Verificar Sistema:[/bold]
  python -m cli status                    # Status geral do sistema
  python -m cli test-db                   # Testar conexão com banco

[bold]🏥 Gerenciar Atendimentos:[/bold]
  python -m cli atendimentos              # Listar todos os atendimentos
  python -m cli listar-atendimentos       # Listar apenas pendentes
  python -m cli buscar-atendimento --telefone 5531995485500
  python -m cli criar-atendimento --nome "João Silva" --telefone 5531999629004 --medico "Dr. Carlos" --especialidade "Cardiologia" --data "15/01/2024" --hora "14:30"

[bold]🤖 Integração Botconversa:[/bold]
  python -m cli test-conexao              # Testar API Botconversa
  python -m cli adicionar-botconversa --telefone 5531995485500
  python -m cli executar-workflow --id 1  # Executar workflow para atendimento ID 1
  python -m cli enviar-mensagem --telefone 5531995485500
  python -m cli processar-resposta --telefone 5531995485500 --resposta 1
  python -m cli adicionar-campanha --telefone 5531995485500
  python -m cli adicionar-etiqueta --telefone 5531995485500

[bold]💡 Fluxo Completo de Trabalho:[/bold]
  1. Criar atendimento: criar-atendimento
  2. Adicionar no Botconversa: adicionar-botconversa
  3. Executar workflow: executar-workflow
  4. Monitorar respostas: processar-resposta

[bold]📱 Formato dos Dados:[/bold]
  • Telefone: 5531999629004 (formato internacional)
  • Data: DD/MM/AAAA (ex: 15/01/2024)
  • Hora: HH:MM (ex: 14:30)
  • Resposta: 1 (SIM) ou 0 (NÃO)

[bold]🔧 Comandos de Ajuda:[/bold]
  python -m cli --help                    # Ajuda geral
  python -m cli [comando] --help          # Ajuda específica do comando
    """

    console.print(
        Panel(
            help_text,
            title="[bold blue]Ajuda do Sistema[/bold blue]",
            border_style="blue",
        )
    )


if __name__ == "__main__":
    cli()
