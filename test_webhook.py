#!/usr/bin/env python3
"""
Script para testar o webhook do Botconversa.

Este script simula o envio de um webhook do Botconversa para testar
o processamento de respostas dos pacientes.
"""

import requests
import json
from datetime import datetime

# URL do webhook local
WEBHOOK_URL = "http://localhost:8000/webhook/botconversa"


def test_webhook_confirmation():
    """Testa o webhook com uma resposta de confirmação"""

    # Payload simulado do Botconversa para confirmação
    webhook_data = {
        "type": "message",
        "contact": {
            "id": 786889127,
            "full_name": "Iury Henrique Costa",
            "first_name": "Iury",
            "last_name": "Costa",
            "phone": "+553199629004",
            "ddd": "31",
        },
        "message": {
            "id": "msg_test_123",
            "type": "text",
            "content": "SIM",
            "timestamp": datetime.now().isoformat(),
        },
    }

    print("🧪 Testando webhook com resposta de CONFIRMAÇÃO...")
    print(f"📤 Enviando para: {WEBHOOK_URL}")
    print(f"📄 Payload: {json.dumps(webhook_data, indent=2)}")

    try:
        response = requests.post(
            WEBHOOK_URL,
            json=webhook_data,
            headers={"Content-Type": "application/json"},
            timeout=30,
        )

        print(f"📥 Status Code: {response.status_code}")
        print(f"📄 Response: {response.text}")

        if response.status_code == 200:
            print("✅ Webhook processado com sucesso!")
        else:
            print("❌ Erro ao processar webhook")

    except Exception as e:
        print(f"❌ Erro ao enviar webhook: {str(e)}")


def test_webhook_cancellation():
    """Testa o webhook com uma resposta de cancelamento"""

    # Payload simulado do Botconversa para cancelamento
    webhook_data = {
        "type": "message",
        "contact": {
            "id": 786889127,
            "full_name": "Iury Henrique Costa",
            "first_name": "Iury",
            "last_name": "Costa",
            "phone": "+553199629004",
            "ddd": "31",
        },
        "message": {
            "id": "msg_test_456",
            "type": "text",
            "content": "NÃO",
            "timestamp": datetime.now().isoformat(),
        },
    }

    print("\n🧪 Testando webhook com resposta de CANCELAMENTO...")
    print(f"📤 Enviando para: {WEBHOOK_URL}")
    print(f"📄 Payload: {json.dumps(webhook_data, indent=2)}")

    try:
        response = requests.post(
            WEBHOOK_URL,
            json=webhook_data,
            headers={"Content-Type": "application/json"},
            timeout=30,
        )

        print(f"📥 Status Code: {response.status_code}")
        print(f"📄 Response: {response.text}")

        if response.status_code == 200:
            print("✅ Webhook processado com sucesso!")
        else:
            print("❌ Erro ao processar webhook")

    except Exception as e:
        print(f"❌ Erro ao enviar webhook: {str(e)}")


def test_webhook_reagendamento():
    """Testa o webhook com uma resposta de reagendamento"""

    # Payload simulado do Botconversa para reagendamento
    webhook_data = {
        "type": "message",
        "contact": {
            "id": 786889127,
            "full_name": "Iury Henrique Costa",
            "first_name": "Iury",
            "last_name": "Costa",
            "phone": "+553199629004",
            "ddd": "31",
        },
        "message": {
            "id": "msg_test_789",
            "type": "text",
            "content": "REAGENDAR",
            "timestamp": datetime.now().isoformat(),
        },
    }

    print("\n🧪 Testando webhook com resposta de REAGENDAMENTO...")
    print(f"📤 Enviando para: {WEBHOOK_URL}")
    print(f"📄 Payload: {json.dumps(webhook_data, indent=2)}")

    try:
        response = requests.post(
            WEBHOOK_URL,
            json=webhook_data,
            headers={"Content-Type": "application/json"},
            timeout=30,
        )

        print(f"📥 Status Code: {response.status_code}")
        print(f"📄 Response: {response.text}")

        if response.status_code == 200:
            print("✅ Webhook processado com sucesso!")
        else:
            print("❌ Erro ao processar webhook")

    except Exception as e:
        print(f"❌ Erro ao enviar webhook: {str(e)}")


if __name__ == "__main__":
    print("🚀 Iniciando testes do webhook do Botconversa...")
    print("=" * 60)

    # Testa diferentes tipos de resposta
    test_webhook_confirmation()
    test_webhook_cancellation()
    test_webhook_reagendamento()

    print("\n" + "=" * 60)
    print("🏁 Testes concluídos!")
