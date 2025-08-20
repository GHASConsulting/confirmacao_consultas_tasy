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


@click.group()
@click.version_option(version="1.0.0", prog_name="🏥 Hospital CLI")
def cli():
    """
    🏥 Sistema de Confirmação de Consultas

    Interface de linha de comando para gerenciar e testar o sistema.

    Exemplos:
        python -m cli status                    # Ver status do sistema
        python -m cli test-db                   # Testar conexão com banco
        python -m cli pacientes                 # Listar pacientes
        python -m cli consultas                 # Listar consultas
        python -m cli criar-paciente            # Criar novo paciente
        python -m cli criar-consulta            # Criar nova consulta
        python -m cli botconversa               # Comandos Botconversa
    """
    pass


# Comandos principais
cli.add_command(test_connection, name="test-db")


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
def pacientes():
    """Lista todos os pacientes"""
    db = None
    try:
        from app.database.manager import get_db, initialize_database
        from app.database.models import Paciente

        initialize_database()
        db = next(get_db())

        pacientes = db.query(Paciente).all()

        if not pacientes:
            console.print("📭 Nenhum paciente encontrado")
            return

        table = Table(title="👥 Pacientes Cadastrados")
        table.add_column("ID", style="cyan")
        table.add_column("Nome", style="green")
        table.add_column("Telefone", style="blue")
        table.add_column("Email", style="yellow")
        table.add_column("Criado em", style="magenta")

        for p in pacientes:
            table.add_row(
                str(p.id),
                p.nome,
                p.telefone,
                p.email or "N/A",
                p.criado_em.strftime("%d/%m/%Y %H:%M") if p.criado_em else "N/A",
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
def consultas():
    """Lista todas as consultas"""
    db = None
    try:
        from app.database.manager import get_db, initialize_database
        from app.database.models import Consulta, Paciente

        initialize_database()
        db = next(get_db())

        consultas = db.query(Consulta).join(Paciente).all()

        if not consultas:
            console.print("📭 Nenhuma consulta encontrada")
            return

        table = Table(title="📋 Consultas Agendadas")
        table.add_column("ID", style="cyan")
        table.add_column("Paciente", style="green")
        table.add_column("Médico", style="blue")
        table.add_column("Especialidade", style="yellow")
        table.add_column("Data", style="magenta")
        table.add_column("Status", style="red")

        for c in consultas:
            table.add_row(
                str(c.id),
                c.paciente.nome,
                c.nome_medico,
                c.especialidade,
                c.data_consulta.strftime("%d/%m/%Y %H:%M") if c.data_consulta else "N/A",
                c.status.value,
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
@click.option("--nome", required=True, help="Nome completo do paciente")
@click.option("--telefone", required=True, help="Telefone no formato 5531999629004")
@click.option("--email", help="Email do paciente (opcional)")
def criar_paciente(nome, telefone, email):
    """Cria um novo paciente"""
    db = None
    try:
        from datetime import datetime

        from app.database.manager import get_db, initialize_database
        from app.database.models import Paciente

        initialize_database()
        db = next(get_db())

        # Verifica se já existe
        existente = db.query(Paciente).filter(Paciente.telefone == telefone).first()
        if existente:
            console.print(f"⚠️ Paciente com telefone {telefone} já existe")
            return

        # Cria novo paciente
        paciente = Paciente(
            nome=nome,
            telefone=telefone,
            email=email,
            criado_em=datetime.now(),
            atualizado_em=datetime.now(),
        )

        db.add(paciente)
        db.commit()

        console.print(f"✅ Paciente {nome} criado com sucesso! ID: {paciente.id}")

    except Exception as e:
        console.print(f"❌ Erro: {str(e)}")
    finally:
        if db:
            try:
                db.close()
            except Exception:
                pass


@cli.command()
@click.option("--paciente-id", required=True, type=int, help="ID do paciente")
@click.option("--medico", required=True, help="Nome do médico")
@click.option("--especialidade", required=True, help="Especialidade médica")
@click.option("--data", required=True, help="Data da consulta (DD/MM/AAAA)")
@click.option("--hora", required=True, help="Horário da consulta (HH:MM)")
@click.option("--observacoes", help="Observações adicionais")
def criar_consulta(paciente_id, medico, especialidade, data, hora, observacoes):
    """Cria uma nova consulta"""
    db = None
    try:
        from datetime import datetime

        from app.database.manager import get_db, initialize_database
        from app.database.models import Consulta, Paciente, StatusConfirmacao

        initialize_database()
        db = next(get_db())

        # Verifica se o paciente existe
        paciente = db.query(Paciente).filter(Paciente.id == paciente_id).first()
        if not paciente:
            console.print(f"❌ Paciente com ID {paciente_id} não encontrado")
            return

        # Converte data e hora
        try:
            data_obj = datetime.strptime(f"{data} {hora}", "%d/%m/%Y %H:%M")
        except ValueError:
            console.print("❌ Formato de data/hora inválido. Use DD/MM/AAAA HH:MM")
            return

        # Cria nova consulta
        consulta = Consulta(
            paciente_id=paciente_id,
            nome_medico=medico,
            especialidade=especialidade,
            data_consulta=data_obj,
            status=StatusConfirmacao.PENDENTE,
            observacoes=observacoes,
            criado_em=datetime.now(),
            atualizado_em=datetime.now(),
        )

        db.add(consulta)
        db.commit()

        console.print(f"✅ Consulta criada com sucesso! ID: {consulta.id}")

    except Exception as e:
        console.print(f"❌ Erro: {str(e)}")
    finally:
        if db:
            try:
                db.close()
            except Exception:
                pass


@cli.command()
@click.option("--nome", required=True, help="Nome completo do paciente")
@click.option("--telefone", required=True, help="Telefone no formato 5531999629004")
@click.option("--email", help="Email do paciente (opcional)")
@click.option("--medico", required=True, help="Nome do médico")
@click.option("--especialidade", required=True, help="Especialidade médica")
@click.option("--data", required=True, help="Data da consulta (DD/MM/AAAA)")
@click.option("--hora", required=True, help="Horário da consulta (HH:MM)")
@click.option("--observacoes", help="Observações adicionais")
def criar_atendimento(nome, telefone, email, medico, especialidade, data, hora, observacoes):
    """Cria um novo atendimento completo (paciente + consulta)"""
    db = None
    try:
        from datetime import datetime

        from app.database.manager import get_db, initialize_database
        from app.database.models import Atendimento, StatusConfirmacao

        initialize_database()
        db = next(get_db())

        # Verifica se já existe atendimento com este telefone
        existente = db.query(Atendimento).filter(Atendimento.telefone == telefone).first()
        if existente:
            console.print(f"⚠️ Atendimento com telefone {telefone} já existe")
            return

        # Converte data e hora
        try:
            data_obj = datetime.strptime(f"{data} {hora}", "%d/%m/%Y %H:%M")
        except ValueError:
            console.print("❌ Formato de data/hora inválido. Use DD/MM/AAAA HH:MM")
            return

        # Cria novo atendimento
        atendimento = Atendimento(
            nome_paciente=nome,
            telefone=telefone,
            email=email,
            nome_medico=medico,
            especialidade=especialidade,
            data_consulta=data_obj,
            observacoes=observacoes,
            status=StatusConfirmacao.PENDENTE,
            criado_em=datetime.now(),
            atualizado_em=datetime.now(),
        )

        db.add(atendimento)
        db.commit()

        console.print(f"✅ Atendimento criado com sucesso! ID: {atendimento.id}")
        console.print(f"📋 Paciente: {nome}")
        console.print(f"👨‍⚕️ Médico: {medico}")
        console.print(f"🏥 Especialidade: {especialidade}")
        console.print(f"📅 Data: {data} às {hora}")

    except Exception as e:
        console.print(f"❌ Erro: {str(e)}")
    finally:
        if db:
            try:
                db.close()
            except Exception:
                pass


@cli.command()
@click.option("--nome", required=True, help="Nome completo do paciente")
@click.option("--telefone", required=True, help="Telefone no formato 5531999629004")
@click.option("--email", help="Email do paciente (opcional)")
@click.option("--medico", required=True, help="Nome do médico")
@click.option("--especialidade", required=True, help="Especialidade médica")
@click.option("--data", required=True, help="Data da consulta (DD/MM/AAAA)")
@click.option("--hora", required=True, help="Horário da consulta (HH:MM)")
@click.option("--observacoes", help="Observações adicionais")
def criar_atendimento_completo(nome, telefone, email, medico, especialidade, data, hora, observacoes):
    """Cria um novo atendimento completo e executa o workflow automaticamente"""
    db = None
    try:
        from datetime import datetime

        from app.database.manager import get_db, initialize_database
        from app.database.models import Atendimento, StatusConfirmacao
        from app.services.botconversa_service import BotconversaService

        initialize_database()
        db = next(get_db())

        # Verifica se já existe atendimento com este telefone
        existente = db.query(Atendimento).filter(Atendimento.telefone == telefone).first()
        if existente:
            console.print(f"⚠️ Atendimento com telefone {telefone} já existe")
            return

        # Converte data e hora
        try:
            data_obj = datetime.strptime(f"{data} {hora}", "%d/%m/%Y %H:%M")
        except ValueError:
            console.print("❌ Formato de data/hora inválido. Use DD/MM/AAAA HH:MM")
            return

        # Cria novo atendimento
        atendimento = Atendimento(
            nome_paciente=nome,
            telefone=telefone,
            email=email,
            nome_medico=medico,
            especialidade=especialidade,
            data_consulta=data_obj,
            observacoes=observacoes,
            status=StatusConfirmacao.PENDENTE,
            criado_em=datetime.now(),
            atualizado_em=datetime.now(),
        )

        db.add(atendimento)
        db.commit()

        console.print(f"✅ Atendimento criado com sucesso! ID: {atendimento.id}")
        console.print(f"📋 Paciente: {nome}")
        console.print(f"👨‍⚕️ Médico: {medico}")
        console.print(f"🏥 Especialidade: {especialidade}")
        console.print(f"📅 Data: {data} às {hora}")

        # Cria subscriber no Botconversa
        console.print("🤖 Criando subscriber no Botconversa...")
        service = BotconversaService(db)
        
        try:
            # Separa nome em primeiro nome e sobrenome
            nome_parts = nome.split()
            primeiro_nome = nome_parts[0] if nome_parts else ""
            sobrenome = " ".join(nome_parts[1:]) if len(nome_parts) > 1 else "Silva"  # Fallback se não tiver sobrenome
            
            subscriber_result = service.criar_subscriber(telefone, primeiro_nome, sobrenome)
            if subscriber_result.get("success"):
                subscriber_id = subscriber_result.get("subscriber_id")
                # Atualiza atendimento com subscriber_id
                atendimento.subscriber_id = subscriber_id
                db.commit()
                console.print(f"✅ Subscriber criado com sucesso! ID: {subscriber_id}")
                
                # Executa workflow
                console.print("🔄 Executando workflow completo...")
                workflow_result = service.executar_workflow_consulta(atendimento.id)
                
                if workflow_result.get("success"):
                    console.print("🎉 Workflow executado com sucesso!")
                    console.print(f"📊 Resultado: {workflow_result}")
                else:
                    console.print(f"⚠️ Workflow executado com avisos: {workflow_result.get('message', 'N/A')}")
            else:
                console.print(f"❌ Erro ao criar subscriber: {subscriber_result.get('error')}")
                console.print("💡 Execute manualmente: python -m cli botconversa criar-subscriber --telefone {telefone} --nome {nome}")
        except Exception as e:
            console.print(f"⚠️ Erro ao executar workflow automático: {str(e)}")
            console.print("💡 Execute manualmente: python -m cli botconversa executar-workflow --atendimento-id {atendimento.id}")

    except Exception as e:
        console.print(f"❌ Erro: {str(e)}")
    finally:
        if db:
            try:
                db.close()
            except Exception:
                pass


@cli.group()
def botconversa():
    """Comandos relacionados ao Botconversa"""
    pass


@botconversa.command()
def test_conexao():
    """Testa conexão com Botconversa"""
    db = None
    try:
        from app.database.manager import get_db, initialize_database
        from app.services.botconversa_service import BotconversaService

        initialize_database()
        db = next(get_db())
        service = BotconversaService(db)

        resultado = service.testar_conexao()

        if resultado.get("success"):
            console.print("✅ Conexão com Botconversa: OK")
        else:
            console.print(f"❌ Erro: {resultado.get('message')}")

    except Exception as e:
        console.print(f"❌ Erro: {str(e)}")
    finally:
        if db:
            try:
                db.close()
            except Exception:
                pass


@botconversa.command()
@click.option("--telefone", required=True, help="Telefone do paciente")
@click.option("--nome", help="Nome completo do paciente (opcional)")
def criar_subscriber(telefone, nome):
    """Cria um subscriber no Botconversa"""
    db = None
    try:
        from app.database.manager import get_db, initialize_database
        from app.services.botconversa_service import BotconversaService

        initialize_database()
        db = next(get_db())
        service = BotconversaService(db)

        # Se não informou nome, busca no banco
        if not nome:
            from app.database.models import Paciente

            paciente = db.query(Paciente).filter(Paciente.telefone == telefone).first()
            if paciente:
                nome = paciente.nome
            else:
                nome = "Paciente"

        # Separa nome em primeiro nome e sobrenome
        nome_parts = nome.split()
        primeiro_nome = nome_parts[0] if nome_parts else ""
        sobrenome = " ".join(nome_parts[1:]) if len(nome_parts) > 1 else "Silva"  # Fallback se não tiver sobrenome

        resultado = service.criar_subscriber(telefone, primeiro_nome, sobrenome)

        if resultado:
            console.print(f"✅ Subscriber criado com sucesso! ID: {resultado.get('id')}")
        else:
            console.print("❌ Erro ao criar subscriber")

    except Exception as e:
        console.print(f"❌ Erro: {str(e)}")
    finally:
        if db:
            try:
                db.close()
            except Exception:
                pass


@botconversa.command()
@click.option("--subscriber-id", required=True, type=int, help="ID do subscriber")
@click.option("--mensagem", required=True, help="Mensagem a ser enviada")
def enviar_mensagem(subscriber_id, mensagem):
    """Envia mensagem para um subscriber"""
    db = None
    try:
        from app.database.manager import get_db, initialize_database
        from app.services.botconversa_service import BotconversaService

        initialize_database()
        db = next(get_db())
        service = BotconversaService(db)

        sucesso = service.enviar_mensagem(subscriber_id, mensagem)

        if sucesso:
            console.print(f"✅ Mensagem enviada com sucesso para subscriber {subscriber_id}")
        else:
            console.print("❌ Erro ao enviar mensagem")

    except Exception as e:
        console.print(f"❌ Erro: {str(e)}")
    finally:
        if db:
            try:
                db.close()
            except Exception:
                pass


@botconversa.command()
@click.option("--atendimento-id", required=True, type=int, help="ID do atendimento")
def executar_workflow(atendimento_id):
    """Executa workflow completo para uma consulta"""
    db = None
    try:
        from app.database.manager import get_db, initialize_database
        from app.services.botconversa_service import BotconversaService

        initialize_database()
        db = next(get_db())
        service = BotconversaService(db)

        resultado = service.executar_workflow_consulta(atendimento_id)

        if resultado.get("success"):
            console.print("✅ Workflow executado com sucesso!")
            console.print(f"📊 Resultado: {resultado}")
        else:
            console.print(f"❌ Erro no workflow: {resultado.get('error')}")

    except Exception as e:
        console.print(f"❌ Erro: {str(e)}")
    finally:
        if db:
            try:
                db.close()
            except Exception:
                pass


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

[bold]👥 Gerenciamento de Pacientes:[/bold]
  pacientes                 - Listar todos os pacientes
  criar-paciente            - Criar novo paciente

[bold]📋 Gerenciamento de Consultas:[/bold]
  consultas                 - Listar todas as consultas
  criar-consulta            - Criar nova consulta
  criar-atendimento         - Criar atendimento completo (paciente + consulta)
  criar-atendimento-completo - Criar atendimento completo e executar workflow

[bold]🏥 Gerenciamento de Atendimentos:[/bold]
  atendimentos              - Listar todos os atendimentos

[bold]🤖 Comandos Botconversa:[/bold]
  botconversa test-conexao  - Testar conexão com Botconversa
  botconversa criar-subscriber  - Criar subscriber no Botconversa
  botconversa enviar-mensagem    - Enviar mensagem para subscriber
  botconversa executar-workflow  - Executar workflow completo

[bold]🎯 Exemplos de Uso:[/bold]
  python -m cli status
  python -m cli pacientes
  python -m cli consultas
  python -m cli criar-paciente --nome "João Silva" --telefone 5531999629004
  python -m cli criar-consulta --paciente-id 1 --medico "Dr. Carlos" --especialidade "Cardiologia" --data "15/01/2024" --hora "14:30"
  python -m cli criar-atendimento --nome "João Silva" --telefone 5531999629004 --medico "Dr. Carlos" --especialidade "Cardiologia" --data "15/01/2024" --hora "14:30"
  python -m cli criar-atendimento-completo --nome "João Silva" --telefone 5531999629004 --medico "Dr. Carlos" --especialidade "Cardiologia" --data "15/01/2024" --hora "14:30"
  python -m cli botconversa test-conexao
  python -m cli botconversa criar-subscriber --telefone 5531999629004 --nome "João"
  python -m cli botconversa enviar-mensagem --subscriber-id 123 --mensagem "Olá! Confirme sua consulta."
  python -m cli botconversa executar-workflow --atendimento-id 1

[bold]💡 Dicas:[/bold]
  • Use --help após qualquer comando para ver opções detalhadas
  • O telefone deve estar no formato: 5531999629004
  • Data deve estar no formato: DD/MM/AAAA
  • Hora deve estar no formato: HH:MM
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
