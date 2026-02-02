from flask import Blueprint
from app.controllers.appointment_controller import AppointmentController
from app.services.appointment_service import AppointmentService
from app.repository.lead_repository import LeadRepository

appointment_bp = Blueprint("appointment", __name__)

repository = LeadRepository()
service = AppointmentService(repository)
controller = AppointmentController(service)

appointment_bp.post("/api/v1/appointment")(controller.create)
appointment_bp.get("/api/v1/appointment")(controller.list)