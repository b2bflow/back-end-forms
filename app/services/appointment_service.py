import dateutil
from app.integrations.pipedrive_crm_integration import PipedriveClient
from app.interfaces.repositories.lead_repository_interface import LeadRepositoryInterface
from app.interfaces.services.appointment_service_interface import AppointmentServiceInterface
from app.integrations.google_calendar_integration import create_event, get_available_slots
from app.utils.logging_config import logger
from datetime import datetime


class AppointmentService(AppointmentServiceInterface):

    def __init__(self, repository: LeadRepositoryInterface):
        self.repository = repository
        self.pipedrive_client = PipedriveClient()

    def create_appointment(self, data: dict) -> dict:
        logger.info(f"[APPOINTMENT_SERVICE] Criando agendamento.")
        lead = self.repository.find_by_token(data.get("leadToken"))
        if not lead:
            logger.error("[APPOINTMENT_SERVICE] Lead nao encontrado")
            return {"error": "Lead não encontrado"}

        try:
            start_time_str = f"{data['date']} {data['time']}"
            start_time_obj = datetime.strptime(start_time_str, '%Y-%m-%d %H:%M')
            start_time_obj = start_time_obj.replace(tzinfo=dateutil.tz.gettz('America/Sao_Paulo'))

            lead.scheduling_day = start_time_obj

        except (KeyError, ValueError) as e:
            logger.error(f"[APPOINTMENT_SERVICE] Erro ao processar data/hora: {e}")
            return {"error": f"Dados de data/hora ausentes ou inválidos: {e}"}

        lead_name = lead.get('name') if isinstance(lead, dict) else getattr(lead, 'name', 'Desconhecido')
        business = lead.get('business_name', 'N/A') if isinstance(lead, dict) else getattr(lead, 'business_name', 'N/A')
        
        summary = f"Reunião: {lead_name} | {business}"
        description = (
            f"Detalhes do Lead:\n"
            f"- Origem: Formulário de Captura\n"
            f"- Data da Requisição: {datetime.now().strftime('%d/%m/%Y %H:%M')}"
        )

        try:
            logger.info(f"[APPOINTMENT_SERVICE] Iniciando integração Google Calendar para {start_time_obj}...")
            event = create_event(
                summary=summary, 
                description=description, 
                start_time=start_time_obj,
                lead_email=lead.email,
                lead_name=lead.name
            )

            if event and 'htmlLink' in event:
                logger.info(f"[APPOINTMENT_SERVICE] Sucesso! Evento disponível em: {event['htmlLink']}")

                self.repository.update_by_phone(lead.phone, {"scheduling_day": start_time_obj})

                self.repository.update_by_phone(lead.phone, {"meet_link": event.get('hangoutLink')})

                logger.info(f"[APPOINTMENT_SERVICE] Deal ID: {lead.id_deal_pipedrive} - {lead.business_name} | {lead.name}")

                self.pipedrive_client.update_deal_stage(
                    deal_id=lead.id_deal_pipedrive,
                    new_stage_id= 3,
                )

                self.pipedrive_client.schedule_confirmation_call(
                    meeting_datetime=start_time_obj,
                    person_id=lead.id_person_pipedrive,
                    org_id=lead.id_organization_pipedrive,
                    deal_id=lead.id_deal_pipedrive
                )

                self.pipedrive_client.schedule_meeting_activity(
                    meeting_datetime=start_time_obj,
                    person_id=lead.id_person_pipedrive,
                    org_id=lead.id_organization_pipedrive,
                    deal_id=lead.id_deal_pipedrive
                )

                return {
                    "success": True, 
                    "expires_at": start_time_obj,
                    "event_id": event.get('id')
                }
            
            return {"success": False, "error": "Resposta inválida da API do Google"}
                
        except Exception as e:
            logger.error(f"[APPOINTMENT_SERVICE] Falha crítica na criação do evento: {str(e)}")
            return {"success": False, "error": "Ocorreu um erro interno ao processar o agendamento."}

    def list_busy_slots(self) -> list:
        try:
            busy_slots = get_available_slots()
            return busy_slots if busy_slots is not None else []
        except Exception as e:
            logger.error(f"[APPOINTMENT_SERVICE] Erro ao listar horários ocupados: {e}")
            return []