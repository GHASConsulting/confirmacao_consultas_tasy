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
@click.option("--todos", is_flag=True, help="Mostrar todos os atendimentos (não apenas pendentes)")
@click.option("--status", help="Filtrar por status específico (PENDENTE, CONFIRMADO, CANCELADO)")
def listar_atendimentos(todos, status):
    """Lista atendimentos com informações detalhadas"""
    try:
        from app.database.manager import initialize_database, get_db
        from app.services.botconversa_service import BotconversaService
        from app.database.models import Atendimento

        initialize_database()
        db = next(get_db())
        service = BotconversaService(db)

        # Busca atendimentos baseado nos filtros
        if todos:
            if status:
                atendimentos = db.query(Atendimento).filter(Atendimento.status == status).all()
            else:
                atendimentos = db.query(Atendimento).all()
        else:
            atendimentos = service.listar_atendimentos_pendentes()

        if not atendimentos:
            console.print("📭 Nenhum atendimento encontrado")
            return

        # Tabela principal com campos essenciais
        table = Table(title="📋 Atendimentos - Visão Geral")
        table.add_column("ID", style="cyan", width=5)
        table.add_column("Paciente", style="green", width=20)
        table.add_column("Telefone", style="blue", width=15)
        table.add_column("Médico", style="yellow", width=20)
        table.add_column("Especialidade", style="magenta", width=15)
        table.add_column("Data", style="white", width=15)
        table.add_column("Status", style="red", width=12)
        table.add_column("Subscriber ID", style="cyan", width=12)

        for a in atendimentos:
            # Formata o subscriber_id
            subscriber_display = str(a.subscriber_id) if a.subscriber_id else "N/A"
            
            # Formata a data
            data_display = a.data_consulta.strftime("%d/%m/%Y %H:%M") if a.data_consulta else "N/A"
            
            # Formata o status com cores
            status_display = a.status.value if a.status else "N/A"
            
            table.add_row(
                str(a.id),
                a.nome_paciente[:18] + "..." if len(a.nome_paciente) > 18 else a.nome_paciente,
                a.telefone,
                a.nome_medico[:18] + "..." if len(a.nome_medico) > 18 else a.nome_medico,
                a.especialidade[:14] + "..." if len(a.especialidade) > 14 else a.especialidade,
                data_display,
                status_display,
                subscriber_display,
            )

        console.print(table)
        
        # Estatísticas
        total = len(atendimentos)
        pendentes = len([a for a in atendimentos if a.status and a.status.value == "PENDENTE"])
        confirmados = len([a for a in atendimentos if a.status and a.status.value == "CONFIRMADO"])
        cancelados = len([a for a in atendimentos if a.status and a.status.value == "CANCELADO"])
        
        console.print(f"\n📊 Estatísticas:")
        console.print(f"   Total: {total}")
        console.print(f"   Pendentes: {pendentes}")
        console.print(f"   Confirmados: {confirmados}")
        console.print(f"   Cancelados: {cancelados}")
        
        # Comandos úteis
        console.print(f"\n💡 Comandos úteis:")
        console.print(f"   python -m cli listar-atendimentos --todos")
        console.print(f"   python -m cli listar-atendimentos --status PENDENTE")
        console.print(f"   python -m cli buscar-atendimento --telefone 5531999629004")
        
        db.close()

    except Exception as e:
        console.print(f"❌ Erro: {str(e)}")
        console.print(f"💡 Dica: Verifique se o banco está conectado")


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
            console.print(f"🏷️ Etiqueta 'subscriber_id' adicionada automaticamente", style="blue")
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


@click.command()
@click.option(
    "--telefone", required=True, help="Telefone do paciente no formato 5531999629004"
)
def adicionar_etiqueta(telefone):
    """
    Adiciona etiqueta 'subscriber_id' a um contato existente no Botconversa.

    Este comando é útil para adicionar a etiqueta em contatos que foram criados
    antes da implementação automática de etiquetas.

    Exemplo:
    python -m cli adicionar-etiqueta --telefone 5531999629004
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
        console.print(f"📱 Telefone: {atendimento.telefone}")

        # Adicionar etiqueta subscriber_id
        console.print("🏷️ Adicionando etiqueta 'subscriber_id' ao contato...")

        sucesso = service.adicionar_etiqueta_subscriber(atendimento.subscriber_id)

        if sucesso:
            console.print(
                f"✅ Etiqueta 'subscriber_id' adicionada com sucesso!", style="green"
            )
            console.print(f"👤 Paciente: {atendimento.nome_paciente}")
            console.print(f"🆔 Subscriber ID: {atendimento.subscriber_id}")
            console.print(f"🏷️ Etiqueta: subscriber_id (ID: 15362464)")
        else:
            console.print(f"❌ Erro ao adicionar etiqueta", style="red")
            console.print(f"💡 Verifique se o subscriber ainda existe no Botconversa")

        db.close()

    except Exception as e:
        console.print(f"❌ Erro ao adicionar etiqueta: {str(e)}", style="red")

@click.command()
@click.option(
    "--telefone", required=True, help="Telefone do paciente no formato 5531999629004"
)
@click.option(
    "--valor", help="Valor a ser salvo no campo personalizado (se não informado, usa o subscriber_id)"
)
def adicionar_campo_personalizado(telefone, valor):
    """
    Adiciona valor ao campo personalizado 'subscriber_id' de um contato existente no Botconversa.
    Este comando é útil para adicionar o campo personalizado em contatos que foram criados
    antes da implementação automática de campos personalizados.
    Exemplo:
    python -m cli adicionar-campo-personalizado --telefone 5531999629004
    python -m cli adicionar-campo-personalizado --telefone 5531999629004 --valor 12345
    """
    try:
        from app.database.manager import initialize_database, get_db
        from app.services.botconversa_service import BotconversaService
        from app.database.models import Atendimento
        initialize_database()
        db = next(get_db())
        service = BotconversaService(db)
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
        console.print(f"📱 Telefone: {atendimento.telefone}")
        
        # Define o valor a ser salvo
        valor_campo = valor if valor else str(atendimento.subscriber_id)
        console.print(f"📝 Valor a ser salvo: {valor_campo}")
        
        console.print("📝 Adicionando campo personalizado 'subscriber_id' ao contato...")
        sucesso = service.adicionar_campo_personalizado(atendimento.subscriber_id, valor=valor_campo)
        if sucesso:
            console.print(
                f"✅ Campo personalizado 'subscriber_id' adicionado com sucesso!", style="green"
            )
            console.print(f"👤 Paciente: {atendimento.nome_paciente}")
            console.print(f"🆔 Subscriber ID: {atendimento.subscriber_id}")
            console.print(f"📝 Campo: subscriber_id (ID: 4336343)")
            console.print(f"💾 Valor salvo: {valor_campo}")
        else:
            console.print(f"❌ Erro ao adicionar campo personalizado", style="red")
            console.print(f"💡 Verifique se o subscriber ainda existe no Botconversa")
        db.close()
    except Exception as e:
        console.print(f"❌ Erro ao adicionar campo personalizado: {str(e)}", style="red")
