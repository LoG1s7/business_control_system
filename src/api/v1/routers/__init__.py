__all__ = [
    'v1_auth_router',
    'v1_company_router',
    'v1_jwt_router',
    'v1_position_router',
    'v1_subdivision_router',
    'v1_user_router',
]

from src.api.v1.routers.auth import router as v1_auth_router
from src.api.v1.routers.company import router as v1_company_router
from src.api.v1.routers.jwt import router as v1_jwt_router
from src.api.v1.routers.position import router as v1_position_router
from src.api.v1.routers.subdivision import router as v1_subdivision_router
from src.api.v1.routers.user import router as v1_user_router
