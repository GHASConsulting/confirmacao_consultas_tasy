-- Script de inicialização PostgreSQL para Docker
-- Cria a tabela ghas_tbl_pac_agendados para diferentes clientes

-- Cria o enum StatusConfirmacao
CREATE TYPE IF NOT EXISTS statusconfirmacao AS ENUM (
    'PENDENTE',
    'CONFIRMADO', 
    'CANCELADO',
    'SEM_RESPOSTA'
);

-- Cria a tabela ghas_tbl_pac_agendados
CREATE TABLE IF NOT EXISTS ghas_tbl_pac_agendados (
    id SERIAL PRIMARY KEY,
    nome_paciente VARCHAR(100) NOT NULL,
    telefone VARCHAR(20) NOT NULL,
    email VARCHAR(100),
    data_consulta TIMESTAMP WITH TIME ZONE NOT NULL,
    nome_medico VARCHAR(100),
    especialidade VARCHAR(100),
    status statusconfirmacao DEFAULT 'PENDENTE',
    
    -- Campos de controle para Botconversa
    subscriber_id INTEGER UNIQUE,
    mensagem_enviada TEXT,
    resposta_paciente VARCHAR(10),
    interpretacao_resposta VARCHAR(50),
    respondido_em TIMESTAMP WITH TIME ZONE,
    
    -- Controle de frequência de lembretes
    lembrete_48h_enviado BOOLEAN DEFAULT FALSE,
    lembrete_12h_enviado BOOLEAN DEFAULT FALSE,
    ultimo_lembrete_enviado TIMESTAMP WITH TIME ZONE,
    tipo_ultimo_lembrete VARCHAR(10),
    
    -- Campo obrigatório para número sequencial da agenda
    nr_seq_agenda INTEGER NOT NULL,
    
    -- Timestamps
    enviado_em TIMESTAMP WITH TIME ZONE,
    criado_em TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    atualizado_em TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Cria índices para melhor performance
CREATE INDEX IF NOT EXISTS idx_ghas_tbl_pac_agendados_subscriber_id ON ghas_tbl_pac_agendados(subscriber_id);
CREATE INDEX IF NOT EXISTS idx_ghas_tbl_pac_agendados_status ON ghas_tbl_pac_agendados(status);
CREATE INDEX IF NOT EXISTS idx_ghas_tbl_pac_agendados_data_consulta ON ghas_tbl_pac_agendados(data_consulta);
CREATE INDEX IF NOT EXISTS idx_ghas_tbl_pac_agendados_telefone ON ghas_tbl_pac_agendados(telefone);
CREATE INDEX IF NOT EXISTS idx_ghas_tbl_pac_agendados_nr_seq_agenda ON ghas_tbl_pac_agendados(nr_seq_agenda);

-- Insere dados de exemplo (opcional)
INSERT INTO ghas_tbl_pac_agendados (
    nome_paciente, 
    telefone, 
    email, 
    data_consulta, 
    nome_medico, 
    especialidade,
    nr_seq_agenda
) VALUES 
    ('João Silva', '5511999999999', 'joao@email.com', NOW() + INTERVAL '3 days', 'Dr. Carlos', 'Cardiologia', 1001),
    ('Maria Santos', '5511888888888', 'maria@email.com', NOW() + INTERVAL '2 days', 'Dra. Ana', 'Dermatologia', 1002)
ON CONFLICT DO NOTHING;

-- Comentários para documentação
COMMENT ON TABLE ghas_tbl_pac_agendados IS 'Tabela de atendimentos médicos com controle de confirmação via WhatsApp';
COMMENT ON COLUMN ghas_tbl_pac_agendados.subscriber_id IS 'ID do subscriber no Botconversa';
COMMENT ON COLUMN ghas_tbl_pac_agendados.status IS 'Status da confirmação da consulta';
COMMENT ON COLUMN ghas_tbl_pac_agendados.nr_seq_agenda IS 'Número sequencial da agenda (campo obrigatório)';
