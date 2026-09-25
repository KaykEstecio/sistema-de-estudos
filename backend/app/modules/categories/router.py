"""Consulta autenticada de categorias."""

from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, Path, Query
from sqlalchemy.orm import Session
from app.database.connection import get_session
from app.modules.users.dependencies import get_current_user
from app.modules.categories.schemas import CategoryListQuery, CategoryPage, CategoryRead
from app.modules.categories.service import CategoryNotFound, CategoryService

from app.modules.users.dependencies import require_admin
from app.modules.categories.schemas import CategoryCreate, CategoryUpdate

router = APIRouter(prefix="/api/v1/categories", tags=["categories"],
                   dependencies=[Depends(get_current_user)])



@router.post("", response_model=CategoryRead, status_code=201, dependencies=[Depends(require_admin)])
def create_category(data: CategoryCreate, session: Annotated[Session, Depends(get_session)]) -> CategoryRead:
    return CategoryService(session).create(data)


@router.patch("/{id}", response_model=CategoryRead, dependencies=[Depends(require_admin)])
def update_category(id: Annotated[int, Path(ge=1, le=2147483647)], data: CategoryUpdate,
                    session: Annotated[Session, Depends(get_session)]) -> CategoryRead:
    return CategoryService(session).update(id, data)


@router.get("", response_model=CategoryPage)
def list_categories(query: Annotated[CategoryListQuery, Query()],
                    session: Annotated[Session, Depends(get_session)]) -> CategoryPage:
    return CategoryService(session).list_page(query)


@router.get("/{id}", response_model=CategoryRead)
def get_category(id: Annotated[int, Path(ge=1, le=2147483647)],
                 session: Annotated[Session, Depends(get_session)]) -> CategoryRead:
    try:
        return CategoryService(session).get(id)
    except CategoryNotFound:
        raise HTTPException(status_code=404, detail="Categoria não encontrada.") from None
