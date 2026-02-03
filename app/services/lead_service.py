from app.interfaces.services.lead_service_interface import LeadServiceInterface
from app.interfaces.repositories.lead_repository_interface import LeadRepositoryInterface
from app.integrations.pipedrive_crm_integration import PipedriveClient
from app.models.tables.lead_model import Lead
from typing import Dict, List

from app.security.session_token import SessionTokenService


class LeadService(LeadServiceInterface):

    def __init__(self, repository: LeadRepositoryInterface):
        self.repository = repository
        self.pipedrive_client = PipedriveClient()

    def create_lead(self, data: Dict) -> Dict:
        # print(data)

        lead = self.repository.find_by_email(data["email"])

        if lead is not None:
            if lead.email == data["email"] and lead.phone == data["phone"]:

                lead.confirmation_sent = False
                lead.recovery_sent = False
                lead.reminder_sent = False

                lead = self.repository.update_by_id(str(lead.id), lead.to_dict())

                return {
                    "message": "Lead já cadastrado",
                    "token": lead.leadtoken,
                    "status": "updated",
                }

        data["scheduling_day"] = None

        data["leadtoken"] = SessionTokenService.generate(
            lead_id=data["phone"],
            expires_at=None,
        )

        try:
            lead = Lead(**data)
            
            data_id = self.pipedrive_client.process_new_lead(
                company_name=data["business_name"],
                lead_name=data["name"],
                email=data["email"],
                phone=data["phone"],
            )

            lead.id_person_pipedrive = data_id["person_id"]
            lead.id_organization_pipedrive = data_id["org_id"]
            lead.id_deal_pipedrive = data_id["deal_id"]

            lead = self.repository.create(lead)

            return {
                "message": "Lead criado com sucesso",
                "token": lead.leadtoken,
                "status": "created",
            }
        except Exception as e:
            print(f"Falha na criação do lead: {str(e)}")
            raise ValueError(str(e))

    def update_lead(self, data: Dict) -> Dict:
        print(f"Dados recebidos: {data}")
        lead = self.repository.find_by_phone(data["phone"])

        if not lead:
            raise ValueError("Lead nao encontrado")

        updated_lead = self.repository.update_by_id(
            lead_id=str(lead.id),
            data=data
        )

        try:
            # organization_id = self.pipedrive_client.get_organization_by_name(data["business_name"])

            # if not organization_id:
            #     raise ValueError("Organização não encontrada no Pipedrive")

            id_faturamento = self.pipedrive_client._get_pipedrive_option_id("faturamento", data.get("invoicing"))
            id_funcionarios = self.pipedrive_client._get_pipedrive_option_id("funcionarios", data.get("collaborators"))

            self.pipedrive_client.update_organization_details(
                org_id=lead.id_organization_pipedrive,
                segmento=data.get("business_tracking"),
                faturamento=id_faturamento,
                funcionarios=id_funcionarios,
                produto=data.get("product_of_interest"),
            )

            deal_title = f"{data['business_name']} | {data['name']}"
            # deal_id = self.pipedrive_client.get_deal_by_title(deal_title)
            deal_id = lead.id_deal_pipedrive

            if deal_id:
                self.pipedrive_client.update_deal_stage(
                    deal_id=deal_id,
                    new_stage_id=2,
                )
                
                if "stage_id" in data:
                    self.pipedrive_client.update_deal_stage(
                        deal_id=deal_id,
                        new_stage_id=data["stage_id"],
                    )
            else:
                print(f"Aviso: Deal '{deal_title}' não encontrado para atualização.")

            return {
                "message": "Lead atualizado com sucesso",
                "token": updated_lead.leadtoken,
                "status": "updated",
            }

        except Exception as e:
            print(f"Falha na integração com Pipedrive: {str(e)}")
            raise ValueError(f"Erro ao processar Pipedrive: {str(e)}")
    
    def list_leads(self,) -> List[Dict]:
        leads = self.repository.list_all()
        return [lead.to_dict() for lead in leads]
