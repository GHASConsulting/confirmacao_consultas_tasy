"""
Serviço para integração com a API do Botconversa.

Este serviço gerencia:
- Envio de dados para o Botconversa
- Criação de subscribers
- Envio de mensagens
- Processamento de respostas
"""

import requests
import json
from typing import Dict, Any, Optional, List
from datetime import datetime
from loguru import logger
from sqlalchemy.orm import Session

from app.config.config import settings
from app.database.models import (
    Atendimento,
    Paciente,
    Consulta,
    StatusConfirmacao,
    Confirmacao,
)


class BotconversaService:
    """Serviço para integração com a API do Botconversa"""

    def __init__(self, db: Session):
        self.db = db
        self.base_url = "https://backend.botconversa.com.br/api/v1/webhook"
        self.api_key = settings.botconversa_api_key
        self.headers = {
            "API-KEY": self.api_key,
            "Content-Type": "application/json",
            "accept": "application/json",
        }

    def testar_conexao(self) -> Dict[str, Any]:
        """
        Testa a conexão com a API do Botconversa.

        Returns:
            Dicionário com resultado do teste
        """
        try:
            response = requests.get(
                f"{self.base_url}/campaigns/", headers=self.headers, timeout=30
            )

            if response.status_code == 200:
                return {
                    "success": True,
                    "message": "Conexão com Botconversa estabelecida com sucesso",
                    "status_code": response.status_code,
                }
            else:
                return {
                    "success": False,
                    "message": f"Erro na conexão: {response.status_code} - {response.text}",
                    "status_code": response.status_code,
                }

        except Exception as e:
            logger.error(f"Erro ao testar conexão: {str(e)}")
            return {
                "success": False,
                "message": f"Erro na conexão: {str(e)}",
                "status_code": None,
            }

    def criar_subscriber(
        self, telefone: str, nome: str, sobrenome: str = ""
    ) -> Optional[Dict[str, Any]]:
        """
        Cria um subscriber no Botconversa usando o webhook.

        Args:
            telefone: Número do telefone (formato: 5531999629004)
            nome: Primeiro nome
            sobrenome: Sobrenome (opcional)

        Returns:
            Dados do subscriber criado ou None se erro
        """
        try:
            # Prepara dados do subscriber
            subscriber_data = {
                "phone": telefone,
                "first_name": nome,
                "last_name": sobrenome,
            }

            logger.info(f"Criando subscriber para telefone: {telefone}")

            # Faz requisição para criar subscriber via webhook
            response = requests.post(
                f"{self.base_url}/subscriber/",
                json=subscriber_data,
                headers=self.headers,
                timeout=30,
            )

            if response.status_code == 200:
                subscriber = response.json()
                subscriber_id = subscriber.get('id')
                logger.info(f"Subscriber criado com sucesso: {subscriber_id}")
                
                # Adicionar etiqueta subscriber_id automaticamente
                if subscriber_id:
                    logger.info(f"Adicionando etiqueta subscriber_id ao subscriber {subscriber_id}")
                    sucesso_etiqueta = self.adicionar_etiqueta_subscriber(subscriber_id)
                    
                    if sucesso_etiqueta:
                        logger.info(f"✅ Etiqueta subscriber_id adicionada com sucesso ao subscriber {subscriber_id}")
                    else:
                        logger.warning(f"⚠️ Subscriber criado, mas falha ao adicionar etiqueta para {subscriber_id}")
                    
                    # Adicionar campo personalizado subscriber_id automaticamente
                    logger.info(f"Adicionando campo personalizado subscriber_id ao subscriber {subscriber_id}")
                    sucesso_campo = self.adicionar_campo_personalizado(subscriber_id)
                    
                    if sucesso_campo:
                        logger.info(f"✅ Campo personalizado subscriber_id adicionado com sucesso ao subscriber {subscriber_id}")
                    else:
                        logger.warning(f"⚠️ Subscriber criado, mas falha ao adicionar campo personalizado para {subscriber_id}")
                        # Continua mesmo se o campo falhar - não quebra o fluxo
                else:
                    logger.warning("Subscriber criado mas sem ID válido para adicionar etiqueta e campo personalizado")
                
                return subscriber
            else:
                logger.error(
                    f"Erro ao criar subscriber: {response.status_code} - {response.text}"
                )
                return None

        except Exception as e:
            logger.error(f"Erro ao criar subscriber: {str(e)}")
            return None

    def buscar_subscriber(self, telefone: str) -> Optional[Dict[str, Any]]:
        """
        Busca um subscriber pelo telefone.

        Args:
            telefone: Número do telefone

        Returns:
            Dados do subscriber ou None se não encontrado
        """
        try:
            logger.info(f"Buscando subscriber para telefone: {telefone}")

            response = requests.get(
                f"{self.base_url}/subscriber/get_by_phone/{telefone}/",
                headers=self.headers,
                timeout=30,
            )

            if response.status_code == 200:
                subscriber = response.json()
                logger.info(f"Subscriber encontrado: {subscriber.get('id')}")
                return subscriber
            else:
                logger.error(
                    f"Erro ao buscar subscriber: {response.status_code} - {response.text}"
                )
                return None

        except Exception as e:
            logger.error(f"Erro ao buscar subscriber: {str(e)}")
            return None

    def adicionar_etiqueta_subscriber(self, subscriber_id: int, tag_id: int = 15362464) -> bool:
        """
        Adiciona etiqueta subscriber_id ao subscriber no Botconversa.

        Args:
            subscriber_id: ID do subscriber no Botconversa
            tag_id: ID da etiqueta (padrão: 15362464 para subscriber_id)

        Returns:
            True se etiqueta foi adicionada com sucesso, False caso contrário
        """
        try:
            logger.info(f"Adicionando etiqueta {tag_id} ao subscriber {subscriber_id}")
            
            # URL para adicionar etiqueta ao subscriber
            url = f"{self.base_url}/subscriber/{subscriber_id}/tags/{tag_id}/"
            
            # Faz requisição POST para adicionar etiqueta
            response = requests.post(
                url,
                headers=self.headers,
                timeout=30,
            )
            
            if response.status_code == 200 or response.status_code == 201:
                logger.info(f"✅ Etiqueta {tag_id} adicionada com sucesso ao subscriber {subscriber_id}")
                return True
            else:
                logger.error(
                    f"❌ Erro ao adicionar etiqueta {tag_id} ao subscriber {subscriber_id}: "
                    f"{response.status_code} - {response.text}"
                )
                return False
                
        except Exception as e:
            logger.error(f"❌ Erro ao adicionar etiqueta ao subscriber {subscriber_id}: {str(e)}")
            return False

    def adicionar_campo_personalizado(
        self, subscriber_id: int, field_id: int = 4336343, valor: str = None
    ) -> bool:
        """
        Adiciona valor ao campo personalizado subscriber_id do subscriber no Botconversa.

        Args:
            subscriber_id: ID do subscriber no Botconversa
            field_id: ID do campo personalizado (padrão: 4336343 para subscriber_id)
            valor: Valor a ser salvo no campo (se None, usa o próprio subscriber_id)

        Returns:
            True se campo foi atualizado com sucesso, False caso contrário
        """
        try:
            # Se não foi informado valor, usa o próprio subscriber_id
            if valor is None:
                valor = str(subscriber_id)
            
            logger.info(f"Adicionando valor '{valor}' ao campo personalizado {field_id} do subscriber {subscriber_id}")
            
            # URL para atualizar campo personalizado do subscriber
            url = f"{self.base_url}/subscriber/{subscriber_id}/custom_fields/{field_id}/"
            
            # Dados para atualizar o campo personalizado
            field_data = {
                "value": valor
            }
            
            # Faz requisição POST para atualizar campo personalizado
            response = requests.post(
                url,
                json=field_data,
                headers=self.headers,
                timeout=30,
            )
            
            if response.status_code == 200 or response.status_code == 201:
                logger.info(f"✅ Campo personalizado {field_id} atualizado com sucesso para subscriber {subscriber_id} com valor '{valor}'")
                return True
            else:
                logger.error(
                    f"❌ Erro ao atualizar campo personalizado {field_id} do subscriber {subscriber_id}: "
                    f"{response.status_code} - {response.text}"
                )
                return False
                
        except Exception as e:
            logger.error(f"❌ Erro ao atualizar campo personalizado do subscriber {subscriber_id}: {str(e)}")
            return False

    def criar_atendimento(self, dados: Dict[str, Any]) -> Optional[Atendimento]:
        """
        Cria um novo atendimento e registra no Botconversa.

        Args:
            dados: Dados do atendimento (nome_paciente, telefone, email, nome_medico, especialidade, data_consulta, observacoes)

        Returns:
            Atendimento criado ou None se erro
        """
        try:
            # Cria o atendimento no banco
            atendimento = Atendimento(
                nome_paciente=dados["nome_paciente"],
                telefone=dados["telefone"],
                email=dados.get("email"),
                nome_medico=dados["nome_medico"],
                especialidade=dados["especialidade"],
                data_consulta=dados["data_consulta"],
                observacoes=dados.get("observacoes"),
                nr_seq_agenda=dados.get("nr_seq_agenda", 0),  # Campo obrigatório
                status=StatusConfirmacao.PENDENTE,  # Campo de controle inicial
            )

            self.db.add(atendimento)
            self.db.commit()
            self.db.refresh(atendimento)

            # Cria subscriber no Botconversa
            nome_parts = dados["nome_paciente"].split()
            primeiro_nome = nome_parts[0] if nome_parts else ""
            sobrenome = " ".join(nome_parts[1:]) if len(nome_parts) > 1 else ""

            subscriber = self.criar_subscriber(
                telefone=dados["telefone"], nome=primeiro_nome, sobrenome=sobrenome
            )

            if subscriber:
                # Atualiza o atendimento com o subscriber_id
                atendimento.subscriber_id = subscriber.get("id")
                self.db.commit()
                self.db.refresh(atendimento)

                logger.info(
                    f"Atendimento {atendimento.id} criado com subscriber_id {atendimento.subscriber_id}"
                )
            else:
                logger.warning(f"Atendimento {atendimento.id} criado sem subscriber_id")

            return atendimento

        except Exception as e:
            logger.error(f"Erro ao criar atendimento: {str(e)}")
            self.db.rollback()
            return None

    def enviar_mensagem(self, subscriber_id: int, mensagem: str) -> bool:
        """
        Envia uma mensagem para um subscriber.

        Args:
            subscriber_id: ID do subscriber no Botconversa
            mensagem: Texto da mensagem

        Returns:
            True se enviado com sucesso, False caso contrário
        """
        try:
            message_data = {"type": "text", "value": mensagem}

            response = requests.post(
                f"{self.base_url}/subscriber/{subscriber_id}/send_message/",
                json=message_data,
                headers=self.headers,
                timeout=30,
            )

            if response.status_code == 200:
                result = response.json()
                logger.info(f"Mensagem enviada com sucesso: {result.get('message_id')}")
                return True
            else:
                logger.error(
                    f"Erro ao enviar mensagem: {response.status_code} - {response.text}"
                )
                return False

        except Exception as e:
            logger.error(f"Erro ao enviar mensagem: {str(e)}")
            return False

    def enviar_mensagem_consulta(self, atendimento: Atendimento) -> bool:
        """
        Envia uma mensagem personalizada sobre a consulta para o paciente.

        Args:
            atendimento: Objeto Atendimento com os dados da consulta

        Returns:
            True se enviado com sucesso, False caso contrário
        """
        try:
            if not atendimento.subscriber_id:
                logger.error(f"Atendimento {atendimento.id} não tem subscriber_id")
                return False

            # Formata a data da consulta
            data_formatada = atendimento.data_consulta.strftime("%d/%m/%Y")
            hora_formatada = atendimento.data_consulta.strftime("%H:%M")

            # Obtém as configurações do hospital
            hospital_name = settings.hospital_name 
            hospital_phone = settings.hospital_phone
            hospital_address = (
                settings.hospital_address 
            )
            hospital_city = settings.hospital_city 
            hospital_state = settings.hospital_state 

            # Monta o endereço completo
            endereco_completo = (
                f"{hospital_address}, {hospital_city} - {hospital_state}"
            )

            # Cria a mensagem personalizada
            mensagem = f"""🏥 **{hospital_name}**

Olá {atendimento.nome_paciente}! 👋

Você tem uma consulta agendada:
📅 **Data:** {data_formatada}
⏰ **Horário:** {hora_formatada}
👨‍⚕️ **Médico:** {atendimento.nome_medico}
🏥 **Especialidade:** {atendimento.especialidade}

Aguardamos sua confirmação! 🙏

📞 Para dúvidas: {hospital_phone}
📍 Endereço: {endereco_completo}"""

            logger.info(
                f"Enviando mensagem personalizada para subscriber {atendimento.subscriber_id}"
            )

            # Envia a mensagem
            sucesso = self.enviar_mensagem(atendimento.subscriber_id, mensagem)

            if sucesso:
                # Atualiza o atendimento com a informação de que a mensagem foi enviada
                atendimento.mensagem_enviada = mensagem
                atendimento.enviado_em = datetime.now()
                atendimento.atualizado_em = datetime.now()
                self.db.commit()

                logger.info(
                    f"Mensagem personalizada enviada com sucesso para {atendimento.nome_paciente}"
                )
                return True
            else:
                logger.error(
                    f"Erro ao enviar mensagem personalizada para {atendimento.nome_paciente}"
                )
                return False

        except Exception as e:
            logger.error(f"Erro ao enviar mensagem personalizada: {str(e)}")
            return False

    def processar_resposta_paciente(self, telefone: str, resposta: str) -> bool:
        """
        Processa a resposta de um paciente e atualiza o campo de controle.

        Args:
            telefone: Telefone do paciente
            resposta: Resposta do paciente (1=SIM, 0=NÃO, ou texto)

        Returns:
            True se processado com sucesso, False caso contrário
        """
        try:
            # Busca atendimento pelo telefone
            atendimento = (
                self.db.query(Atendimento)
                .filter(Atendimento.telefone == telefone)
                .order_by(Atendimento.data_consulta.desc())
                .first()
            )

            if not atendimento:
                logger.error(f"Atendimento não encontrado para telefone: {telefone}")
                return False

            # Processa resposta e atualiza o campo de controle
            resposta_limpa = resposta.strip()

            # Verifica respostas numéricas primeiro (1=SIM, 0=NÃO)
            if resposta_limpa == "1":
                novo_status = StatusConfirmacao.CONFIRMADO
                interpretacao = "confirmado"
            elif resposta_limpa == "0":
                novo_status = StatusConfirmacao.CANCELADO
                interpretacao = "cancelado"
            else:
                # Processa respostas textuais (fallback)
                resposta_lower = resposta_limpa.lower()

                if "sim" in resposta_lower or "confirmo" in resposta_lower:
                    novo_status = StatusConfirmacao.CONFIRMADO
                    interpretacao = "confirmado"
                elif (
                    "não" in resposta_lower
                    or "nao" in resposta_lower
                    or "cancelo" in resposta_lower
                ):
                    novo_status = StatusConfirmacao.CANCELADO
                    interpretacao = "cancelado"
                elif "reagendar" in resposta_lower:
                    novo_status = (
                        StatusConfirmacao.PENDENTE
                    )  # Mantém pendente para reagendamento
                    interpretacao = "reagendar"
                else:
                    novo_status = StatusConfirmacao.PENDENTE
                    interpretacao = "indefinido"

            # Atualiza o campo de controle (status_confirmacao) e outros dados
            atendimento.status_confirmacao = novo_status
            atendimento.resposta_paciente = resposta
            atendimento.interpretacao_resposta = interpretacao
            atendimento.respondido_em = datetime.now()
            atendimento.atualizado_em = datetime.now()

            self.db.commit()

            logger.info(
                f"Resposta do paciente processada: {interpretacao} - Status atualizado para: {novo_status.value}"
            )
            return True

        except Exception as e:
            logger.error(f"Erro ao processar resposta do paciente: {str(e)}")
            self.db.rollback()
            return False

    def listar_atendimentos_pendentes(self) -> List[Atendimento]:
        """
        Lista todos os atendimentos pendentes (campo de controle = PENDENTE).

        Returns:
            Lista de atendimentos pendentes
        """
        try:
            atendimentos = (
                self.db.query(Atendimento)
                .filter(Atendimento.status_confirmacao == StatusConfirmacao.PENDENTE)
                .order_by(Atendimento.data_consulta.asc())
                .all()
            )
            return atendimentos
        except Exception as e:
            logger.error(f"Erro ao listar atendimentos pendentes: {str(e)}")
            return []

    def buscar_atendimento_por_telefone(self, telefone: str) -> Optional[Atendimento]:
        """
        Busca um atendimento pelo telefone.

        Args:
            telefone: Número do telefone

        Returns:
            Atendimento encontrado ou None
        """
        try:
            atendimento = (
                self.db.query(Atendimento)
                .filter(Atendimento.telefone == telefone)
                .order_by(Atendimento.data_consulta.desc())
                .first()
            )
            return atendimento
        except Exception as e:
            logger.error(
                f"Erro ao buscar atendimento por telefone {telefone}: {str(e)}"
            )
            return None

    def atualizar_status_atendimento(
        self, atendimento_id: int, novo_status: StatusConfirmacao
    ) -> bool:
        """
        Atualiza o campo de controle (status) de um atendimento.

        Args:
            atendimento_id: ID do atendimento
            novo_status: Novo status

        Returns:
            True se atualizado com sucesso, False caso contrário
        """
        try:
            atendimento = (
                self.db.query(Atendimento)
                .filter(Atendimento.id == atendimento_id)
                .first()
            )
            if not atendimento:
                logger.error(f"Atendimento não encontrado: {atendimento_id}")
                return False

            atendimento.status_confirmacao = novo_status
            atendimento.atualizado_em = datetime.now()

            self.db.commit()

            logger.info(
                f"Status do atendimento {atendimento_id} atualizado para {novo_status.value}"
            )
            return True

        except Exception as e:
            logger.error(
                f"Erro ao atualizar status do atendimento {atendimento_id}: {str(e)}"
            )
            self.db.rollback()
            return False

    def listar_campanhas(self) -> Optional[List[Dict[str, Any]]]:
        """
        Lista todas as campanhas ativas no Botconversa.

        Returns:
            Lista de campanhas ou None se erro
        """
        try:
            logger.info("Listando campanhas ativas...")

            response = requests.get(
                f"{self.base_url}/campaigns/",
                headers=self.headers,
                timeout=30,
            )

            if response.status_code == 200:
                campanhas = response.json()
                logger.info(f"Campanhas encontradas: {len(campanhas)}")
                return campanhas
            else:
                logger.error(
                    f"Erro ao listar campanhas: {response.status_code} - {response.text}"
                )
                return None

        except Exception as e:
            logger.error(f"Erro ao listar campanhas: {str(e)}")
            return None

    def adicionar_subscriber_campanha(
        self, subscriber_id: int, campaign_id: int = 289860
    ) -> bool:
        """
        Adiciona um subscriber à campanha de confirmação de consultas.

        Args:
            subscriber_id: ID do subscriber no Botconversa
            campaign_id: ID da campanha (padrão: 289860 - Confirmação de Consultas)

        Returns:
            True se adicionado com sucesso, False caso contrário
        """
        try:
            logger.info(
                f"Adicionando subscriber {subscriber_id} à campanha {campaign_id}"
            )

            response = requests.post(
                f"{self.base_url}/subscriber/{subscriber_id}/campaigns/{campaign_id}/",
                headers=self.headers,
                timeout=30,
            )

            if response.status_code == 200:
                logger.info(
                    f"Subscriber {subscriber_id} adicionado à campanha {campaign_id} com sucesso"
                )
                return True
            else:
                logger.error(
                    f"Erro ao adicionar subscriber à campanha: {response.status_code} - {response.text}"
                )
                return False

        except Exception as e:
            logger.error(f"Erro ao adicionar subscriber à campanha: {str(e)}")
            return False

    def listar_fluxos(self) -> Optional[List[Dict[str, Any]]]:
        """
        Lista todos os fluxos disponíveis no Botconversa.

        Returns:
            Lista de fluxos ou None se erro
        """
        try:
            logger.info("Listando fluxos disponíveis...")

            response = requests.get(
                f"{self.base_url}/flows/",
                headers=self.headers,
                timeout=30,
            )

            if response.status_code == 200:
                fluxos = response.json()
                logger.info(f"Fluxos encontrados: {len(fluxos)}")
                return fluxos
            else:
                logger.error(
                    f"Erro ao listar fluxos: {response.status_code} - {response.text}"
                )
                return None

        except Exception as e:
            logger.error(f"Erro ao listar fluxos: {str(e)}")
            return None

    def enviar_fluxo(self, subscriber_id: int, flow_id: Optional[int] = None) -> bool:
        """
        Envia um fluxo para um subscriber.

        Args:
            subscriber_id: ID do subscriber no Botconversa
            flow_id: ID do fluxo (opcional - se não informado, usa o fluxo padrão da campanha)

        Returns:
            True se enviado com sucesso, False caso contrário
        """
        try:
            logger.info(
                f"Enviando fluxo para subscriber {subscriber_id} com flow_id: {flow_id}"
            )

            # Prepara dados do fluxo
            if flow_id is not None:
                flow_data = {"flow": flow_id}
                logger.info(f"Enviando fluxo com flow_id: {flow_id}")

                response = requests.post(
                    f"{self.base_url}/subscriber/{subscriber_id}/send_flow/",
                    json=flow_data,
                    headers=self.headers,
                    timeout=30,
                )
            else:
                # Envia sem flow_id (usa o fluxo padrão da campanha)
                logger.info(
                    "Enviando fluxo sem flow_id (usando fluxo padrão da campanha)"
                )
                response = requests.post(
                    f"{self.base_url}/subscriber/{subscriber_id}/send_flow/",
                    headers=self.headers,
                    timeout=30,
                )

            if response.status_code == 200:
                result = response.json()
                logger.info(
                    f"Fluxo enviado com sucesso para subscriber {subscriber_id}"
                )
                return True
            else:
                logger.error(
                    f"Erro ao enviar fluxo: {response.status_code} - {response.text}"
                )
                return False

        except Exception as e:
            logger.error(f"Erro ao enviar fluxo: {str(e)}")
            return False

    def aguardar_resposta_paciente(
        self, subscriber_id: int, timeout_minutos: int = 60
    ) -> Optional[Dict[str, Any]]:
        """
        Aguarda a resposta do paciente por um determinado tempo.

        Args:
            subscriber_id: ID do subscriber no Botconversa
            timeout_minutos: Tempo máximo de espera em minutos (padrão: 60)

        Returns:
            Dados da resposta ou None se não houve resposta
        """
        try:
            logger.info(
                f"Aguardando resposta do subscriber {subscriber_id} por {timeout_minutos} minutos..."
            )

            # Por enquanto, apenas retorna None (não implementado ainda)
            # Esta é a etapa que foi pulada - precisamos implementar a lógica de aguardar
            logger.warning("Método aguardar_resposta_paciente ainda não implementado")
            return None

        except Exception as e:
            logger.error(f"Erro ao aguardar resposta do paciente: {str(e)}")
            return None

    def executar_workflow_consulta(self, atendimento_id: int) -> Dict[str, Any]:
        """
        Executa o workflow completo para uma consulta:
        1. Verifica se o atendimento existe
        2. Envia mensagem personalizada
        3. Adiciona à campanha (se necessário)
        4. Envia fluxo

        Args:
            atendimento_id: ID do atendimento

        Returns:
            Dicionário com resultado do workflow
        """
        try:
            # Busca o atendimento
            atendimento = (
                self.db.query(Atendimento)
                .filter(Atendimento.id == atendimento_id)
                .first()
            )

            if not atendimento:
                return {
                    "success": False,
                    "error": f"Atendimento {atendimento_id} não encontrado",
                }

            if not atendimento.subscriber_id:
                return {
                    "success": False,
                    "error": f"Atendimento {atendimento_id} não tem subscriber_id",
                }

            logger.info(
                f"Iniciando workflow para atendimento {atendimento_id} - {atendimento.nome_paciente}"
            )

            # 1. Envia mensagem personalizada
            logger.info("1. Enviando mensagem personalizada...")
            mensagem_enviada = self.enviar_mensagem_consulta(atendimento)

            if not mensagem_enviada:
                return {
                    "success": False,
                    "error": "Erro ao enviar mensagem personalizada",
                }

            # 2. Adiciona à campanha (se necessário)
            logger.info("2. Adicionando à campanha...")
            campanha_adicionada = self.adicionar_subscriber_campanha(
                atendimento.subscriber_id
            )

            if not campanha_adicionada:
                logger.warning(
                    f"Erro ao adicionar subscriber {atendimento.subscriber_id} à campanha"
                )
                # Continua mesmo com erro na campanha

            # 3. Envia fluxo
            logger.info("3. Enviando fluxo...")
            fluxo_enviado = self.enviar_fluxo(
                atendimento.subscriber_id, 7725640
            )  # ID do fluxo "CONFIRMACAO CONSULTA"

            if not fluxo_enviado:
                return {"success": False, "error": "Erro ao enviar fluxo"}

            logger.info(
                f"Workflow concluído com sucesso para atendimento {atendimento_id}"
            )

            return {
                "success": True,
                "message": "Workflow executado com sucesso",
                "atendimento_id": atendimento_id,
                "subscriber_id": atendimento.subscriber_id,
                "mensagem_enviada": mensagem_enviada,
                "campanha_adicionada": campanha_adicionada,
                "fluxo_enviado": fluxo_enviado,
            }

        except Exception as e:
            logger.error(f"Erro ao executar workflow: {str(e)}")
            return {"success": False, "error": f"Erro interno: {str(e)}"}
