import sys
from datetime import datetime

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from loguru import logger

from app.config.config import settings
from app.database.manager import create_tables, initialize_database
from app.database.sqlite_envios import init_sqlite
from app.scheduler import iniciar_scheduler, parar_scheduler

# Configuração de logs
logger.remove()
logger.add(sys.stdout, level=settings.log_level)
logger.add(
    "logs/app.log", rotation="1 day", retention="30 days", level=settings.log_level
)

# Criação da aplicação FastAPI
app = FastAPI(
    title=f"{settings.hospital_name or 'Hospital'} - Sistema de Confirmação de Consultas",
    description="Sistema de mensageria via Botconversa para confirmação de agendamentos médicos",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# Configuração de CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Inicialização do banco de dados
@app.on_event("startup")
async def startup_event():
    """Evento executado na inicialização da aplicação"""
    try:
        logger.info("Inicializando aplicação...")

        # Inicializa o banco de dados
        initialize_database()
        logger.info("Banco de dados inicializado")

        # Cria as tabelas da app só se configurado (use CREATE_APP_TABLES=false quando usar apenas view)
        if getattr(settings, "create_app_tables", True):
            create_tables()
            logger.info("Tabelas criadas/verificadas")
        else:
            logger.info("CREATE_APP_TABLES=false: pulando criação de tabelas (uso apenas view + agenda_consulta)")

        # Inicializa SQLite (controle de envios 48h/12h)
        try:
            init_sqlite()
            logger.info("SQLite de envios inicializado")
        except Exception as e:
            logger.warning(f"SQLite de envios não inicializado: {e}")

        # Inicia o scheduler
        if iniciar_scheduler():
            logger.info("Scheduler iniciado com sucesso")
        else:
            logger.warning("Erro ao iniciar scheduler")

        logger.info("Aplicação inicializada com sucesso!")

    except Exception as e:
        logger.error(f"Erro na inicialização: {str(e)}")
        raise e


@app.on_event("shutdown")
async def shutdown_event():
    """Evento executado no encerramento da aplicação"""
    logger.info("Encerrando aplicação...")

    # Para o scheduler
    if parar_scheduler():
        logger.info("Scheduler parado com sucesso")
    else:
        logger.warning("Erro ao parar scheduler")


# Middleware para logging de requisições
@app.middleware("http")
async def log_requests(request: Request, call_next):
    """Middleware para logging de requisições"""
    start_time = datetime.now()
    
    try:
        response = await call_next(request)
        process_time = (datetime.now() - start_time).total_seconds()
        
        logger.info(
            f"{request.method} {request.url.path} - {response.status_code} - {process_time:.3f}s"
        )
        
        return response
        
    except Exception as e:
        process_time = (datetime.now() - start_time).total_seconds()
        logger.error(f"Erro no middleware para {request.method} {request.url.path}: {str(e)}")
        logger.error(f"Tempo de processamento: {process_time:.3f}s")
        
        # Retorna erro 500 sem quebrar a aplicação
        return JSONResponse(
            status_code=500,
            content={"detail": "Erro interno do servidor"},
        )


# Tratamento de exceções
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Handler global para exceções não tratadas"""
    logger.error(f"Erro não tratado: {str(exc)}")
    return JSONResponse(
        status_code=500,
        content={"detail": "Erro interno do servidor"},
    )


@app.get("/")
async def root():
    """Endpoint raiz da aplicação"""
    hospital_name = settings.hospital_name or "Hospital"
    return {
        "message": f"Bem-vindo ao {hospital_name} - Sistema de Confirmação de Consultas",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/health",
    }


@app.get("/health")
async def health_check():
    """Endpoint para verificação de saúde da aplicação"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "version": "1.0.0",
    }


@app.get("/scheduler/status")
async def scheduler_status():
    """Endpoint para verificar o status do scheduler"""
    from app.scheduler import obter_status_scheduler

    return obter_status_scheduler()


# Inclusão dos routers
from app.api.routes.botconversa_test import router as botconversa_test_router
from app.api.routes.webhook import router as webhook_router

app.include_router(botconversa_test_router)
app.include_router(webhook_router)


if __name__ == "__main__":
    import uvicorn

    # Usa configurações do .env ou valores padrão
    host = getattr(settings, "webhook_host", "0.0.0.0")
    port = getattr(settings, "webhook_port", 8000)

    logger.info(f"Iniciando servidor em {host}:{port}")

    uvicorn.run(
        "app.main:app",
        host=host,
        port=port,
        reload=settings.debug,
        log_level=settings.log_level.lower(),
    )
