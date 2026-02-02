from flask import Blueprint

from app.controllers.auth_controller import AuthController
from app.repository.lead_repository import LeadRepository
from app.services.auth_serivce import AuthService


auth_bp = Blueprint("auth", __name__)

repository = LeadRepository()
service = AuthService(repository)
controller = AuthController(service)

auth_bp.post("/api/v1/auth")(controller.verify_token)
