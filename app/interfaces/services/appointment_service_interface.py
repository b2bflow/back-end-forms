from abc import ABC, abstractmethod
from typing import Dict, List


class AppointmentServiceInterface(ABC):

    @abstractmethod
    def create_appointment(self, data: Dict) -> Dict:
        pass

    @abstractmethod
    def list_busy_slots(self) -> List[Dict]:
        pass