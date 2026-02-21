import os
import re
import time
from dotenv import load_dotenv
import requests
from app.utils.logging_config import logger


load_dotenv()

class ZAPIClient:
    def __init__(self):
        self.base_url = os.getenv("ZAPI_BASE_URL")
        self.instance_id = os.getenv("ZAPI_INSTANCE_ID")
        self.instance_token = os.getenv("ZAPI_INSTANCE_TOKEN")
        self.client_token = os.getenv("ZAPI_CLIENT_TOKEN")
        
        # Headers padrão
        self.headers = {
            "Content-Type": "application/json",
            "Client-Token": self.client_token
        }

        # Validação inicial das variáveis de ambiente
        if not all([self.base_url, self.instance_id, self.instance_token, self.client_token]):
            logger.info("[ZAPI_INTEGRATION] Aviso: Variáveis de ambiente incompletas.")

    def _get_api_url(self, endpoint: str) -> str:
        """Monta a URL completa baseada no padrão da Z-API."""
        # Remove barras extras do final da base_url se houver
        base = self.base_url.rstrip('/')
        return f"{base}/instances/{self.instance_id}/token/{self.instance_token}/{endpoint}"

    def _format_phone(self, phone: str) -> str:
        """Limpa e formata o telefone para o padrão DDI+DDD+NUMERO."""
        if not phone:
            return None

        # Remove tudo que não for dígito
        clean_phone = re.sub(r"\D", "", str(phone))

        # Se tiver 10 ou 11 dígitos, assume que é BR e falta o DDI 55
        if 10 <= len(clean_phone) <= 11:
            clean_phone = f"55{clean_phone}"

        # Validação básica de tamanho (Ex: 55 + 11 + 999999999 = 12 a 13 digitos)
        if len(clean_phone) < 12:
            logger.warning(f"[ZAPI_INTEGRATION] Telefone inválido (muito curto)")
            return None
            
        return clean_phone

    def send_message(self, phone: str, message: str) -> bool:
        """Envia uma mensagem de texto simples com retry logic."""
        
        # 1. Validações
        target_phone = self._format_phone(phone)
        if not target_phone:
            logger.warning("[ZAPI_INTEGRATION] Falha: Telefone inválido.")
            return False

        if not message or not isinstance(message, str):
            logger.warning("[ZAPI_INTEGRATION] Falha: Mensagem vazia ou inválida.")
            return False

        # 2. Preparação
        url = self._get_api_url("send-text")
        
        payload = {
            "phone": target_phone,
            "message": message,
        }

        # print(f"[Z-API] Enviando para {url} com payload: {payload}")


        # 3. Envio com Retry (3 tentativas)
        max_attempts = 3
        for attempt in range(1, max_attempts + 1):
            try:
                logger.info(f"[ZAPI_INTEGRATION] Enviando para mensagem para contato (Tentativa {attempt})...")
                
                response = requests.post(url, json=payload, headers=self.headers, timeout=10)
                response.raise_for_status() # Levanta erro se status code for 4xx ou 5xx

                logger.info(f"[ZAPI_INTEGRATION] Status: {response.status_code} Resposta: {response.text}")

                return True

            except requests.exceptions.RequestException as e:
                logger.warning(f"[ZAPI_INTEGRATION] Falha definitiva ao enviar para {target_phone}. Erro: {e}")
                continue
        
        return False