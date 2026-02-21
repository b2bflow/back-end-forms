from app.interfaces.services.lead_service_interface import LeadServiceInterface
from app.interfaces.repositories.lead_repository_interface import LeadRepositoryInterface
from app.integrations.pipedrive_crm_integration import PipedriveClient
from app.models.tables.lead_model import Lead
from typing import Dict, List
from app.utils.logging_config import logger
from app.security.session_token import SessionTokenService


class LeadService(LeadServiceInterface):

    def __init__(self, repository: LeadRepositoryInterface):
        self.repository = repository
        self.pipedrive_client = PipedriveClient()

    def create_lead(self, data: Dict) -> Dict:
        logger.info(f"[LEAD_SERVICE] Creating lead with data: {data}")

        lead = self.repository.find_by_phone(data["phone"])

        if lead is None:
            lead = self.repository.find_by_email(data["email"])

        if lead is not None:
            if lead.email == data["email"] or lead.phone == data["phone"]:

                lead.confirmation_sent = False
                lead.recovery_sent = False
                lead.reminder_sent = False

                lead = self.repository.update_by_phone(str(lead.phone), data=data)

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
            logger.error(f"[LEAD_SERVICE] Falha na criação do lead: {str(e)}")
            raise ValueError(str(e))

    def update_lead(self, data: Dict) -> Dict:
        logger.info(f"[LEAD_SERVICE] Atualizando lead com dados: {data}")
        lead = self.repository.find_by_phone(data["phone"])

        if not lead:
            raise ValueError("Lead nao encontrado")

        updated_lead = self.repository.update_by_phone(
            lead_phone=str(lead.phone),
            data=data
        )

        if updated_lead.type_lead == 'venda':
            return self.update_sales_lead(updated_lead)

        if updated_lead.type_lead == 'consultoria':
            return self.update_followup_lead(updated_lead)
    
    def list_leads(self,) -> List[Dict]:
        leads = self.repository.list_all()
        return [lead.to_dict() for lead in leads]
    
    def update_sales_lead(self, lead: Lead) -> Dict:
        try:
            id_faturamento = self.pipedrive_client._get_pipedrive_option_id("faturamento", lead.sales_data.invoicing)
            id_funcionarios = self.pipedrive_client._get_pipedrive_option_id("funcionarios", lead.sales_data.collaborators)

            self.pipedrive_client.update_organization_details(
                org_id=lead.id_organization_pipedrive,
                segmento=lead.sales_data.business_tracking,
                faturamento=id_faturamento,
                funcionarios=id_funcionarios,
                produto=lead.sales_data.product_of_interest,
            )

            deal_title = lead.business_name
            deal_id = lead.id_deal_pipedrive

            if deal_id:
                self.pipedrive_client.update_deal_stage(
                    deal_id=deal_id,
                    new_stage_id=2,
                )
            else:
                logger.warning(f"[LEAD_SERVICE] Aviso: Deal '{deal_title}' não encontrado para atualização.")

            return {
                "message": "Lead atualizado com sucesso",
                "token": lead.leadtoken,
                "status": "updated",
            }

        except Exception as e:
            logger.error(f"[LEAD_SERVICE] Falha na integração com Pipedrive update_sales_lead: {str(e)}")
            raise ValueError(f"Erro ao processar Pipedrive: {str(e)}")
        
    def update_followup_lead(self, lead: Lead) -> Dict:

        desafios_selecionados = lead.followup_data.challenge
        ids_desafios = []
        
        if isinstance(desafios_selecionados, list):
            for texto_desafio in desafios_selecionados:
                id_op = self.pipedrive_client._get_pipedrive_option_id("desafio", texto_desafio)
                if id_op:
                    ids_desafios.append(str(id_op))
            
            valor_desafio_final = ",".join(ids_desafios)
        else:
            valor_desafio_final = self.pipedrive_client._get_pipedrive_option_id("desafio", desafios_selecionados)

        id_momento = self.pipedrive_client._get_pipedrive_option_id("momento", lead.followup_data.customer_stage)
        id_capacidade_investimento = self.pipedrive_client._get_pipedrive_option_id("investimento", lead.followup_data.investment_capacity)

        try:
            logger.info(f"[LEAD_SERVICE] Atualizando detalhes do lead: {lead.name}")
            self.pipedrive_client.update_organization_details(
                org_id=lead.id_organization_pipedrive,
                desafio=valor_desafio_final,
                momento=id_momento,
                capacidade_investimento=id_capacidade_investimento,
            )

            deal_title = lead.business_name
            deal_id = lead.id_deal_pipedrive

            if deal_id:
                self.pipedrive_client.update_deal_stage(
                    deal_id=deal_id,
                    new_stage_id=2,
                )
            else:
                logger.warning(f"[LEAD_SERVICE] Aviso: Deal '{deal_title}' não encontrado para atualização.")

            return {
                "message": "Lead atualizado com sucesso",
                "token": lead.leadtoken,
                "status": "updated",
            }

        except Exception as e:
            logger.error(f"[LEAD_SERVICE] Falha na integração com Pipedrive update_followup_lead: {str(e)}")
            raise ValueError(f"Erro ao processar Pipedrive: {str(e)}")