from datetime import datetime
from typing import Dict
from app.models.tables.lead_model import Lead

class LeadResponseDTO:

    @staticmethod
    def minimal(lead: Lead) -> Dict:
        return {
            "name": lead.name,
            "business_name": lead.business_name
        }

    @staticmethod
    def existing_lead(lead: Lead, appt_date: str = None, appt_time: str = None) -> Dict:
        return {
            "id": str(lead.id),
            "name": lead.name,
            "business_name": lead.business_name,
            "email": lead.email,
            "phone": lead.phone,
            "job_position": lead.job_position,
            "appointmentDate": appt_date,
            "appointmentTime": appt_time,
        }