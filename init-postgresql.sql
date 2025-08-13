-- Script de inicialização PostgreSQL para Docker
-- Cria o schema SantaCasa e as tabelas necessárias

-- Cria o schema SantaCasa
CREATE SCHEMA IF NOT EXISTS "SantaCasa";

-- Cria o enum StatusConfirmacao
CREATE TYPE IF NOT EXISTS "SantaCasa".statusconfirmacao AS ENUM (
    'PENDENTE',
    'CONFIRMADO', 
    'CANCELADO',
    'SEM_RESPOSTA'
);

-- Cria a tabela atendimentos
CREATE TABLE IF NOT EXISTS "SantaCasa".atendimentos (
    id SERIAL PRIMARY KEY,
    nome_paciente VARCHAR(100) NOT NULL,
    telefone VARCHAR(20) NOT NULL,
    email VARCHAR(100),
    data_consulta TIMESTAMP WITH TIME ZONE NOT NULL,
    nome_medico VARCHAR(100),
    especialidade VARCHAR(100),
    status_confirmacao "SantaCasa".statusconfirmacao DEFAULT 'PENDENTE',
    
    -- Campos de controle para Botconversa
    subscriber_id INTEGER UNIQUE,
    mensagem_enviada TEXT,
    resposta_paciente VARCHAR(10),
    respondido_em TIMESTAMP WITH TIME ZONE,
    
    -- Controle de frequência de lembretes
    lembrete_48h_enviado BOOLEAN DEFAULT FALSE,
    lembrete_12h_enviado BOOLEAN DEFAULT FALSE,
    ultimo_lembrete_enviado TIMESTAMP WITH TIME ZONE,
    tipo_ultimo_lembrete VARCHAR(10),
    
    -- Timestamps
    criado_em TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    atualizado_em TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Cria índices para melhor performance
CREATE INDEX IF NOT EXISTS idx_atendimentos_subscriber_id ON "SantaCasa".atendimentos(subscriber_id);
CREATE INDEX IF NOT EXISTS idx_atendimentos_status ON "SantaCasa".atendimentos(status_confirmacao);
CREATE INDEX IF NOT EXISTS idx_atendimentos_data_consulta ON "SantaCasa".atendimentos(data_consulta);
CREATE INDEX IF NOT EXISTS idx_atendimentos_telefone ON "SantaCasa".atendimentos(telefone);

-- Insere dados de exemplo (opcional)
INSERT INTO "SantaCasa".atendimentos (
    nome_paciente, 
    telefone, 
    email, 
    data_consulta, 
    nome_medico, 
    especialidade
) VALUES 
    ('João Silva', '5511999999999', 'joao@email.com', NOW() + INTERVAL '3 days', 'Dr. Carlos', 'Cardiologia'),
    ('Maria Santos', '5511888888888', 'maria@email.com', NOW() + INTERVAL '2 days', 'Dra. Ana', 'Dermatologia')
ON CONFLICT DO NOTHING;

-- Comentários para documentação
COMMENT ON SCHEMA "SantaCasa" IS 'Schema para dados da Santa Casa de Belo Horizonte';
COMMENT ON TABLE "SantaCasa".atendimentos IS 'Tabela de atendimentos médicos com controle de confirmação via WhatsApp';
COMMENT ON COLUMN "SantaCasa".atendimentos.subscriber_id IS 'ID do subscriber no Botconversa';
COMMENT ON COLUMN "SantaCasa".atendimentos.status_confirmacao IS 'Status da confirmação da consulta';
