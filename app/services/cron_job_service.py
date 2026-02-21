from datetime import datetime, timedelta
import dateutil.tz
from app.interfaces.repositories.lead_repository_interface import LeadRepositoryInterface
from app.interfaces.services.cron_job_service_interface import CronJobServiceInterface
from app.integrations.zapi_integration import ZAPIClient
from app.utils.logging_config import logger


class CronJobService(CronJobServiceInterface):
    def __init__(self, repository: LeadRepositoryInterface):
        self.lead_repository = repository
        self.zapi = ZAPIClient()
        
        # Definição de Fuso Horário (Brasil)
        self.TZ_BRASIL = dateutil.tz.gettz('America/Sao_Paulo')
        
        # Configurações de tempo ORIGINAIS (1 hora)
        self.DELAY_CONFIRMATION = timedelta(hours=1)
        self.DELAY_RECOVERY = timedelta(hours=1)

    def _get_now(self):
        """Retorna a hora atual com Fuso Horário correto."""
        return datetime.now(self.TZ_BRASIL)

    def _ensure_timezone(self, dt: datetime):
        """
        Garante que a data seja interpretada como Horário de Brasília.
        Corrige o problema onde o banco salva horário local com flag UTC.
        """
        if dt is None: return None
        
        # 1. Remove qualquer info de fuso (UTC/Z) para pegar a hora 'limpa'
        if dt.tzinfo is not None:
            dt = dt.replace(tzinfo=None)
            
        # 2. Força o fuso Brasil (Ex: se era 10:30Z, vira 10:30 Brasil)
        return dt.replace(tzinfo=self.TZ_BRASIL)

    def send_confirmation_messager(self):
        """
        Envia mensagem de confirmação 1h APÓS o cliente ter realizado o agendamento.
        """
        logger.info("[CRON_JOB_SERVICE] Iniciando verificação de confirmação de agendamento...")
        
        leads = self.lead_repository.find_pending_confirmations() 
        now = self._get_now()
        
        count = 0
        
        for lead in leads:
            try:
                if not lead.scheduling_day or getattr(lead, 'confirmation_sent', False):
                    continue

                booking_time = getattr(lead, 'updated_at', lead.created_at)
                booking_time = self._ensure_timezone(booking_time)

                if now - booking_time >= self.DELAY_CONFIRMATION:
                    
                    first_name = lead.name.split()[0] if lead.name else "visitante"
                    meeting_date = self._ensure_timezone(lead.scheduling_day)
                    date_str = meeting_date.strftime('%d/%m às %H:%M')
                    
                    msg = f"Eaee {first_name}! Tudo certo?\n\nAqui é o Marcelo Baldi da b2bflow.\n\nVi que você agendou uma reunião comigo dia {date_str}. e antes quero te ligar e entender melhor seu cenário para tornar nossa call mais produtiva\n\nQual horário posso te ligar?"
                    
                    if self.zapi.send_message(lead.phone, msg):
                        self.lead_repository.update_by_phone(lead.phone, {"confirmation_sent": True})
                        logger.info(f"[CRON_JOB_SERVICE] Confirmação enviada para: {lead.name}")
                        count += 1
            
            except Exception as e:
                logger.error(f"[CRON_JOB_SERVICE] Erro confirmação lead {getattr(lead, 'id', 'Unknown')}: {e}")
        return f"Processamento finalizado. {count} confirmações enviadas."

    def send_recovery_message(self):
        """
        Recupera leads que se cadastraram há mais de 1h e NÃO agendaram.
        """
        logger.info("[CRON_JOB_SERVICE] Iniciando verificação de recuperação (abandono)...")
        
        leads = self.lead_repository.find_abandoned_leads()
        now = self._get_now()
        
        count = 0

        for lead in leads:
            try:
                if lead.scheduling_day is not None or getattr(lead, 'recovery_sent', False):
                    continue
                
                created_at = self._ensure_timezone(lead.created_at)

                if now - created_at >= self.DELAY_RECOVERY:
                    
                    first_name = lead.name.split()[0] if lead.name else "visitante"
                    msg = f"Eaee {first_name}! Tudo certo?\n\nAqui é o Marcelo Baldi da b2bflow.\n\nVi que entrou em contato para atender\ncomo implementar IA na operação, e acredito que posso ajudar\n\nQual horário posso te ligar e entender melhor seu momento?"
                    
                    if self.zapi.send_message(lead.phone, msg):
                        self.lead_repository.update_by_phone(lead.phone, {"recovery_sent": True})
                        logger.info(f"[CRON_JOB_SERVICE] Recuperação enviada para: {lead.name}")
                        count += 1

            except Exception as e:
                logger.error(f"[CRON_JOB_SERVICE] Erro recuperação lead {getattr(lead, 'id', 'Unknown')}: {e}")
        return f"Processamento finalizado. {count} recuperações enviadas."
    
    def send_meeting_reminder(self):
        """
        Envia um lembrete se faltar aproximadamente 1 hora para a reunião.
        (Janela de 50 a 70 minutos para garantir captura)
        """
        logger.info("[CRON_JOB_SERVICE] Iniciando verificação de lembrete de reunião...")
        
        leads = self.lead_repository.find_upcoming_meetings()
        now = self._get_now()
        count = 0

        for lead in leads:
            try:
                if not lead.scheduling_day or getattr(lead, 'reminder_sent', False):
                    continue

                meeting_time = self._ensure_timezone(lead.scheduling_day)
                time_remaining = meeting_time - now

                if timedelta(minutes=50) <= time_remaining <= timedelta(minutes=70):
                    
                    first_name = lead.name.split()[0] if lead.name else "Cliente"
                    time_str = meeting_time.strftime('%H:%M')
                    
                    msg = f"Bom dia {first_name}! Tudo certo?\n\nPara facilitar seu acesso nossa reunião {time_str}\nsegue o link da call.\n\nlink:{lead.meet_link}\n\nQualquer coisa só chamar!"

                    if self.zapi.send_message(lead.phone, msg):
                        self.lead_repository.update_by_phone(lead.phone, {"reminder_sent": True})
                        logger.info(f"[CRON_JOB_SERVICE] Lembrete 1H enviado para: {lead.name}")
                        count += 1
            
            except Exception as e:
                logger.error(f"[CRON_JOB_SERVICE] Erro lembrete lead {getattr(lead, 'id', 'Unknown')}: {e}")
        return f"Processamento finalizado. {count} lembretes enviados."
