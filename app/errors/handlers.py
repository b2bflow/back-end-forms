from flask import jsonify
from mongoengine.errors import NotUniqueError, ValidationError
import logging


def register_error_handlers(app):

    @app.errorhandler(ValueError)
    def handle_value_error(error):
        return jsonify({
            "mensagem": str(error),
            "status": "error"
        }), 400

    @app.errorhandler(ValidationError)
    def handle_validation_error(error):
        return jsonify({
            "mensagem": "Dados inválidos",
            "status": "error"
        }), 400

    @app.errorhandler(NotUniqueError)
    def handle_duplicate_error(error):
        return jsonify({
            "mensagem": "Registro já existe",
            "status": "error"
        }), 409

    @app.errorhandler(Exception)
    def handle_generic_error(error):
        app.logger.exception(error)

        return jsonify({
            "mensagem": "Erro interno no servidor",
            "status": "error"
        }), 500
