import pydantic
from sqlalchemy.ext.asyncio import (
    AsyncEngine as SQLAlchemyAsyncEngine,
    AsyncSession as SQLAlchemyAsyncSession,
    create_async_engine as create_sqlalchemy_async_engine,
)
from sqlalchemy.pool import Pool as SQLAlchemyPool
from sqlalchemy.pool import NullPool
from sqlalchemy import create_engine
from src.config.manager import settings


class AsyncDatabase:
    def __init__(self):
        self.postgres_uri: pydantic.PostgresDsn = pydantic.PostgresDsn(
            url=f"{settings.POSTGRES_SCHEMA}://{settings.POSTGRES_USERNAME}:{settings.POSTGRES_PASSWORD}@{settings.POSTGRES_HOST}:{settings.POSTGRES_PORT}/{settings.POSTGRES_DB}",
        )
        self.async_engine: SQLAlchemyAsyncEngine = create_sqlalchemy_async_engine(
            url=self.set_async_db_uri,
            echo=settings.IS_DB_ECHO_LOG,
            # pool_size=settings.DB_POOL_SIZE,
            # max_overflow=settings.DB_POOL_OVERFLOW,
            pool_recycle=3600,  # Periodically recycle connections (optional)
            pool_pre_ping=True,  # Check the connection status before using it
            # https://github.com/MagicStack/asyncpg/issues/863
            poolclass=NullPool,
        )
        self.sync_engine = create_engine(
            f"{settings.POSTGRES_SCHEMA}://{settings.POSTGRES_USERNAME}:{settings.POSTGRES_PASSWORD}@{settings.POSTGRES_HOST}:{settings.POSTGRES_PORT}/{settings.POSTGRES_DB}"
        )
        self.async_session: SQLAlchemyAsyncSession = SQLAlchemyAsyncSession(bind=self.async_engine)
        self.pool: SQLAlchemyPool = self.async_engine.pool

    @property
    def set_async_db_uri(self) -> str | pydantic.PostgresDsn:
        """
        Set the synchronous database driver into asynchronous version by utilizing AsyncPG:

            `postgresql://` => `postgresql+asyncpg://`
        """
        return (
            self.postgres_uri.unicode_string().replace("postgresql://", "postgresql+asyncpg://")
            if self.postgres_uri
            else self.postgres_uri
        )


async_db: AsyncDatabase = AsyncDatabase()
