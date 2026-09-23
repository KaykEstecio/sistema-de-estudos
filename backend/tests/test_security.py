import unicodedata

import pytest

from app.core.security import hash_password, verify_password


def test_hash_uses_random_salt_and_verifies_original_password() -> None:
    password = "frase de senha para teste"
    first = hash_password(password)
    second = hash_password(password)

    assert first.startswith("$argon2id$")
    assert first != second
    assert password not in first
    assert verify_password(password, first)
    assert verify_password(password, second)
    assert not verify_password("senha incorreta", first)


def test_password_whitespace_and_case_are_preserved() -> None:
    password = "  Senha Com Espaços  "
    hashed = hash_password(password)

    assert verify_password(password, hashed)
    assert not verify_password(password.strip(), hashed)
    assert not verify_password(password.lower(), hashed)


def test_unicode_is_not_normalized() -> None:
    password = "Café 🔐"
    hashed = hash_password(password)

    assert verify_password(password, hashed)
    assert not verify_password(unicodedata.normalize("NFD", password), hashed)


def test_long_password_is_not_truncated() -> None:
    prefix = "a" * 100
    hashed = hash_password(prefix + "X")

    assert verify_password(prefix + "X", hashed)
    assert not verify_password(prefix + "Y", hashed)


@pytest.mark.parametrize("hashed", ["", "not-an-argon2-hash", "$argon2id$v=19$invalid"])
def test_invalid_stored_hash_does_not_authenticate(hashed: str) -> None:
    assert not verify_password("senha de teste", hashed)
