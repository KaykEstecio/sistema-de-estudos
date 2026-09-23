"""Hash de senhas; não autentica usuários nem realiza persistência."""

from argon2 import PasswordHasher
from argon2.exceptions import InvalidHashError, VerificationError
from argon2.profiles import RFC_9106_LOW_MEMORY

# Argon2id: 64 MiB, 3 iterações, 4 threads, salt de 16 bytes e hash de 32 bytes.
_password_hasher = PasswordHasher.from_parameters(RFC_9106_LOW_MEMORY)


def hash_password(password: str) -> str:
    """Gera hash com salt aleatório, preservando todos os caracteres da senha."""
    return _password_hasher.hash(password)


def verify_password(password: str, password_hash: str) -> bool:
    """Confere a senha contra um hash obtido da persistência confiável."""
    try:
        return _password_hasher.verify(password_hash, password)
    except (VerificationError, InvalidHashError):
        return False
