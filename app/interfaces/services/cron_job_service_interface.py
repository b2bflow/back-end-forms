from abc import ABC, abstractmethod
from typing import Dict, List

class CronJobServiceInterface(ABC):
    @abstractmethod
    def send_confirmation_messager(self) -> List[Dict]:
        pass

    @abstractmethod
    def send_recovery_message(self) -> List[Dict]:
        pass

    @abstractmethod
    def send_meeting_reminder(self) -> List[Dict]:
        pass