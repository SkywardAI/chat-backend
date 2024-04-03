import fastapi

from src.api.dependencies.repository import get_rag_repository, get_repository
from src.models.schemas.chat import ChatHistory, ChatInMessage, ChatInResponse, Session
from src.repository.crud.chat import ChatHistoryCRUDRepository, SessionCRUDRepository
from src.repository.rag.chat import RAGChatModelRepository
from src.securities.authorizations.jwt import jwt_generator
from src.utilities.exceptions.database import EntityDoesNotExist

router = fastapi.APIRouter(prefix="/chat", tags=["chatbot"])


@router.post(
    "",
    name="chat:chatbot",
    response_model=ChatInResponse,
    status_code=fastapi.status.HTTP_201_CREATED,
)
async def chat(
    chat_in_msg: ChatInMessage,
    session_repo: SessionCRUDRepository = fastapi.Depends(get_repository(repo_type=SessionCRUDRepository)),
    chat_repo: ChatHistoryCRUDRepository = fastapi.Depends(get_repository(repo_type=ChatHistoryCRUDRepository)),
    rag_chat_repo: RAGChatModelRepository = fastapi.Depends(get_rag_repository(repo_type=RAGChatModelRepository)),
) -> ChatInResponse:
    # if not chat_in_msg.accountID:
    #     chat_in_msg.accountID = 0
    if not hasattr(chat_in_msg, "sessionId") or not chat_in_msg.sessionId:
        new_session = await session_repo.create_session(
            account_id=chat_in_msg.accountID, name=chat_in_msg.message[:20]
        )
        session_id = new_session.id
    else:
        # TODO need verify if sesson exist
        # create_session = await session_repo.read_create_sessions_by_id(id=chat_in_msg.sessionId, account_id=chat_in_msg.accountID, name=chat_in_msg.message[:20])
        session_id = chat_in_msg.sessionId
    await chat_repo.create_chat_history(session_id=session_id, is_bot_msg=False, message=chat_in_msg.message)
    response_msg = await rag_chat_repo.get_response(session_id=session_id, input_msg=chat_in_msg.message)
    await chat_repo.create_chat_history(session_id=session_id, is_bot_msg=True, message=response_msg)
    return ChatInResponse(
        sessionId=session_id,
        message=response_msg,
    )


@router.get(
    path="/{id}",
    name="chat:get-session-by-account-id",
    response_model=list[Session],
    status_code=fastapi.status.HTTP_200_OK,
)
async def get_session(
    id: int,
    session_repo: SessionCRUDRepository = fastapi.Depends(get_repository(repo_type=SessionCRUDRepository)),
) -> list[Session]:
    sessions = await session_repo.read_sessions_by_account_id(id=id)
    sessions_list: list = list()
    for session in sessions:
        print(session.name)
        try:
            res_session = Session(
                id=session.id,
                name=session.name,
                created_at=session.created_at,
            )
            sessions_list.append(res_session)
        except Exception as e:
            print(e)

    return sessions_list


@router.get(
    path="",
    name="chat:get-all-sessions",
    response_model=list[Session],
    status_code=fastapi.status.HTTP_200_OK,
)
async def get_all_sessions(
    session_repo: SessionCRUDRepository = fastapi.Depends(get_repository(repo_type=SessionCRUDRepository)),
) -> list[Session]:
    sessions = await session_repo.read_sessions()
    sessions_list: list = list()

    for session in sessions:
        res_session = Session(
            id=session.id,
            name=session.name,
            created_at=session.created_at,
        )
        sessions_list.append(res_session)

    return sessions_list


@router.get(
    path="/history/{id}",
    name="chat:get-chat-history-by-account-id",
    response_model=list[ChatHistory],
    status_code=fastapi.status.HTTP_200_OK,
)
async def get_chathistory(
    id: int,
    chat_repo: ChatHistoryCRUDRepository = fastapi.Depends(get_repository(repo_type=ChatHistoryCRUDRepository)),
) -> list[ChatHistory]:
    chats = await chat_repo.read_chat_history_by_session_id(id=id)
    chats_list: list = list()
    for chat in chats:
        res_session = ChatHistory(
            id=chat.id,
            type="out" if chat.is_bot_msg else "in",
            message=chat.message,
        )
        chats_list.append(res_session)

    return chats_list
