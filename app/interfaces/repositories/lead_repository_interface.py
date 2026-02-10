from abc import ABC, abstractmethod
from typing import Dict, Optional, List
from app.models.tables.lead_model import Lead


class LeadRepositoryInterface(ABC):

    @abstractmethod
    def create(self, lead: Lead) -> Lead:
        pass

    @abstractmethod
    def find_by_email(self, email: str) -> Optional[Lead]:
        pass

    @abstractmethod
    def find_by_phone(self, phone: str) -> Optional[Lead]:
        pass

    @abstractmethod
    def find_by_token(self, token: str) -> Optional[Lead]:
        pass

    @abstractmethod
    def list_all(self) -> List[Lead]:
        pass

    @abstractmethod
    def update_by_phone(self, lead_phone: str, data: Dict) -> Lead:
        pass

    @abstractmethod
    def find_pending_confirmations(self) -> List["Lead"]:
        pass

    @abstractmethod
    def find_abandoned_leads(self) -> List["Lead"]:
        pass

    @abstractmethod
    def find_upcoming_meetings(self) -> List["Lead"]:
        pass

