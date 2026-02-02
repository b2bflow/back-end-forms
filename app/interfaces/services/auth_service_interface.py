from abc import ABC, abstractmethod
from typing import Dict, List


class AuthServiceInterface(ABC):

    @abstractmethod
    def remove_token(self, data: Dict) -> Dict:
        pass
    
    @abstractmethod
    def verify_token(self, data: Dict) -> Dict:
        pass