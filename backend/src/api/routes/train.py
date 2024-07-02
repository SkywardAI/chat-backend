from src.models.schemas.dataset import DatasetCreate
from src.repository.crud.dataset_db import DataSetCRUDRepository
import fastapi
import threading
from src.api.dependencies.repository import get_rag_repository, get_repository
from src.models.schemas.train import TrainFileIn, TrainFileInResponse
from src.repository.crud.ai_model import AiModelCRUDRepository
from src.repository.crud.file import UploadedFileCRUDRepository
from src.repository.rag.chat import RAGChatModelRepository

router = fastapi.APIRouter(prefix="/train", tags=["Save"])


@router.post(
    "",
    name="train:Save file or dataset to DB",
    response_model=TrainFileInResponse,
    status_code=fastapi.status.HTTP_201_CREATED,
)
async def save(
    train_in_msg: TrainFileIn,
    aimodel_repo: AiModelCRUDRepository = fastapi.Depends(get_repository(repo_type=AiModelCRUDRepository)),
    file_repo: UploadedFileCRUDRepository = fastapi.Depends(get_repository(repo_type=UploadedFileCRUDRepository)),
    rag_chat_repo: RAGChatModelRepository = fastapi.Depends(get_rag_repository(repo_type=RAGChatModelRepository)),
    dataset_repo: DataSetCRUDRepository = fastapi.Depends(get_rag_repository(repo_type=DataSetCRUDRepository)),
) -> TrainFileInResponse:
    # 1, either fileID or dataset should be shown in input
    # 2, validate fileID or dataset
    # 3, use file and or dataset perform the training logic (csv id done)

    if  train_in_msg.modelID is not None and train_in_msg.fileID is not None:
        # if contains file ID and modelID,  then load file
        ai_model = await aimodel_repo.read_aimodel_by_id(id=train_in_msg.modelID)
        file_csv = await file_repo.read_uploadedfiles_by_id(id=train_in_msg.fileID)
        await rag_chat_repo.load_csv_file(file_name=file_csv.name, model_name=ai_model.name)
    else:
        # Else, load dataset
        db_dataset=await dataset_repo.get_dataset_by_name(train_in_msg.dataSet)
        if not db_dataset:
            dataload_thread = threading.Thread(target=rag_chat_repo.load_data_set,args=(train_in_msg,) )
            dataload_thread.daemon = True
            dataload_thread.start()
            await dataset_repo.create_dataset(DatasetCreate(dataset_name=train_in_msg.dataSet,des=train_in_msg.dataSet)) 

    return TrainFileInResponse(
        msg="successful",
    )
