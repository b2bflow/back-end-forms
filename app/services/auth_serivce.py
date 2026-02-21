from datetime import datetime
from typing import Dict
from app.interfaces.repositories.lead_repository_interface import LeadRepositoryInterface
from app.interfaces.services.auth_service_interface import AuthServiceInterface
from app.dto.lead_response_dto import LeadResponseDTO


class AuthService(AuthServiceInterface):
    def __init__(self, lead_repository: LeadRepositoryInterface):
        self.lead_repository = lead_repository 

    def remove_token(self, data: Dict) -> Dict:
        pass

    def verify_token(self, data: Dict) -> Dict:
        lead = self.lead_repository.find_by_token(data["token"])

        if not lead:
            return {"error": "Token inválido", "status": 401}

        sched_day = lead.scheduling_day

        appt_date = None
        appt_time = None

        if sched_day and isinstance(sched_day, datetime):
            appt_date = sched_day.strftime('%Y-%m-%d')
            appt_time = sched_day.strftime('%H:%M')

        return LeadResponseDTO.existing_lead(lead, appt_date, appt_time)