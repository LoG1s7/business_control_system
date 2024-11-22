from fastapi import HTTPException
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.status import HTTP_401_UNAUTHORIZED

from src.auth.utils import decode_jwt


class AuthMiddleware(BaseHTTPMiddleware):
    async def dispatch(
        self,
        request: Request,
        call_next,
    ):
        public_paths = [
            '/docs',
            '/openapi.json',
            '/redoc',
            '/favicon.ico',
            '/api/v1/user',
            '/api/v1/auth/check_account',
            '/api/v1/auth/sign-up',
            '/api/v1/auth/sign-up/confirm',
            '/api/v1/auth/sign-up-complete',
            '/api/v1/jwt/login',
            '/api/healthz/',
        ]

        request_path = request.url.path
        if any(request_path.startswith(path) for path in public_paths):
            return await call_next(request)

        if 'Bearer' not in request.headers:
            raise HTTPException(
                status_code=HTTP_401_UNAUTHORIZED,
                detail='Authorization header missing',
            )

        auth_header = request.headers.get('Bearer')
        token = auth_header.split(' ')[1]
        try:
            payload = decode_jwt(token)
            request.state.user = payload
        except Exception:
            raise HTTPException(status_code=HTTP_401_UNAUTHORIZED, detail='Invalid token')
        return await call_next(request)
