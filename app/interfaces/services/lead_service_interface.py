from abc import ABC, abstractmethod
from typing import Dict, List


class LeadServiceInterface(ABC):

    @abstractmethod
    def create_lead(self, data: Dict) -> Dict:
        pass

    @abstractmethod
    def list_leads(self) -> List[Dict]:
        pass

    @abstractmethod
    def update_lead(self, data: Dict) -> Dict:
        pass
