from datetime import datetime, timedelta
import os
import dateutil
from dotenv import load_dotenv
import requests
from typing import Optional
from app.utils.logging_config import logger


load_dotenv()

class PipedriveClient:

    def __init__(self):
        self.api_token = os.getenv("PIPEDRIVE_API_TOKEN")
        self.owner_id = int(os.getenv("PIPEDRIVE_OWNER_ID"))

        self.base_url = "https://api.pipedrive.com/v1"
        self.visible_to = 3

        # --- IDs DOS CAMPOS PERSONALIZADOS ---
        # self.FIELD_SEGMENTO = "fbc308cdf13795575d40d7f17a95487f477daa0e"
        # self.FIELD_FATURAMENTO = "df91788afb1cb9e7d7949727684e895b6deb1a29"
        # self.FIELD_FUNCIONARIOS = "5095a2aeccdc56ca262471a7731d9e54aa0edaee"
        # self.FIELD_PRODUTO = "ee0b4513ad28a2f52edbc8b4252f0fdc33cd7fd5"
        # self.FIELD_MOTIVO_IA = "0a605b9668c110080cd956312ac51b11a7855621"
        # self.FIELD_DESAFIO = "26067d9464f84b9c8979452fcdf9d0197aa9cf37"
        # self.FIELD_MOMENTO = "9ecee0c9e0b9232313912a5082dac228d299dcea"
        # self.FIELD_CAPACIDADE_INVESTIMENTO = "8c4d7b17bad6d31b26c3f24a6aa68d39628e49dc"

        self.FIELD_SEGMENTO = "3bba6a3886d88fa043d916830d8e3fa63704b325"
        self.FIELD_FATURAMENTO = "5dc337302075b541c01d5b4b43cdc18c6d069ac9"
        self.FIELD_FUNCIONARIOS = "d12a57b7469d8e92be6922544fb6534ca4ed1e21"
        self.FIELD_PRODUTO = "675a446167008ae9d3aca7c95e57189b9199eb29"
        self.FIELD_MOTIVO_IA = "0a605b9668c110080cd956312ac51b11a7855621"
        self.FIELD_DESAFIO = "5c6b52fb5611bf4d30e6a7a69499b23ea6c76b47"
        self.FIELD_MOMENTO = "33a533f719c6d40e15e3ccff84a36002ac6209c9"
        self.FIELD_CAPACIDADE_INVESTIMENTO = "d6d6bd34a685a23f535f5de7170d343602ec59b3"

    def _get_headers(self):
        return {"Content-Type": "application/json"}
    
    def create_activity(self, subject: str, type: str, due_date: str, due_time: str, person_id: int, org_id: int, deal_id: int = None) -> dict:
        """
        Método genérico para criar qualquer atividade.
        """
        data = {
            "subject": subject,
            "type": type,
            "due_date": due_date,
            "due_time": due_time,
            "person_id": person_id,
            "org_id": org_id,
            "done": 0
        }

        if deal_id:
            data["deal_id"] = deal_id

        logger.info(f"[PIPEDRIVE_CRM_INTEGRATION] 📅 Criando atividade no Pipedrive")
        return self._post("activities", data)

    def schedule_confirmation_call(self, meeting_datetime: datetime, person_id: int, org_id: int, deal_id: int = None):
        """
        Cria ligação 1 dia antes as 10:00 BRT.
        Converte 10:00 BRT para UTC (13:00) antes de enviar.
        """
        tz_brasil = dateutil.tz.gettz('America/Sao_Paulo')
        tz_utc = dateutil.tz.UTC

        if meeting_datetime.tzinfo is None:
            meeting_datetime = meeting_datetime.replace(tzinfo=tz_brasil)

        call_date_obj = meeting_datetime - timedelta(days=1)

        call_datetime_br = call_date_obj.replace(hour=10, minute=0, second=0, microsecond=0, tzinfo=tz_brasil)

        call_datetime_utc = call_datetime_br.astimezone(tz_utc)

        due_date = call_datetime_utc.strftime("%Y-%m-%d")
        due_time = call_datetime_utc.strftime("%H:%M")

        subject = "Ligar para confirmar reunião de amanhã"
        
        return self.create_activity(
            subject=subject,
            type="call",
            due_date=due_date,
            due_time=due_time,
            person_id=person_id,
            org_id=org_id,
            deal_id=deal_id
        )

    def schedule_meeting_activity(self, meeting_datetime: datetime, person_id: int, org_id: int, deal_id: int = None):
        """
        Cria a reunião no horário agendado.
        Converte o horário BRT para UTC antes de enviar.
        """
        tz_brasil = dateutil.tz.gettz('America/Sao_Paulo')
        tz_utc = dateutil.tz.UTC

        if meeting_datetime.tzinfo is None:
            meeting_br = meeting_datetime.replace(tzinfo=tz_brasil)
        else:
            meeting_br = meeting_datetime.astimezone(tz_brasil)
        
        meeting_utc = meeting_br.astimezone(tz_utc)

        due_date = meeting_utc.strftime("%Y-%m-%d")
        due_time = meeting_utc.strftime("%H:%M")

        subject = "Reunião de Diagnóstico (Agendada)"

        return self.create_activity(
            subject=subject,
            type="meeting",
            due_date=due_date,
            due_time=due_time,
            person_id=person_id,
            org_id=org_id,
            deal_id=deal_id
        )
    
    def _get(self, endpoint: str, params: dict = None):
        """Método auxiliar para requisições GET"""
        url = f"{self.base_url}/{endpoint}?api_token={self.api_token}"
        response = requests.get(url, params=params, headers=self._get_headers())
        
        if response.status_code == 200:
            return response.json()
        else:
            logger.error(f"[PIPEDRIVE_CRM_INTEGRATION] Erro ao buscar em {endpoint}: {response.text}")
            return None
    
    def _post(self, endpoint: str, data: dict):
        """Método auxiliar para requisições POST"""
        url = f"{self.base_url}/{endpoint}?api_token={self.api_token}"
        # print(f"Requisição POST para {url}.")
        response = requests.post(url, json=data, headers=self._get_headers())

        # print(response.json())
        
        if response.status_code == 201:
            return response.json()['data']
        else:
            logger.error(f"[PIPEDRIVE_CRM_INTEGRATION] Erro ao criar em {endpoint}: {response.text}")
            return None

    def _put(self, endpoint: str, resource_id: int, data: dict):
        """Método auxiliar para requisições PUT (Atualização)"""
        url = f"{self.base_url}/{endpoint}/{resource_id}?api_token={self.api_token}"
        response = requests.put(url, json=data, headers=self._get_headers())
        
        if response.status_code == 200:
            logger.info(f"[PIPEDRIVE_CRM_INTEGRATION] Atualização realizada com sucesso no ID {resource_id}")
            return response.json()['data']
        else:
            logger.error(f"[PIPEDRIVE_CRM_INTEGRATION] Erro ao atualizar {endpoint}/{resource_id}: {response.text}")
            return None

    def create_organization(self, name: str, motivo_ia: str = "") -> dict:
        """
        Cria a organização (Empresa).
        """

        data = {
            "name": name,
            "owner_id": self.owner_id,
            "visible_to": self.visible_to,
            # self.FIELD_MOTIVO_IA: motivo_ia
        }
        
        logger.info(f"[PIPEDRIVE_CRM_INTEGRATION] 🏢 Criando Organização no Pipedrive")
        return self._post("organizations", data)
    
    def update_organization_details(self, org_id: int, segmento: str = None, faturamento: int = None, funcionarios: int = None, produto: str = None, desafio: list = None, momento: int = None, capacidade_investimento: int = None):
        data = {}

        if segmento: data[self.FIELD_SEGMENTO] = segmento
        if faturamento: data[self.FIELD_FATURAMENTO] = faturamento
        if funcionarios: data[self.FIELD_FUNCIONARIOS] = funcionarios
        if produto: data[self.FIELD_PRODUTO] = produto
        if desafio: data[self.FIELD_DESAFIO] = desafio
        if momento: data[self.FIELD_MOMENTO] = momento
        if capacidade_investimento: data[self.FIELD_CAPACIDADE_INVESTIMENTO] = capacidade_investimento

        if not data: return None

        logger.info(f"[PIPEDRIVE_CRM_INTEGRATION] Atualizando dados da Organização {org_id}...")
        return self._put("organizations", org_id, data)

    def create_person(self, name: str, org_id: int, email: str = None, phone: str = None) -> dict:
        """
        Cria a pessoa (Lead) vinculada à Organização.
        """
        data = {
            "name": name,
            "email": email,
            "phone": phone,
            "owner_id": self.owner_id,
            "visible_to": self.visible_to,
            "org_id": org_id
        }

        logger.info(f"[PIPEDRIVE_CRM_INTEGRATION] 👤 Criando Pessoa no Pipedrive")
        return self._post("persons", data)

    def create_deal(self, title: str, person_id: int, org_id: int, value: float = 0) -> dict:
        """
        Cria o Negócio (Deal/Card).
        """
        data = {
            "title": title,
            "person_id": person_id,
            "org_id": org_id,
            "pipeline_id": 1,
            "stage_id": 1,
            "value": value,
            "currency": "BRL",
            "status": "open",
            "probability": 70,
            "visible_to": self.visible_to,
            # "owner_id": self.owner_id
        }

        logger.info(f"[PIPEDRIVE_CRM_INTEGRATION] 💰 Criando Negócio no Pipedrive")
        return self._post("deals", data)

    def update_deal_stage(self, deal_id: int, new_stage_id: int):
        """
        Move o card para uma nova etapa do funil.
        """
        data = {
            "stage_id": new_stage_id
        }
        logger.info(f"[PIPEDRIVE_CRM_INTEGRATION] 🚀 Movendo Deal {deal_id} para etapa {new_stage_id}...")
        return self._put("deals", deal_id, data)
    
    def _get_pipedrive_option_id(self, category: str, value: str) -> int:
        """
        Traduz o texto do Front-end para o ID numérico do Pipedrive.
        """
        if not value:
            return None

        # faturamento_map = {
        #     "Até R$100 mil/ano": 27,
        #     "R$100 mil a R$500 mil/ano": 28,
        #     "R$500 mil a R$2 milhões/ano": 29,
        #     "R$2 milhões/ano a R$10 milhões/ano": 30,
        #     "Acima de R$10 milhões/ano": 31
        # }

        # funcionarios_map = {
        #     "apenas eu": 32,
        #     "1 a 5": 33,
        #     "6 a 20": 34,
        #     "21 a 50": 35,
        #     "51 a 200": 36,
        #     "+200": 37
        # }

        faturamento_map = {
            "Até R$100 mil/ano": 173,
            "R$100 mil a R$500 mil/ano": 174,
            "R$500 mil a R$2 milhões/ano": 175,
            "R$2 milhões/ano a R$10 milhões/ano": 176,
            "Acima de R$10 milhões/ano": 177
        }

        funcionarios_map = {
            "apenas eu": 178,
            "1 a 5": 179,
            "6 a 20": 180,
            "21 a 50": 181,
            "51 a 200": 182,
            "+200": 183
        }

        desafio_map = {
            "Consumo muitos tutoriais, mas não sei qual stack de ferramentas realmente gera lucro e escala.": 184,
            "Tenho medo de fechar um contrato e não saber estruturar um fluxo que funcione no mundo real sem quebrar.": 185,
            "Não sei como cobrar o valor justo ou demonstrar o ROI da solução de IA para o cliente.": 186,
            "Sinto que o que eu faço qualquer um faz com o ChatGPT; preciso criar Agentes de Elite que resolvam problemas complexos.": 187,
            "Não tenho um método para prospectar leads qualificados e dependo apenas de indicações esporádicas.": 188,
            "Já vendo alguns projetos, mas a entrega consome todo o meu tempo e não consigo escalar meu faturamento.": 189
        }

        momento_map = {
            "Trabalho em outra área, mas quero aproveitar o boom da IA para construir minha liberdade financeira e migrar de carreira.": 190,
            "Já sou dono de agência (marketing, software, etc) e preciso integrar IA urgentemente para não perder mercado.": 191,
            "Faço alguns freelas de automação, mas sinto que sou visto como um amador e quero me tornar uma referência de elite.": 192,
            "Tenho facilidade técnica, mas percebi que preciso aprender a vender e gerir um negócio de IA para ganhar dinheiro de verdade.": 193,
            "Sou sócio/gestor de uma empresa e quero aprender o método para implementar soluções internas e reduzir custos.": 194,
            "Domino a técnica e quero estruturar meu conhecimento para ensinar outros, mas me falta o método de escala.": 195
        }

        investimento_map = {
            "Entendo o valor de um método testado e o investimento está totalmente dentro do meu planejamento para crescer agora": 196,
            "Tenho o capital, mas meu foco é validar como este acompanhamento vai acelerar meu ROI": 197,
            "Tenho prioridade total em resolver isso, mas precisaria de opções de parcelamento": 198,
            "Reconheço que preciso de ajuda, mas no momento não possuo recurso financeiro para investir em uma mentoria profissional.": 199
        }

        try:
            if category == "faturamento":
                return faturamento_map.get(value)
            elif category == "funcionarios":
                return funcionarios_map.get(value)
            elif category == "desafio":
                return desafio_map.get(value)
            elif category == "momento":
                return momento_map.get(value)
            elif category == "investimento":
                return investimento_map.get(value)
        except Exception as e:
            logger.error(f"[PIPEDRIVE_CRM_INTEGRATION] Erro ao mapear valor '{value}' para categoria '{category}': {e}")
            return None
        
        return None

    def process_new_lead(self, company_name: str, lead_name: str, motivo_ia: str = "0a605b9668c110080cd956312ac51b11a7855621", email: str = None, phone: str = None) -> dict | None:
        """
        Função Mestra: Executa todo o fluxo em ordem.
        1. Cria Org -> 2. Cria Pessoa -> 3. Cria Deal
        """
        # 1. Criar Organização
        org = self.create_organization(company_name, motivo_ia)
        if not org: return None
        org_id = org['id']

        # 2. Criar Pessoa
        person = self.create_person(lead_name, org_id, email, phone)
        if not person: return None
        person_id = person['id']

        # 3. Criar Deal
        deal_title = f"{company_name} | {lead_name}"
        
        deal = self.create_deal(deal_title, person_id, org_id)
        if not deal: return None
        deal_id = deal['id']

        data_id = {
            "person_id": person_id,
            "org_id": org_id,
            "deal_id": deal_id
        }
        
        if deal:
            logger.info(f"[PIPEDRIVE_CRM_INTEGRATION] Fluxo completo! Deal ID: {deal['id']}")
            return data_id
        return None

