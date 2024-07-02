from src.models.schemas.base import BaseSchemaModel


class ServiceVersionResponse(BaseSchemaModel):
    llamacpp_version: str | None = None
    milvus_version : str | None = None
    backend_version :str | None = None

