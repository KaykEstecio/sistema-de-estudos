"""Utilitários JWT; existência do usuário e permissões exigem consulta ao banco."""

from datetime import datetime, timezone
import re

import jwt

from app.core.config import JWTSettings

ALGORITHM = "HS256"
ISSUER = "codetrack"
AUDIENCE = "codetrack-api"


class InvalidAccessToken(Exception):
    """Token inválido ou expirado; nunca inclui credenciais no erro."""


def create_access_token(user_id: int, settings: JWTSettings) -> str:
    if type(user_id) is not int or not 0 < user_id <= 2147483647:
        raise ValueError("user_id deve ser um ID PostgreSQL válido.")
    now = int(datetime.now(timezone.utc).timestamp())
    return jwt.encode(
        {"sub": str(user_id), "iat": now,
         "exp": now + settings.jwt_access_token_minutes * 60,
         "iss": ISSUER, "aud": AUDIENCE, "token_type": "access"},
        settings.jwt_secret_key.get_secret_value(), algorithm=ALGORITHM,
    )


def decode_access_token(token: str, settings: JWTSettings) -> int:
    """Retorna o ID validado, sem confirmar existência ou role do usuário."""
    try:
        claims = jwt.decode(
            token, settings.jwt_secret_key.get_secret_value(), algorithms=[ALGORITHM],
            issuer=ISSUER, audience=AUDIENCE,
            options={"require": ["sub", "iat", "exp", "iss", "aud", "token_type"],
                     "strict_aud": True},
        )
        if (claims["token_type"] != "access"
                or not isinstance(claims["sub"], str)
                or re.fullmatch(r"[1-9][0-9]{0,9}", claims["sub"]) is None
                or int(claims["sub"]) > 2147483647
                or type(claims["iat"]) is not int or type(claims["exp"]) is not int
                or claims["exp"] <= claims["iat"]):
            raise InvalidAccessToken("Token inválido ou expirado.")
        return int(claims["sub"])
    except jwt.InvalidTokenError:
        raise InvalidAccessToken("Token inválido ou expirado.") from None
