from fastapi import (
    APIRouter,
    Depends,
    Form,
)
from starlette.status import HTTP_200_OK, HTTP_201_CREATED

from src.api.v1.services.auth import AuthService
from src.schemas.auth import (
    CheckAccountResponse,
    SignUpCompleteRequest,
    SignUpConfirmRequest,
)
from src.schemas.response import BaseResponse
from src.schemas.user import UserResponse

router = APIRouter(
    prefix='/auth',
)


@router.get('/check_account/{account}', response_model=CheckAccountResponse)
async def check_account_availability(
    account: str,
    service: AuthService = Depends(AuthService),
):
    account = account.lower()
    is_available = await service.check_account_availability(account)
    return CheckAccountResponse(is_available=is_available)


@router.post('/sign-up/', status_code=HTTP_200_OK)
async def initiate_registration(
    account: str = Form(...),
    service: AuthService = Depends(AuthService),
):
    account = account.lower()
    await service.initiate_registration(account)
    return BaseResponse()


@router.post('/sign-up/confirm/', status_code=HTTP_200_OK)
async def confirm_invitation(
    data: SignUpConfirmRequest,
    service: AuthService = Depends(AuthService),
):
    await service.confirm_invitation(data)
    return BaseResponse()


@router.post('/sign-up-complete/', status_code=HTTP_201_CREATED)
async def complete_registration(
    data: SignUpCompleteRequest,
    service: AuthService = Depends(AuthService),
):
    user = await service.complete_registration(data)
    return UserResponse(payload=user.to_pydantic_schema())
