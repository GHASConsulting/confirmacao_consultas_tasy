"""
Comandos CLI para Botconversa
"""

import click
from rich.console import Console  # type: ignore
from rich.table import Table  # type: ignore
from datetime import datetime

# Importações serão feitas dentro das funções para evitar problemas de módulo

console = Console()


@click.command()
def test_conexao():
    """Testa conexão com Botconversa"""
    try:
        from app.database.manager import initialize_database, get_db
        from app.services.botconversa_service import BotconversaService

        initialize_database()
        db = next(get_db())
        service = BotconversaService(db)

        resultado = service.testar_conexao()

        if resultado.get("success"):
            console.print("✅ Conexão com Botconversa: OK")
        else:
            console.print(f"❌ Erro: {resultado.get('message')}")

        db.close()

    except Exception as e:
        console.print(f"❌ Erro: {str(e)}")


@click.command()
def listar_atendimentos():
    """Lista todos os atendimentos"""
    try:
        from app.database.manager import initialize_database, get_db
        from app.services.botconversa_service import BotconversaService

        initialize_database()
        db = next(get_db())
        service = BotconversaService(db)

        atendimentos = service.listar_atendimentos_pendentes()

        if not atendimentos:
            console.print("📭 Nenhum atendimento encontrado")
            return

        table = Table(title="📋 Atendimentos")
        table.add_column("ID", style="cyan")
        table.add_column("Paciente", style="green")
        table.add_column("Telefone", style="blue")
        table.add_column("Médico", style="yellow")
        table.add_column("Data", style="magenta")
        table.add_column("Status", style="red")

        for a in atendimentos:
            table.add_row(
                str(a.id),
                a.nome_paciente,
                a.telefone,
                a.nome_medico,
                a.data_consulta.strftime("%d/%m/%Y %H:%M"),
                a.status.value,
            )

        console.print(table)
        db.close()

    except Exception as e:
        console.print(f"❌ Erro: {str(e)}")


@click.command()
@click.option("--telefone", required=True, help="Telefone do paciente")
def buscar_atendimento(telefone):
    """Busca atendimento por telefone"""
    try:
        from app.database.manager import initialize_database, get_db
        from app.services.botconversa_service import BotconversaService

        initialize_database()
        db = next(get_db())
        service = BotconversaService(db)

        atendimento = service.buscar_atendimento_por_telefone(telefone)

        if not atendimento:
            console.print(f"📭 Atendimento não encontrado para telefone: {telefone}")
            return

        console.print(
            f"ID: {atendimento.id}\n"
            f"Paciente: {atendimento.nome_paciente}\n"
            f"Telefone: {atendimento.telefone}\n"
            f"Médico: {atendimento.nome_medico}\n"
            f"Especialidade: {atendimento.especialidade}\n"
            f"Data: {atendimento.data_consulta.strftime('%d/%m/%Y %H:%M')}\n"
            f"Status: {atendimento.status.value}\n"
            f"Subscriber ID: {atendimento.subscriber_id}"
        )

        db.close()

    except Exception as e:
        console.print(f"❌ Erro: {str(e)}")


@click.command()
@click.option("--telefone", required=True, help="Telefone do paciente")
def enviar_mensagem(telefone):
    """Envia mensagem para paciente"""
    try:
        from app.database.manager import initialize_database, get_db
        from app.services.botconversa_service import BotconversaService

        initialize_database()
        db = next(get_db())
        service = BotconversaService(db)

        atendimento = service.buscar_atendimento_por_telefone(telefone)

        if not atendimento:
            console.print(f"📭 Atendimento não encontrado para telefone: {telefone}")
            return

        console.print(f"📤 Enviando mensagem para {atendimento.nome_paciente}...")

        resultado = service.enviar_mensagem_consulta(atendimento)

        if resultado:
            console.print("✅ Mensagem enviada com sucesso!")
        else:
            console.print("❌ Erro ao enviar mensagem")

        db.close()

    except Exception as e:
        console.print(f"❌ Erro: {str(e)}")


@click.command()
@click.option("--id", required=True, type=int, help="ID do atendimento")
def executar_workflow(id):
    """Executa workflow completo"""
    try:
        from app.database.manager import initialize_database, get_db
        from app.services.botconversa_service import BotconversaService

        initialize_database()
        db = next(get_db())
        service = BotconversaService(db)

        console.print(f"🚀 Executando workflow para atendimento {id}...")

        resultado = service.executar_workflow_consulta(id)

        if resultado.get("success"):
            console.print("✅ Workflow executado com sucesso!")
            console.print(f"📊 Resultado: {resultado}")
        else:
            console.print(f"❌ Erro: {resultado.get('error')}")

        db.close()

    except Exception as e:
        console.print(f"❌ Erro: {str(e)}")


@click.command()
@click.option("--telefone", required=True, help="Telefone do paciente")
@click.option("--resposta", required=True, help="Resposta (1=SIM, 0=NÃO)")
def processar_resposta(telefone, resposta):
    """Processa resposta do paciente"""
    try:
        from app.database.manager import initialize_database, get_db
        from app.services.botconversa_service import BotconversaService

        initialize_database()
        db = next(get_db())
        service = BotconversaService(db)

        console.print(
            f"📝 Processando resposta '{resposta}' para telefone {telefone}..."
        )

        resultado = service.processar_resposta_paciente(telefone, resposta)

        if resultado:
            console.print("✅ Resposta processada com sucesso!")
        else:
            console.print("❌ Erro ao processar resposta")

        db.close()

    except Exception as e:
        console.print(f"❌ Erro: {str(e)}")


@click.command()
@click.option("--nome", required=True, help="Nome completo do paciente")
@click.option("--telefone", required=True, help="Telefone no formato 5531999629004")
@click.option("--medico", required=True, help="Nome do médico")
@click.option("--especialidade", required=True, help="Especialidade médica")
@click.option("--data", required=True, help="Data da consulta (DD/MM/AAAA)")
@click.option("--hora", required=True, help="Horário da consulta (HH:MM)")
@click.option("--observacoes", help="Observações adicionais")
def criar_atendimento(nome, telefone, medico, especialidade, data, hora, observacoes):
    """
    Cria um novo atendimento no banco de dados.

    Exemplo:
    python -m cli criar-atendimento --nome "João Silva" --telefone 5531999629004 --medico "Dr. Carlos" --especialidade "Cardiologia" --data "15/08/2025" --hora "14:00"
    """
    try:
        from app.database.manager import initialize_database, get_db
        from app.database.models import Atendimento, StatusConfirmacao

        # Validar formato do telefone
        if not telefone.startswith("55") or len(telefone) < 12:
            console.print(
                "❌ Telefone deve estar no formato 5531999629004", style="red"
            )
            return

        # Converter data e hora
        try:
            data_obj = datetime.strptime(f"{data} {hora}", "%d/%m/%Y %H:%M")
        except ValueError:
            console.print(
                "❌ Formato de data/hora inválido. Use DD/MM/AAAA HH:MM", style="red"
            )
            return

        # Inicializar banco e criar atendimento
        initialize_database()
        db = next(get_db())

        novo_atendimento = Atendimento(
            nome_paciente=nome,
            telefone=telefone,
            nome_medico=medico,
            especialidade=especialidade,
            data_consulta=data_obj,
            observacoes=observacoes,
            status=StatusConfirmacao.PENDENTE,
            criado_em=datetime.now(),
            atualizado_em=datetime.now(),
        )

        db.add(novo_atendimento)
        db.commit()
        db.refresh(novo_atendimento)

        console.print(f"✅ Atendimento criado com sucesso!", style="green")
        console.print(f"📋 ID: {novo_atendimento.id}")
        console.print(f"👤 Paciente: {novo_atendimento.nome_paciente}")
        console.print(f"📱 Telefone: {novo_atendimento.telefone}")
        console.print(f"👨‍⚕️ Médico: {novo_atendimento.nome_medico}")
        console.print(f"🏥 Especialidade: {novo_atendimento.especialidade}")
        console.print(
            f"📅 Data: {novo_atendimento.data_consulta.strftime('%d/%m/%Y %H:%M')}"
        )
        console.print(f"📊 Status: {novo_atendimento.status.value}")

        db.close()

    except Exception as e:
        console.print(f"❌ Erro ao criar atendimento: {str(e)}", style="red")


@click.command()
@click.option(
    "--telefone", required=True, help="Telefone do paciente no formato 5531999629004"
)
@click.option("--nome", help="Nome do paciente (opcional, será buscado no banco)")
def adicionar_botconversa(telefone, nome):
    """
    Adiciona um paciente no Botconversa (cria subscriber).

    Exemplo:
    python -m cli adicionar-botconversa --telefone 5531999629004
    """
    try:
        from app.database.manager import initialize_database, get_db
        from app.services.botconversa_service import BotconversaService
        from app.database.models import Atendimento

        initialize_database()
        db = next(get_db())
        service = BotconversaService(db)

        # Buscar atendimento no banco
        atendimento = (
            db.query(Atendimento).filter(Atendimento.telefone == telefone).first()
        )

        if not atendimento:
            console.print(
                f"❌ Atendimento não encontrado para telefone: {telefone}", style="red"
            )
            return

        console.print(f"🔍 Encontrado atendimento: {atendimento.nome_paciente}")
        console.print(f"📱 Telefone: {atendimento.telefone}")

        # Criar subscriber no Botconversa
        console.print("📡 Criando subscriber no Botconversa...")

        # Usar o método do serviço para criar subscriber
        subscriber_info = service.criar_subscriber(
            telefone=atendimento.telefone,
            nome=atendimento.nome_paciente.split()[0],  # Primeiro nome
            sobrenome=(
                " ".join(atendimento.nome_paciente.split()[1:])
                if len(atendimento.nome_paciente.split()) > 1
                else ""
            ),
        )

        if subscriber_info and subscriber_info.get("id"):
            subscriber_id = subscriber_info.get("id")

            # Atualizar atendimento com subscriber_id
            atendimento.subscriber_id = subscriber_id
            atendimento.atualizado_em = datetime.now()
            db.commit()

            console.print(
                f"✅ Subscriber criado com sucesso no Botconversa!", style="green"
            )
            console.print(f"🆔 Subscriber ID: {subscriber_id}")
            console.print(f"👤 Nome: {subscriber_info.get('full_name')}")
            console.print(f"📱 Telefone: {subscriber_info.get('phone')}")
            console.print(f"📊 Status: {subscriber_info.get('status', 'N/A')}")
        else:
            console.print("❌ Erro ao criar subscriber no Botconversa", style="red")
            if subscriber_info:
                console.print(f"Resposta: {subscriber_info}")

        db.close()

    except Exception as e:
        console.print(f"❌ Erro ao adicionar no Botconversa: {str(e)}", style="red")


@click.command()
@click.option(
    "--telefone", required=True, help="Telefone do paciente no formato 5531999629004"
)
@click.option("--campanha-id", help="ID da campanha (padrão: Confirmação de Consultas)")
def adicionar_campanha(telefone, campanha_id):
    """
    Adiciona um paciente na campanha do Botconversa.

    Exemplo:
    python -m cli adicionar-campanha --telefone 5531999629004
    """
    try:
        from app.database.manager import initialize_database, get_db
        from app.services.botconversa_service import BotconversaService
        from app.database.models import Atendimento

        initialize_database()
        db = next(get_db())
        service = BotconversaService(db)

        # Buscar atendimento no banco
        atendimento = (
            db.query(Atendimento).filter(Atendimento.telefone == telefone).first()
        )

        if not atendimento:
            console.print(
                f"❌ Atendimento não encontrado para telefone: {telefone}", style="red"
            )
            return

        if not atendimento.subscriber_id:
            console.print(
                f"❌ Paciente não está no Botconversa. Execute 'adicionar-botconversa' primeiro.",
                style="red",
            )
            return

        console.print(f"🔍 Encontrado atendimento: {atendimento.nome_paciente}")
        console.print(f"🆔 Subscriber ID: {atendimento.subscriber_id}")

        # Se não foi especificado campanha_id, buscar a campanha "Confirmação de Consultas"
        if not campanha_id:
            console.print("🔍 Buscando campanha 'Confirmação de Consultas'...")
            campanhas = service.listar_campanhas()

            if not campanhas:
                console.print("❌ Nenhuma campanha encontrada", style="red")
                return

            # Procurar pela campanha de confirmação
            campanha_confirma = None
            for campanha in campanhas:
                if (
                    "confirmação" in campanha.get("name", "").lower()
                    or "consulta" in campanha.get("name", "").lower()
                ):
                    campanha_confirma = campanha
                    break

            if not campanha_confirma:
                console.print(
                    "❌ Campanha 'Confirmação de Consultas' não encontrada", style="red"
                )
                console.print("📋 Campanhas disponíveis:")
                for camp in campanhas:
                    console.print(f"   - {camp.get('name')} (ID: {camp.get('id')})")
                return

            campanha_id = campanha_confirma["id"]
            console.print(
                f"🎯 Campanha encontrada: {campanha_confirma['name']} (ID: {campanha_id})"
            )

        # Adicionar subscriber à campanha
        console.print(
            f"📡 Adicionando subscriber {atendimento.subscriber_id} à campanha {campanha_id}..."
        )

        sucesso = service.adicionar_subscriber_campanha(
            atendimento.subscriber_id, campanha_id
        )

        if sucesso:
            console.print(
                f"✅ Subscriber adicionado à campanha com sucesso!", style="green"
            )
            console.print(f"👤 Paciente: {atendimento.nome_paciente}")
            console.print(f"🆔 Subscriber ID: {atendimento.subscriber_id}")
            console.print(f"🎯 Campanha ID: {campanha_id}")
        else:
            console.print(f"❌ Erro ao adicionar subscriber à campanha", style="red")

        db.close()

    except Exception as e:
        console.print(f"❌ Erro ao adicionar na campanha: {str(e)}", style="red")
