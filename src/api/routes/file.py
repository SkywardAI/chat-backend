import os
import random

import fastapi
from fastapi import BackgroundTasks

from src.api.dependencies.repository import get_repository
from src.config.settings.const import UPLOAD_FILE_PATH
from src.models.schemas.file import FileInResponse, FileStatusInResponse
from src.repository.crud.file import UploadedFileCRUDRepository

router = fastapi.APIRouter(prefix="/file", tags=["file"])


async def save_upload_file(contents: bytes, save_file: str):
    with open(save_file, "wb") as f:
        f.write(contents)


@router.post(
    "",
    name="file:upload file",
    response_model=FileInResponse,
    status_code=fastapi.status.HTTP_201_CREATED,
)
async def upload_and_return_id(
    background_tasks: BackgroundTasks,
    file: fastapi.UploadFile = fastapi.File(...),
    file_repo: UploadedFileCRUDRepository = fastapi.Depends(get_repository(repo_type=UploadedFileCRUDRepository)),
):

    new_file = await file_repo.create_uploadfile(file_name=file.filename)
    save_path = UPLOAD_FILE_PATH

    if not os.path.exists(save_path):
        os.mkdir(save_path)
    save_file = os.path.join(save_path, file.filename)
    contents = await file.read()
    background_tasks.add_task(save_upload_file, contents, save_file)

    return FileInResponse(fileID=new_file.id)


@router.get(
    path="/{id}",
    name="file:check upload status",
    response_model=FileStatusInResponse,
    status_code=fastapi.status.HTTP_200_OK,
)
async def check_status(
    id: int,
) -> FileStatusInResponse:

    # TODO check process status of training
    choices = [0, 1, -1]
    # 0 for in process
    # 1 for complete successfully
    # -1 for error
    return FileStatusInResponse(status=1)
