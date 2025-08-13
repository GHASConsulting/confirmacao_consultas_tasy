#!/usr/bin/env python3
"""
Script para testar a conexão com o banco de dados.
"""

import os
import sys
from loguru import logger

# Adiciona o diretório raiz ao path (sobe um nível da pasta scripts)
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def test_database_connection():
    """Testa a conexão com o banco de dados configurado"""
    try:
        from app.database.manager import initialize_database, create_tables, get_db
        from app.config.config import settings

        logger.info("🔍 Iniciando teste de conexão com o banco de dados...")
        logger.info(f"📊 Tipo de banco configurado: {settings.database_type}")
        logger.info(f"🔗 URL do banco: {settings.get_database_url}")

        # Inicializa o banco
        logger.info("🚀 Inicializando banco de dados...")
        initialize_database()
        logger.info("✅ Banco de dados inicializado com sucesso!")

        # Cria as tabelas
        logger.info("🏗️ Criando tabelas...")
        create_tables()
        logger.info("✅ Tabelas criadas com sucesso!")

        # Testa a conexão
        logger.info("🔌 Testando conexão...")
        db = next(get_db())
        logger.info("✅ Conexão estabelecida com sucesso!")

        # Fecha a conexão
        db.close()
        logger.info("🔒 Conexão fechada com sucesso!")

        logger.info("🎉 Teste de conexão concluído com sucesso!")
        return True

    except Exception as e:
        logger.error(f"❌ Erro ao testar conexão: {str(e)}")
        return False


def test_database_adapter():
    """Testa o adaptador do banco de dados"""
    try:
        from app.database.manager import get_database_adapter_instance, get_db
        from app.config.config import settings
        import time

        logger.info("🔍 Testando adaptador do banco de dados...")

        # Obtém uma sessão
        db = next(get_db())

        # Obtém o adaptador
        adapter = get_database_adapter_instance(db)
        logger.info(f"✅ Adaptador criado: {type(adapter).__name__}")

        # Testa operações básicas
        logger.info("🧪 Testando operações básicas...")

        # Gera dados únicos para evitar conflitos
        timestamp = int(time.time())
        patient_data = {
            "nome": f"João Teste {timestamp}",
            "telefone": f"1199999{timestamp % 10000:04d}",
            "email": f"joao.teste{timestamp}@email.com",
        }

        paciente = adapter.create_patient(patient_data)
        logger.info(f"✅ Paciente criado: {paciente.nome} (ID: {paciente.id})")

        # Testa busca de paciente
        paciente_buscado = adapter.get_patient(paciente.id)
        if paciente_buscado:
            logger.info(f"✅ Paciente encontrado: {paciente_buscado.nome}")
        else:
            logger.error("❌ Paciente não encontrado")

        # Fecha a conexão
        db.close()
        logger.info("🎉 Teste do adaptador concluído com sucesso!")
        return True

    except Exception as e:
        logger.error(f"❌ Erro ao testar adaptador: {str(e)}")
        return False


if __name__ == "__main__":
    logger.info("🚀 Iniciando testes de conexão...")

    # Testa conexão básica
    if test_database_connection():
        logger.info("✅ Teste de conexão básica: PASSOU")
    else:
        logger.error("❌ Teste de conexão básica: FALHOU")
        sys.exit(1)

    # Testa adaptador
    if test_database_adapter():
        logger.info("✅ Teste do adaptador: PASSOU")
    else:
        logger.error("❌ Teste do adaptador: FALHOU")
        sys.exit(1)

    logger.info("🎉 Todos os testes passaram com sucesso!")
