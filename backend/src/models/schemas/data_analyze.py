from pydantic import Field
from src.models.schemas.base import BaseSchemaModel


class DataViewResponse(BaseSchemaModel):
    file_path: str = Field(..., title="File path", description="File path")
