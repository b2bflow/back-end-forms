from functools import wraps
from flask import request
from jwt import ExpiredSignatureError, InvalidTokenError
from app.security.session_token import SessionTokenService


def validate_lead_session(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        token = request.headers.get("X-Session-Token")

        # Se não existe token, deixa passar (primeiro cadastro)
        if not token:
            return func(*args, **kwargs)

        try:
            # Se o token for válido e não expirou,
            # significa que o lead já tem um agendamento ativo
            SessionTokenService.validate(token)
            raise ValueError("Lead já possui um agendamento ativo")

        except ExpiredSignatureError:
            # Token expirado → pode cadastrar novamente
            return func(*args, **kwargs)

        except InvalidTokenError:
            # Token inválido → ignora e deixa seguir
            return func(*args, **kwargs)

    return wrapper
