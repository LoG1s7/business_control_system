from datetime import UTC, datetime, timedelta

import bcrypt
import jwt

from schemas.user import UserSchema
from src.config import settings

TOKEN_TYPE_FIELD = 'type'
ACCESS_TOKEN_TYPE = 'access'
REFRESH_TOKEN_TYPE = 'refresh'


def create_jwt(
    token_type: str,
    token_data: dict,
    expire_minutes: int = settings.auth_jwt.access_token_expire_minutes,
    expire_timedelta: timedelta | None = None,
) -> str:
    jwt_payload = {TOKEN_TYPE_FIELD: token_type}
    jwt_payload.update(token_data)
    return encode_jwt(
        payload=jwt_payload,
        expire_minutes=expire_minutes,
        expire_timedelta=expire_timedelta,
    )


def create_access_token(user: UserSchema) -> str:
    jwt_payload = {
        'sub': user.username,
        'id': str(user.id),
        'email': user.email,
    }
    return create_jwt(
        token_type=ACCESS_TOKEN_TYPE,
        token_data=jwt_payload,
        expire_minutes=settings.auth_jwt.access_token_expire_minutes,
    )


def create_refresh_token(user: UserSchema) -> str:
    jwt_payload = {
        'sub': user.username,
        'id': str(user.id),
    }
    return create_jwt(
        token_type=REFRESH_TOKEN_TYPE,
        token_data=jwt_payload,
        expire_timedelta=timedelta(days=settings.auth_jwt.refresh_token_expire_days),
    )


def encode_jwt(
    payload: dict,
    private_key: str = settings.auth_jwt.private_key_path.read_text(),
    algorithm: str = settings.auth_jwt.algorithm,
    expire_minutes: int = settings.auth_jwt.access_token_expire_minutes,
    expire_timedelta: timedelta | None = None,
) -> str:
    to_encode = payload.copy()
    now = datetime.now(tz=UTC)
    expire = now + expire_timedelta if expire_timedelta else now + timedelta(minutes=expire_minutes)
    to_encode.update(
        exp=expire,
        iat=now,
    )
    encoded = jwt.encode(
        to_encode,
        private_key,
        algorithm=algorithm,
    )
    return encoded


def decode_jwt(
    token: str | bytes,
    public_key: str = settings.auth_jwt.public_key_path.read_text(),
    algorithm: str = settings.auth_jwt.algorithm,
) -> dict:
    decoded = jwt.decode(
        token,
        public_key,
        algorithms=[algorithm],
    )
    return decoded


def hash_password(
    password: str,
) -> bytes:
    salt = bcrypt.gensalt()
    pwd_bytes: bytes = password.encode()
    return bcrypt.hashpw(pwd_bytes, salt)
