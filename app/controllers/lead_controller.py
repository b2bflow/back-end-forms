from flask import request, jsonify
from app.interfaces.services.lead_service_interface import LeadServiceInterface
from app.security.lead_session_guard import validate_lead_session
from app.security.validate_client_token import validate_client_token

class LeadController:

    def __init__(self, service: LeadServiceInterface):
        self.service = service

    @validate_lead_session
    @validate_client_token
    def create(self):
        data = request.json
        result = self.service.create_lead(data)
        return jsonify(result), 201

    def list(self):
        result = self.service.list_leads()
        return jsonify(result), 200
    
    @validate_lead_session
    @validate_client_token
    def update(self):
        data = request.json
        result = self.service.update_lead(data)
        return jsonify(result), 200
