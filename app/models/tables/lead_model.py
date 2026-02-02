from mongoengine import Document, StringField, DateTimeField, IntField, BooleanField
from datetime import datetime
from typing import Dict, List

class Lead(Document):
    meta = {"collection": "leads"}

    UPDATABLE_FIELDS = {
        "name",
        "phone",
        "email",
        "business_name",
        "business_tracking",
        "product_of_interest",
        "job_position",
        "invoicing",
        "collaborators",
        "scheduling_day",
        "confirmation_sent",
        "recovery_sent",
        "reminder_sent"
    }

    name = StringField(required=True)
    phone = StringField(required=True, unique=True)
    email = StringField(required=True, unique=True)
    business_name = StringField()
    business_tracking = StringField()
    invoicing = StringField()
    product_of_interest = StringField()
    collaborators = StringField()
    scheduling_day = DateTimeField()
    leadtoken = StringField()
    id_person_pipedrive = IntField()
    id_organization_pipedrive = IntField()
    id_deal_pipedrive = IntField()
    
    confirmation_sent = BooleanField(default=False)
    recovery_sent = BooleanField(default=False)
    reminder_sent = BooleanField(default=False)
    
    created_at = DateTimeField(default=datetime.now)
    updated_at = DateTimeField(default=datetime.now)

    def save(self, *args, **kwargs):
        if not self.created_at:
            self.created_at = datetime.now()
        self.updated_at = datetime.now()
        return super().save(*args, **kwargs)

    @classmethod
    def update_by_id(cls, lead_phone: str, data: Dict) -> "Lead":
        update_data = {
            f"set__{k}": v
            for k, v in data.items()
            if k in cls.UPDATABLE_FIELDS
        }

        if not update_data:
            raise ValueError("Nenhum campo válido para atualizar")

        update_data["set__updated_at"] = datetime.now()

        try:
            updated = cls.objects(id=lead_phone).update_one(**update_data)
        except Exception as e:
            raise ValueError(str(e))

        if not updated:
            raise ValueError("Lead não encontrado")

        return cls.objects.get(id=lead_phone)

    @classmethod
    def find_pending_confirmations(cls) -> List["Lead"]:
        """
        Retorna apenas leads que têm agendamento marcado (ne=None) 
        e ainda NÃO receberam a confirmação (False).
        """
        return cls.objects(scheduling_day__ne=None, confirmation_sent=False)

    @classmethod
    def find_abandoned_leads(cls) -> List["Lead"]:
        """
        Retorna apenas leads que NÃO têm agendamento (None)
        e ainda NÃO receberam a mensagem de recuperação (False).
        """
        return cls.objects(scheduling_day=None, recovery_sent=False)
    
    @classmethod
    def find_upcoming_meetings(cls) -> List["Lead"]:
        """
        Retorna leads com agendamento marcado e que 
        ainda NÃO receberam o lembrete de 1h antes (False).
        """
        return cls.objects(scheduling_day__ne=None, reminder_sent=False)

    def to_dict(self) -> dict:
        return {
            "id": str(self.id),
            "name": self.name,
            "phone": self.phone,
            "email": self.email,
            "business_name": self.business_name,
            "business_tracking": self.business_tracking,
            "invoicing": self.invoicing,
            "product_of_interest": self.product_of_interest,
            "collaborators": self.collaborators,
            "scheduling_day": self.scheduling_day.isoformat() if self.scheduling_day else None,
            "leadtoken": self.leadtoken,
            "id_person_pipedrive": self.id_person_pipedrive,
            "id_organization_pipedrive": self.id_organization_pipedrive,
            "id_deal_pipedrive": self.id_deal_pipedrive,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "confirmation_sent": self.confirmation_sent,
            "recovery_sent": self.recovery_sent,
            "reminder_sent": self.reminder_sent
        }