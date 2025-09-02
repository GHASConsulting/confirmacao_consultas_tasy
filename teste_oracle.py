#!/usr/bin/env python3
"""
Teste de conexão Oracle usando cx_Oracle
"""

import cx_Oracle
import os
import sys
from datetime import datetime

def test_oracle_connection():
    print("🔍 TESTANDO CONEXÃO ORACLE...")
    print("=" * 50)
    
    # 1. DEFINIR variáveis de ambiente ANTES de tudo
    print("🔧 Configurando variáveis de ambiente...")
    os.environ['ORACLE_HOME'] = '/root/instantclient_21_13'
    os.environ['LD_LIBRARY_PATH'] = '/root/instantclient_21_13:' + os.environ.get('LD_LIBRARY_PATH', '')
    os.environ['PATH'] = '/root/instantclient_21_13:' + os.environ.get('PATH', '')
    
    # 2. Verificar se foram definidas
    print("📋 Variáveis de ambiente:")
    print(f"ORACLE_HOME: {os.environ.get('ORACLE_HOME', 'NÃO DEFINIDO')}")
    print(f"LD_LIBRARY_PATH: {os.environ.get('LD_LIBRARY_PATH', 'NÃO DEFINIDO')}")
    print()
    
    # 3. Tentar inicializar Oracle Client
    try:
        print("🚀 Inicializando Oracle Client...")
        cx_Oracle.init_oracle_client()
        print("✅ Oracle Client inicializado com sucesso!")
    except Exception as e:
        print(f"❌ Erro ao inicializar Oracle Client: {e}")
        return False
    
    # 4. Testar conexão
    try:
        print("\n🔌 Testando conexão...")
        connection = cx_Oracle.connect(
            user="tasy",
            password="aloisk",
            dsn="172.23.88.78:1521/TASYH"
        )
        
        print("✅ CONEXÃO ORACLE FUNCIONANDO!")
        print(f"📊 Versão Oracle: {connection.version}")
        
        # 5. Executar consulta na tabela ghas_tbl_pac_agendados
        print("\n📋 EXECUTANDO CONSULTA NA TABELA ghas_tbl_pac_agendados...")
        consultar_tabela_agendados(connection)
        
        connection.close()
        return True
        
    except Exception as e:
        print(f"❌ Erro na conexão: {e}")
        return False

def consultar_tabela_agendados(connection):
    """
    Consulta dados da tabela ghas_tbl_pac_agendados
    """
    try:
        cursor = connection.cursor()
        
        # Consulta para verificar se a tabela existe e contar registros
        print("🔍 Verificando estrutura da tabela...")
        cursor.execute("""
            SELECT COUNT(*) as total_registros 
            FROM ghas_tbl_pac_agendados
        """)
        
        total = cursor.fetchone()[0]
        print(f"📊 Total de registros na tabela: {total}")
        
        if total > 0:
            # Consulta para buscar alguns registros de exemplo
            print("\n📋 Buscando primeiros 5 registros da tabela...")
            cursor.execute("""
                SELECT 
                    id,
                    nome_paciente,
                    telefone,
                    email,
                    nome_medico,
                    especialidade,
                    data_consulta,
                    status_confirmacao,
                    nr_seq_agenda,
                    criado_em
                FROM ghas_tbl_pac_agendados 
                WHERE ROWNUM <= 5
                ORDER BY criado_em DESC
            """)
            
            registros = cursor.fetchall()
            
            if registros:
                print("\n📋 REGISTROS ENCONTRADOS:")
                print("-" * 80)
                for i, registro in enumerate(registros, 1):
                    print(f"\n🔹 REGISTRO {i}:")
                    print(f"   ID: {registro[0]}")
                    print(f"   Paciente: {registro[1]}")
                    print(f"   Telefone: {registro[2]}")
                    print(f"   Email: {registro[3] or 'N/A'}")
                    print(f"   Médico: {registro[4]}")
                    print(f"   Especialidade: {registro[5]}")
                    print(f"   Data Consulta: {registro[6]}")
                    print(f"   Status_confirmacao: {registro[7]}")
                    print(f"   Nr Seq Agenda: {registro[8]}")
                    print(f"   Criado em: {registro[9]}")
            else:
                print("❌ Nenhum registro encontrado")
        
        # Consulta para verificar consultas agendadas para hoje
        print("\n📅 CONSULTAS AGENDADAS PARA HOJE:")
        cursor.execute("""
            SELECT 
                *
            FROM ghas_tbl_pac_agendados 
            WHERE TRUNC(data_consulta) = TRUNC(SYSDATE)
            ORDER BY data_consulta
        """)
        
        consultas_hoje = cursor.fetchall()
        if consultas_hoje:
            for consulta in consultas_hoje:
                print(f"   📋 {consulta[0]} - Dr. {consulta[1]} ({consulta[2]}) - {consulta[3]} - Status_confirmacao: {consulta[4]}")
        else:
            print("   Nenhuma consulta agendada para hoje")
        
        # Consulta para verificar consultas pendentes de confirmação
        print("\n⏳ CONSULTAS PENDENTES DE CONFIRMAÇÃO:")
        cursor.execute("""
            SELECT 
                COUNT(*) as total_pendentes,
                COUNT(CASE WHEN TRUNC(data_consulta) = TRUNC(SYSDATE) THEN 1 END) as hoje_pendentes,
                COUNT(CASE WHEN TRUNC(data_consulta) = TRUNC(SYSDATE + 1) THEN 1 END) as amanha_pendentes
            FROM ghas_tbl_pac_agendados 
            WHERE status_confirmacao = 'PENDENTE'
        """)
        
        pendentes = cursor.fetchone()
        print(f"   Total pendentes: {pendentes[0]}")
        print(f"   Pendentes para hoje: {pendentes[1]}")
        print(f"   Pendentes para amanhã: {pendentes[2]}")
        
        cursor.close()
        print("\n✅ Consulta executada com sucesso!")
        
    except Exception as e:
        print(f"❌ Erro ao executar consulta: {e}")
        # Tentar verificar se a tabela existe
        try:
            cursor = connection.cursor()
            cursor.execute("""
                SELECT table_name 
                FROM user_tables 
                WHERE table_name = 'GHAS_TBL_PAC_AGENDADOS'
            """)
            
            if cursor.fetchone():
                print("✅ Tabela existe, mas houve erro na consulta")
            else:
                print("❌ Tabela ghas_tbl_pac_agendados não encontrada")
            cursor.close()
        except:
            pass

if __name__ == "__main__":
    success = test_oracle_connection()
    sys.exit(0 if success else 1)