#!/usr/bin/env python3
"""
Script para adicionar dados de teste no banco de dados.
"""

import sys
import os
from datetime import datetime, timedelta

# Adiciona o diretório raiz ao path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database.manager import get_db, initialize_database, create_tables
from app.database.models import Paciente, Consulta, StatusConfirmacao


def add_test_data():
    """Adiciona dados de teste no banco de dados."""

    print("🚀 Adicionando dados de teste...")

    # Inicializa o banco
    initialize_database()
    create_tables()

    # Obtém sessão
    db = next(get_db())

    try:
        # Verifica se já existe paciente
        paciente = (
            db.query(Paciente).filter(Paciente.telefone == "5531999629004").first()
        )

        if not paciente:
            # Cria paciente
            paciente = Paciente(
                nome="João Silva",
                telefone="5531999629004",
                email="joao.silva@email.com",
            )
            db.add(paciente)
            db.commit()
            print("✅ Paciente João Silva criado")
        else:
            print("ℹ️ Paciente João Silva já existe")

        # Verifica se já existe consulta
        consulta = (
            db.query(Consulta)
            .filter(
                Consulta.paciente_id == paciente.id,
                Consulta.status == StatusConfirmacao.PENDENTE,
            )
            .first()
        )

        if not consulta:
            # Cria consulta
            consulta = Consulta(
                paciente_id=paciente.id,
                nome_medico="Dr. Maria Santos",
                especialidade="Cardiologia",
                data_consulta=datetime.now() + timedelta(days=2),
                status=StatusConfirmacao.PENDENTE,
                observacoes="Consulta de rotina",
            )
            db.add(consulta)
            db.commit()
            print("✅ Consulta criada")
        else:
            print("ℹ️ Consulta já existe")

        print("\n🎯 Dados de teste adicionados com sucesso!")
        print(f"📞 Telefone: {paciente.telefone}")
        print(f"👤 Nome: {paciente.nome}")
        print(f"👨‍⚕️ Médico: {consulta.nome_medico}")
        print(f"🏥 Especialidade: {consulta.especialidade}")
        print(f"📅 Data: {consulta.data_consulta.strftime('%d/%m/%Y')}")
        print(f"⏰ Hora: {consulta.data_consulta.strftime('%H:%M')}")

    except Exception as e:
        print(f"❌ Erro ao adicionar dados: {str(e)}")
        db.rollback()
    finally:
        db.close()


if __name__ == "__main__":
    add_test_data()
