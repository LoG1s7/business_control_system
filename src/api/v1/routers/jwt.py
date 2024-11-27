"""The module contains base routes for authentication with jwt tokens."""

from fastapi import (
    APIRouter,
    Depends,
)
from fastapi.security import (
    HTTPBearer,
)
from pydantic import BaseModel

from schemas.user import UserSchema
from src.utils.auth.jwt_tools import (
    create_access_token,
    create_refresh_token,
)
from src.utils.auth.validators import (
    get_current_active_auth_user,
    get_current_auth_user_for_refresh,
    get_current_token_payload,
    validate_auth_user,
)

http_bearer = HTTPBearer(auto_error=False)


class TokenInfo(BaseModel):
    access_token: str
    refresh_token: str | None = None
    token_type: str = 'Bearer'


router = APIRouter(
    prefix='/jwt',
    dependencies=[Depends(http_bearer)],
)


@router.post('/login/', response_model=TokenInfo)
def auth_user_issue_jwt(
    user: UserSchema = Depends(validate_auth_user),
):
    access_token = create_access_token(user)
    refresh_token = create_refresh_token(user)
    return TokenInfo(
        access_token=access_token,
        refresh_token=refresh_token,
    )


@router.post(
    '/refresh/',
    response_model=TokenInfo,
    response_model_exclude_none=True,
)
def auth_refresh_jwt(
    user: UserSchema = Depends(get_current_auth_user_for_refresh),
):
    access_token = create_access_token(user)
    return TokenInfo(
        access_token=access_token,
    )


@router.get('/users/me/')
def auth_user_check_self_info(
    payload: dict = Depends(get_current_token_payload),
    user: UserSchema = Depends(get_current_active_auth_user),
):
    iat = payload.get('iat')
    return {
        'username': user.username,
        'email': user.email,
        'logged_in_at': iat,
    }
