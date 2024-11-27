import bcrypt
from fastapi import Depends, Form, HTTPException
from fastapi.security import OAuth2PasswordBearer
from jwt import InvalidTokenError
from pydantic import UUID4
from starlette import status

from src.api.v1.services.user import UserService
from src.schemas.user import UserRole, UserSchema
from src.utils.auth.jwt_tools import ACCESS_TOKEN_TYPE, REFRESH_TOKEN_TYPE, TOKEN_TYPE_FIELD, decode_jwt

oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl='/api/v1/jwt/login/',
)


async def get_user_service() -> UserService:
    return UserService()


def get_current_token_payload(
    token: str = Depends(oauth2_scheme),
) -> dict:
    try:
        payload = decode_jwt(
            token=token,
        )
    except InvalidTokenError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f'invalid token error: {e}',
        )
    return payload


def validate_token_type(
    payload: dict,
    token_type: str,
) -> bool:
    current_token_type = payload.get(TOKEN_TYPE_FIELD)
    if current_token_type == token_type:
        return True
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail=f'invalid token type {current_token_type!r} expected {token_type!r}',
    )


async def get_user_by_token_sub(
    payload: dict,
    service: UserService = Depends(get_user_service),
) -> UserSchema:
    username: str | None = payload.get('sub')
    user_model = await service.get_user_by_username(username=username)
    if user := user_model:
        return user
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail='token invalid (user not found)',
    )


def get_auth_user_from_token_of_type(token_type: str):
    async def get_auth_user_from_token(
        payload: dict = Depends(get_current_token_payload),
        service: UserService = Depends(get_user_service),
    ) -> UserSchema:
        validate_token_type(payload, token_type)
        return await get_user_by_token_sub(payload, service)

    return get_auth_user_from_token


get_current_auth_user = get_auth_user_from_token_of_type(ACCESS_TOKEN_TYPE)
get_current_auth_user_for_refresh = get_auth_user_from_token_of_type(REFRESH_TOKEN_TYPE)


def get_current_active_auth_user(
    user: UserSchema = Depends(get_current_auth_user),
):
    if user.active:
        return user
    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail='inactive user',
    )


async def validate_auth_user(
    username: str = Form(...),
    password: str = Form(...),
    service: UserService = Depends(get_user_service),
):
    username = username.lower()
    unauthed_exc = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail='invalid username or password',
    )

    if not (user := await service.get_user_by_username(username)):
        raise unauthed_exc

    if not validate_password(
        password=password,
        hashed_password=user.hashed_password,
    ):
        raise unauthed_exc

    if not user.active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail='user inactive',
        )

    return user


def validate_password(
    password: str,
    hashed_password: bytes,
) -> bool:
    return bcrypt.checkpw(
        password=password.encode(),
        hashed_password=hashed_password,
    )


def check_user_is_admin(user: UserSchema | None) -> None:
    if not user.role == UserRole.ADMIN:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='Allowed only for admin')


def check_company_is_yours(
        user: UserSchema | None,
        company_id: UUID4,
) -> None:
    if user.company_id != company_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail='Allowed only for your company',
        )
