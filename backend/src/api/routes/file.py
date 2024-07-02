import os

from src.repository.crud.dataset_db import DataSetCRUDRepository
from src.models.schemas.dataset import DatasetResponse
import fastapi
from fastapi import BackgroundTasks

from src.api.dependencies.repository import get_repository
from src.config.settings.const import UPLOAD_FILE_PATH
from src.models.schemas.file import FileInResponse
from src.repository.crud.file import UploadedFileCRUDRepository
from src.utilities.exceptions.database import EntityAlreadyExists

from src.utilities.exceptions.http.exc_400 import (
   http_400_exc_bad_file_name_request,
)

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

    filename=file.filename 
    try:
        new_file = await file_repo.create_uploadfile(file_name=filename)
        save_path = UPLOAD_FILE_PATH
    except EntityAlreadyExists:
        raise await http_400_exc_bad_file_name_request(filename)

    if not os.path.exists(save_path):
        os.mkdir(save_path)
    save_file = os.path.join(save_path, filename)
    contents = await file.read()
    background_tasks.add_task(save_upload_file, contents, save_file)

    return FileInResponse(fileID=new_file.id)

@router.get(
    path="/dataset",
    name="dataset:get-dataset-list",
    response_model=list[DatasetResponse],
    status_code=fastapi.status.HTTP_200_OK,
)
async def get_dataset(
    dataset_repo: DataSetCRUDRepository = fastapi.Depends(get_repository(repo_type=DataSetCRUDRepository)),
) -> list[DatasetResponse]:
    db_datasets=await dataset_repo.get_dataset_list()
    datasets_list: list = list()    

    for db_dataset in db_datasets:
        # print(f"db_dataset:{type(db_dataset.id),type(db_dataset.name),type(db_dataset.created_at),type(db_dataset.updated_at)}")    
        dataset_res=DatasetResponse(
                id=db_dataset.id,
                dataset_name=db_dataset.name,
                created_at=db_dataset.created_at,
                updated_at=db_dataset.updated_at,
            ),
        datasets_list.append(dataset_res)
        # datasets_list.append(db_dataset.name)
    return datasets_list


