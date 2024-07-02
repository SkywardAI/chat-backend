import fastapi

from src.api.routes.account import router as account_router
from src.api.routes.ai_model import router as ai_model_router
from src.api.routes.authentication import router as auth_router
from src.api.routes.chat import router as chat_router
from src.api.routes.file import router as file_router
from src.api.routes.train import router as train_router
from src.api.routes.version import router as version_router

router = fastapi.APIRouter()

router.include_router(router=account_router)
router.include_router(router=auth_router)
router.include_router(router=chat_router)
router.include_router(router=ai_model_router)
router.include_router(router=train_router)
router.include_router(router=file_router)
router.include_router(router=version_router)