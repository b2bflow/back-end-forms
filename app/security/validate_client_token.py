import os
from functools import wraps
from flask import request, jsonify


def validate_client_token(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        token_client = request.headers.get("X-Client-Token")

        expected_token = os.getenv("CLIENT_TOKEN")

        if not expected_token:
            return jsonify({
                "mensagem": "Configuração de segurança inválida",
                "status": "error"
            }), 500

        if not token_client:
            return jsonify({
                "mensagem": "Token do cliente não informado",
                "status": "error"
            }), 401

        if token_client != expected_token:
            return jsonify({
                "mensagem": "Origem da requisição não autorizada",
                "status": "error"
            }), 403

        return func(*args, **kwargs)

    return wrapper
