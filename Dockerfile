# Multi-stage build para otimizar o tamanho da imagem
FROM python:3.11-slim as builder

# Instalar dependências do sistema necessárias para build
RUN apt-get update && apt-get install -y \
    build-essential \
    libaio1t64 \
    unzip \
    wget \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Criar diretório para o Oracle Instant Client
RUN mkdir -p /opt/oracle

# Baixar e instalar o Oracle Instant Client 21.17
RUN cd /tmp && \
    wget https://download.oracle.com/otn_software/linux/instantclient/2117000/instantclient-basic-linux.x64-21.17.0.0.0dbru.zip && \
    unzip instantclient-basic-linux.x64-21.17.0.0.0dbru.zip && \
    mkdir -p /opt/oracle && \
    mv instantclient_21_17 /opt/oracle/ && \
    rm instantclient-basic-linux.x64-21.17.0.0.0dbru.zip

# Configurar variáveis de ambiente Oracle
ENV ORACLE_HOME=/opt/oracle/instantclient_21_17
ENV LD_LIBRARY_PATH=/opt/oracle/instantclient_21_17
ENV PATH=/opt/oracle/instantclient_21_17:$PATH

# Instalar dependências Python
COPY requirements.txt .
RUN pip install --no-cache-dir --user -r requirements.txt

# Estágio final - imagem de produção
FROM python:3.11-slim

# Instalar apenas dependências de runtime
RUN apt-get update && apt-get install -y \
    libaio1t64 \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copiar Oracle Instant Client do estágio builder
COPY --from=builder /opt/oracle/instantclient_21_17 /opt/oracle/instantclient_21_17

# Copiar dependências Python do estágio builder para o sistema
COPY --from=builder /root/.local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=builder /root/.local/bin /usr/local/bin

# Configurar variáveis de ambiente Oracle
ENV ORACLE_HOME=/opt/oracle/instantclient_21_17
ENV LD_LIBRARY_PATH=/opt/oracle/instantclient_21_17
ENV PATH=/opt/oracle/instantclient_21_17:$PATH

# Criar usuário não-root para segurança
RUN useradd --create-home --shell /bin/bash app

# Definir diretório de trabalho
WORKDIR /app

# Copiar código da aplicação
COPY --chown=app:app app/ ./app/
COPY --chown=app:app cli/ ./cli/

# Criar diretórios de logs e dados (SQLite)
RUN mkdir -p logs data && chown -R app:app logs data

# Mudar para usuário não-root
USER app

# Expor porta da aplicação
EXPOSE 5001

# Comando para iniciar a aplicação
CMD ["python", "-m", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "5001"]
