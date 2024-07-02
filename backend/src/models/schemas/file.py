from src.models.schemas.base import BaseSchemaModel


class UploadedFile(BaseSchemaModel):
    name: str


class FileInResponse(BaseSchemaModel):
    fileID: int
