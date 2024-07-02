from src.models.schemas.base import BaseSchemaModel


class TrainFileIn(BaseSchemaModel):
    fileID: int | None = None
    dataSet: str | None = None
    modelID: int | None = None
    embedField : str | None = None
    resField : str | None = None
    directLoad: bool = False


class TrainFileInResponse(BaseSchemaModel):
    trainID: int | None = None
    msg : str