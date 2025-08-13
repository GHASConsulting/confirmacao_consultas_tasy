"""
Comandos relacionados ao banco de dados.
"""

import click
from loguru import logger


@click.command()
@click.option(
    "--database-type",
    "-t",
    type=click.Choice(["oracle", "postgresql", "firebird"]),
    help="Tipo de banco de dados para testar",
)
@click.option("--verbose", "-v", is_flag=True, help="Modo verboso")
@click.option("--create-tables", "-c", is_flag=True, help="Criar tabelas se não existirem")
def test_connection(database_type, verbose, create_tables):
    """
    Testa a conexão com o banco de dados configurado.

    Exemplos:
        python -m cli test-db
        python -m cli test-db --verbose
        python -m cli test-db --create-tables
    """
    try:
        from app.database.manager import (
            initialize_database,
            create_tables as create_db_tables,
            get_db,
        )
        from app.config.config import settings

        if verbose:
            logger.info("🔍 Iniciando teste de conexão com o banco de dados...")
            logger.info(f"📊 Tipo de banco configurado: {settings.database_type}")
            logger.info(f"🔗 URL do banco: {settings.get_database_url}")

        # Inicializa o banco
        if verbose:
            logger.info("🚀 Inicializando banco de dados...")
        initialize_database()

        if verbose:
            logger.info("✅ Banco de dados inicializado com sucesso!")

        # Cria as tabelas se solicitado
        if create_tables:
            if verbose:
                logger.info("🏗️ Criando tabelas...")
            create_db_tables()
            if verbose:
                logger.info("✅ Tabelas criadas com sucesso!")

        # Testa a conexão
        if verbose:
            logger.info("🔌 Testando conexão...")
        db = next(get_db())

        if verbose:
            logger.info("✅ Conexão estabelecida com sucesso!")

        # Fecha a conexão
        db.close()

        if verbose:
            logger.info("🔒 Conexão fechada com sucesso!")
            logger.info("🎉 Teste de conexão concluído com sucesso!")
        else:
            click.echo("✅ Conexão com banco de dados: OK")

        return True

    except Exception as e:
        if verbose:
            logger.error(f"❌ Erro ao testar conexão: {str(e)}")
        else:
            click.echo(f"❌ Erro: {str(e)}")
        return False
