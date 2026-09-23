from datetime import datetime, timezone

import pytest
from pydantic import ValidationError

from app.modules.users.models import User, UserRole
from app.modules.users.schemas import UserCreate, UserRead


def test_create_normalizes_identity_without_changing_password() -> None:
    password = "  Senha Com Espaços  "
    data = UserCreate(name="  Ana Silva  ", email="  ANA@EXAMPLE.COM  ", password=password)
    assert data.name == "Ana Silva"
    assert data.email == "ana@example.com"
    assert data.password.get_secret_value() == password
    assert "password" not in data.model_dump()
    assert password not in repr(data)


@pytest.mark.parametrize("changes", [
    {"name": "   "}, {"name": "a" * 121}, {"email": "invalid"},
    {"password": ""}, {"role": "ADMIN"}, {"password_hash": "injected"},
    {"onboarding_completed": True},
])
def test_create_rejects_invalid_or_privileged_fields(changes: dict[str, object]) -> None:
    payload = {"name": "Ana", "email": "ana@example.com", "password": "fixture password"}
    payload.update(changes)
    with pytest.raises(ValidationError):
        UserCreate.model_validate(payload)


def test_read_excludes_credentials_from_orm() -> None:
    now = datetime.now(timezone.utc)
    user = User(id=1, name="Ana", email="ana@example.com", password_hash="private-hash",
                role=UserRole.STUDENT, onboarding_completed=False, created_at=now, updated_at=now)
    result = UserRead.model_validate(user).model_dump(mode="json")
    assert set(result) == {"id", "name", "email", "role", "onboarding_completed", "created_at", "updated_at"}
    assert result["role"] == "STUDENT"
    assert "private-hash" not in str(result)


@pytest.mark.parametrize("length,valid", [(14, False), (15, True), (128, True), (129, False)])
def test_password_length_boundaries(length: int, valid: bool) -> None:
    payload = {"name": "Ana", "email": "ana@example.com", "password": "á" * length}
    if valid:
        assert len(UserCreate.model_validate(payload).password.get_secret_value()) == length
    else:
        with pytest.raises(ValidationError):
            UserCreate.model_validate(payload)
