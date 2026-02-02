from flask import request, jsonify
from app.interfaces.services.appointment_service_interface import AppointmentServiceInterface
from app.security.lead_session_guard import validate_lead_session
from app.security.validate_client_token import validate_client_token


class AppointmentController:

    def __init__(self, service: AppointmentServiceInterface):
        self.service = service

    @validate_lead_session
    @validate_client_token
    def create(self):
        data = request.json
        result = self.service.create_appointment(data)
        return jsonify(result), 201

    def list(self):
        result = self.service.list_busy_slots()
        return jsonify(result), 200
