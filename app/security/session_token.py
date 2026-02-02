import os
import jwt
from datetime import datetime, timedelta


class SessionTokenService:

    @staticmethod
    def generate(lead_id: str, expires_at: datetime) -> str:
        secret = os.getenv("JWT_SECRET_KEY")

        if not secret or not isinstance(secret, str):
            raise RuntimeError("JWT_SECRET_KEY não configurada corretamente")

        payload = {
            "sub": lead_id,
            "exp": expires_at,
            "iat": datetime.utcnow(),
            "scope": "lead_session",
        }

        return jwt.encode(payload, secret, algorithm="HS256")

    @staticmethod
    def validate(token: str) -> dict:
        secret = os.getenv("JWT_SECRET_KEY")

        if not secret or not isinstance(secret, str):
            raise RuntimeError("JWT_SECRET_KEY não configurada corretamente")

        return jwt.decode(token, secret, algorithms=["HS256"])
