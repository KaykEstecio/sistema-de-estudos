"""Contrato JWT com chaves efêmeras, sem credenciais locais."""

from datetime import datetime, timezone
import secrets

import jwt
import pytest
from pydantic import ValidationError

from app.core.config import JWTSettings
from app.core.tokens import create_access_token, decode_access_token, InvalidAccessToken


@pytest.fixture
def settings(monkeypatch):
    monkeypatch.delenv("JWT_SECRET_KEY", raising=False)
    monkeypatch.delenv("JWT_ACCESS_TOKEN_MINUTES", raising=False)
    return JWTSettings(_env_file=None, jwt_secret_key=secrets.token_urlsafe(32))


def payload():
    now = int(datetime.now(timezone.utc).timestamp())
    return {"sub": "1", "iat": now - 10, "exp": now + 60,
            "iss": "codetrack", "aud": "codetrack-api", "token_type": "access"}


def test_round_trip_and_lifetime(settings):
    token = create_access_token(123, settings)
    assert decode_access_token(token, settings) == 123
    claims = jwt.decode(token, settings.jwt_secret_key.get_secret_value(),
                        algorithms=["HS256"], audience="codetrack-api", issuer="codetrack")
    assert claims["exp"] - claims["iat"] == 1800
    assert set(claims) == {"sub", "iat", "exp", "iss", "aud", "token_type"}
    custom = JWTSettings(_env_file=None, jwt_secret_key=settings.jwt_secret_key, jwt_access_token_minutes=1)
    token = create_access_token(1, custom)
    claims = jwt.decode(token, custom.jwt_secret_key.get_secret_value(), algorithms=["HS256"], audience="codetrack-api")
    assert claims["exp"] - claims["iat"] == 60


@pytest.mark.parametrize("claim", ["sub", "iat", "exp", "iss", "aud", "token_type"])
def test_missing_claim(settings, claim):
    claims = payload()
    del claims[claim]
    token = jwt.encode(claims, settings.jwt_secret_key.get_secret_value(), algorithm="HS256")
    with pytest.raises(InvalidAccessToken):
        decode_access_token(token, settings)


@pytest.mark.parametrize("changes", [
    {"sub": 1}, {"sub": "0"}, {"sub": "-1"}, {"sub": "01"}, {"sub": "2147483648"},
    {"sub": "abc"}, {"iss": "other"}, {"aud": "other"}, {"aud": ["codetrack-api"]},
    {"token_type": "refresh"}, {"exp": 1}, {"exp": "invalid"}, {"iat": True},
    {"iat": "1"}, {"iat": 9999999999}, {"exp": 9999999999, "iat": 9999999999},
])
def test_invalid_claim(settings, changes):
    claims = {**payload(), **changes}
    token = jwt.encode(claims, settings.jwt_secret_key.get_secret_value(), algorithm="HS256")
    with pytest.raises(InvalidAccessToken):
        decode_access_token(token, settings)


def test_signature_algorithm_and_malformed_token(settings):
    key = settings.jwt_secret_key.get_secret_value()
    tokens = [jwt.encode(payload(), secrets.token_urlsafe(32), algorithm="HS256"),
              jwt.encode(payload(), key * 2, algorithm="HS384"),
              jwt.encode(payload(), None, algorithm="none"), "invalid", ""]
    for token in tokens:
        with pytest.raises(InvalidAccessToken) as error:
            decode_access_token(token, settings)
        assert str(error.value) == "Token inválido ou expirado."


@pytest.mark.parametrize("value", [0, -1, True, "1", 2147483648])
def test_invalid_user_id(settings, value):
    with pytest.raises(ValueError):
        create_access_token(value, settings)


@pytest.mark.parametrize("secret", [None, "", "short", " " * 32])
def test_missing_or_short_secret(settings, secret):
    kwargs = {} if secret is None else {"jwt_secret_key": secret}
    with pytest.raises(ValidationError):
        JWTSettings(_env_file=None, **kwargs)


@pytest.mark.parametrize("minutes", [0, -1, 121, "invalid"])
def test_invalid_lifetime(settings, minutes):
    with pytest.raises(ValidationError):
        JWTSettings(_env_file=None, jwt_secret_key=settings.jwt_secret_key, jwt_access_token_minutes=minutes)


def test_secret_hidden(settings):
    assert settings.jwt_secret_key.get_secret_value() not in repr(settings)
