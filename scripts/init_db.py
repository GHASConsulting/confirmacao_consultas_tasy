#!/usr/bin/env python3
"""
Script para inicializar o banco de dados.
Cria as tabelas e insere dados de exemplo se necessário.
"""

import os
import sys
from loguru import logger

# Adiciona o diretório raiz ao path (sobe um nível da pasta scripts)
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def init_database():
    """Inicializa banco com dados de exemplo"""
    try:
        from app.database.manager import initialize_database, create_tables, get_db
        from app.database.models import Paciente, Consulta, Confirmacao
        from app.config.config import settings
        from datetime import datetime, timedelta

        logger.info("🔍 Iniciando inicialização do banco de dados...")
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

        # Obtém uma sessão para verificar dados
        db = next(get_db())

        try:
            # Verifica se já existem dados
            if db.query(Paciente).count() == 0:
                logger.info("📝 Criando dados de exemplo...")
                
                # Cria pacientes de exemplo
                pacientes = [
                    Paciente(
                        nome="João Silva",
                        telefone="11999999999",
                        email="joao@email.com"
                    ),
                    Paciente(
                        nome="Maria Santos",
                        telefone="11888888888",
                        email="maria@email.com"
                    ),
                ]

                for paciente in pacientes:
                    db.add(paciente)

                db.commit()
                logger.info("✅ Pacientes de exemplo criados")

                # Cria consultas de exemplo
                consultas = [
                    Consulta(
                        paciente_id=1,
                        data_consulta=datetime.utcnow() + timedelta(days=3),
                        medico="Dr. Carlos",
                        especialidade="Cardiologia",
                        status="agendada"
                    ),
                    Consulta(
                        paciente_id=2,
                        data_consulta=datetime.utcnow() + timedelta(days=2),
                        medico="Dra. Ana",
                        especialidade="Dermatologia",
                        status="agendada"
                    ),
                ]

                for consulta in consultas:
                    db.add(consulta)

                db.commit()
                logger.info("✅ Consultas de exemplo criadas")
                
                logger.info("✅ Dados de exemplo criados com sucesso!")
            else:
                logger.info("✅ Banco já possui dados")

        finally:
            # Fecha a conexão
            db.close()

        logger.info("🎉 Inicialização do banco concluída com sucesso!")
        return True

    except Exception as e:
        logger.error(f"❌ Erro ao inicializar banco: {str(e)}")
        return False


if __name__ == "__main__":
    logger.info("🚀 Iniciando script de inicialização do banco...")
    
    success = init_database()
    
    if success:
        logger.info("✅ Script executado com sucesso!")
        sys.exit(0)
    else:
        logger.error("❌ Script falhou!")
        sys.exit(1)
