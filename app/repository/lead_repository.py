from app.interfaces.repositories.lead_repository_interface import LeadRepositoryInterface
from app.models.tables.lead_model import Lead
from typing import Dict, Optional, List


class LeadRepository(LeadRepositoryInterface):

    def create(self, lead: Lead) -> Lead:
        return lead.save()

    def find_by_email(self, email: str) -> Optional[Lead]:
        return Lead.objects(email=email).first()

    def find_by_phone(self, phone: str) -> Optional[Lead]:
        return Lead.objects(phone=phone).first()
    
    def find_by_token(self, token: str) -> Optional[Lead]:
        return Lead.objects(leadtoken=token).first()
    
    def list_all(self) -> List[Lead]:
        return list(Lead.objects())
    
    def update_by_id(self, lead_id: str, data: Dict) -> Lead:
        return Lead.update_by_id(lead_id, data)
    
    def find_pending_confirmations(self) -> List[Lead]:
        return Lead.find_pending_confirmations()
    
    def find_abandoned_leads(self) -> List[Lead]:
        return Lead.find_abandoned_leads()
    
    def find_upcoming_meetings(self) -> List["Lead"]:
        return Lead.find_upcoming_meetings()
