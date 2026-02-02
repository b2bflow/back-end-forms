from flask import Blueprint
from app.controllers.lead_controller import LeadController
from app.services.lead_service import LeadService
from app.repository.lead_repository import LeadRepository

lead_bp = Blueprint("leads", __name__)

repository = LeadRepository()
service = LeadService(repository)
controller = LeadController(service)

lead_bp.post("/api/v1/leads")(controller.create)
lead_bp.get("/api/v1/leads")(controller.list)
lead_bp.put("/api/v1/leads")(controller.update)