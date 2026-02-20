from mongoengine import Document, EmbeddedDocument, StringField, DateTimeField, IntField, BooleanField, EmbeddedDocumentField, ListField
from datetime import datetime
from typing import Dict, List, Optional

class LeadFollowupData(EmbeddedDocument):
    """Dados vindos do formulário de Consultoria/Followup"""
    challenge = ListField(StringField())
    customer_stage = StringField()
    investment_capacity = StringField()
    

class SalesLeadData(EmbeddedDocument):
    """Dados vindos do formulário de Venda"""
    business_tracking = StringField()
    invoicing = StringField()
    product_of_interest = StringField()
    collaborators = StringField()

# 2. O Documento Principal
class Lead(Document):
    meta = {
        "collection": "leads",
        "indexes": [
            "phone",
            "email",
            "scheduling_day",
            "confirmation_sent"
        ]
    }

    name = StringField(required=True)
    phone = StringField(required=True, unique=True)
    email = StringField(required=True, unique=True)
    business_name = StringField()
    meet_link = StringField()
    
    scheduling_day = DateTimeField()
    leadtoken = StringField()
    
    id_person_pipedrive = IntField()
    id_organization_pipedrive = IntField()
    id_deal_pipedrive = IntField()
    
    type_lead = StringField(required=True, choices=('consultoria', 'venda'))

    confirmation_sent = BooleanField(default=False)
    recovery_sent = BooleanField(default=False)
    reminder_sent = BooleanField(default=False)
    
    created_at = DateTimeField(default=datetime.now)
    updated_at = DateTimeField(default=datetime.now)

    followup_data = EmbeddedDocumentField(LeadFollowupData)
    sales_data = EmbeddedDocumentField(SalesLeadData)

    def save(self, *args, **kwargs):
        if not self.created_at:
            self.created_at = datetime.now()
        self.updated_at = datetime.now()
        return super().save(*args, **kwargs)

    @classmethod
    def update_by_phone(cls, lead_phone: str, data: Dict) -> "Lead":
        lead = cls.objects(phone=lead_phone).first()
        if not lead:
            raise ValueError("Lead não encontrado")
        
        for key, value in data.items():
            if hasattr(lead, key) and key not in ['followup_data', 'sales_data']:
                setattr(lead, key, value)
            
        if lead.type_lead == 'consultoria':
            if not lead.followup_data:
                lead.followup_data = LeadFollowupData()
            for key, value in data.items():
                if hasattr(lead.followup_data, key):
                    setattr(lead.followup_data, key, value)

        elif lead.type_lead == 'venda':
            if not lead.sales_data:
                lead.sales_data = SalesLeadData()
            for key, value in data.items():
                if hasattr(lead.sales_data, key):
                    setattr(lead.sales_data, key, value)

        lead.save()
        return lead

    @classmethod
    def find_pending_confirmations(cls) -> List["Lead"]:
        """Leads com agendamento marcado mas sem confirmação enviada."""
        return cls.objects(scheduling_day__ne=None, confirmation_sent=False)

    @classmethod
    def find_abandoned_leads(cls) -> List["Lead"]:
        """Leads sem agendamento e sem recuperação enviada."""
        return cls.objects(scheduling_day=None, recovery_sent=False)

    @classmethod
    def find_upcoming_meetings(cls) -> List["Lead"]:
        """Leads agendados sem lembrete enviado."""
        return cls.objects(scheduling_day__ne=None, reminder_sent=False)

    
    def to_dict(self) -> dict:
        result = {
            "id": str(self.id),
            "name": self.name,
            "phone": self.phone,
            "email": self.email,
            "type_lead": self.type_lead,
            
            "business_name": self.business_name,
            "meet_link": self.meet_link,
            "scheduling_day": self.scheduling_day.isoformat() if self.scheduling_day else None,
            "leadtoken": self.leadtoken,

            "id_person_pipedrive": self.id_person_pipedrive,
            "id_organization_pipedrive": self.id_organization_pipedrive,
            "id_deal_pipedrive": self.id_deal_pipedrive,
            
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "confirmation_sent": self.confirmation_sent,
            "recovery_sent": self.recovery_sent,
            "reminder_sent": self.reminder_sent,
        }

        specific_data = {}
        
        if self.type_lead == 'consultoria' and self.followup_data:
            specific_data = self.followup_data.to_mongo().to_dict()
            
        elif self.type_lead == 'venda' and self.sales_data:
            specific_data = self.sales_data.to_mongo().to_dict() 

        result.update(specific_data)

        return result