import typing

import fastapi
from sqlalchemy.ext.asyncio import AsyncSession as SQLAlchemyAsyncSession

from src.api.dependencies.session import get_async_session
from src.repository.crud.base import BaseCRUDRepository
from src.repository.rag.base import BaseRAGRepository


def get_repository(
    repo_type: typing.Type[BaseCRUDRepository],
) -> typing.Callable[[SQLAlchemyAsyncSession], BaseCRUDRepository]:
    def _get_repo(
        async_session: SQLAlchemyAsyncSession = fastapi.Depends(get_async_session),
    ) -> BaseCRUDRepository:
        return repo_type(async_session=async_session)

    return _get_repo


def get_rag_repository(
    repo_type: typing.Type[BaseRAGRepository],
) -> typing.Callable[[SQLAlchemyAsyncSession], BaseRAGRepository]:
    def _get_repo(
        async_session: SQLAlchemyAsyncSession = fastapi.Depends(get_async_session),
    ) -> BaseRAGRepository:
        return repo_type(async_session=async_session)

    return _get_repo
