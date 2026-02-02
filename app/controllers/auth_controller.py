from flask import request, jsonify

from app.interfaces.services.auth_service_interface import AuthServiceInterface


class AuthController:
    def __init__(self, service: AuthServiceInterface):
        self.service = service
        pass

    def remove_token(self):
        data = request.json
        result = self.service.remove_token(data)
        return jsonify(result), 200
    
    def verify_token(self):
        data = request.json
        result = self.service.verify_token(data)
        return jsonify(result), 200