"""The module contains base routes for authentication with email invites."""

from fastapi import (
    APIRouter,
    Depends,
    Form,
)
from starlette.status import HTTP_200_OK, HTTP_201_CREATED

from src.api.v1.services import AuthService
from src.schemas.auth import (
    CheckAccountResponse,
    SignUpCompleteRequest,
    SignUpConfirmUserInCompanyRequest,
)
from src.schemas.response import BaseResponse, PayloadResponse
from src.schemas.user import UserResponse, UserSchema
from src.utils.auth.validators import get_current_active_auth_user

router = APIRouter(
    prefix='/auth',
)


@router.get('/check_account/{account}', response_model=CheckAccountResponse)
async def check_account_availability(
    account: str,
    service: AuthService = Depends(AuthService),
):
    is_available = await service.check_account_availability(account)
    return CheckAccountResponse(is_available=is_available)


@router.post('/sign-up/', status_code=HTTP_200_OK)
async def initiate_admin_registration(
    account: str = Form(...),
    service: AuthService = Depends(AuthService),
):
    await service.initiate_admin_registration(account)
    return BaseResponse()


@router.post('/send-invite/{company_id}', status_code=HTTP_200_OK)
async def send_invite_with_role_in_company(
    data: SignUpConfirmUserInCompanyRequest,
    service: AuthService = Depends(AuthService),
    current_user: UserSchema = Depends(get_current_active_auth_user),
):
    """Send invite with role in company."""
    await service.initiate_employee_registration(
        company_id=data.company_id,
        account=data.email,
        role=data.role,
        current_user=current_user,
    )
    return BaseResponse()


@router.post('/sign-up/confirm/', status_code=HTTP_200_OK)
async def confirm_invitation(
    invite_token: str,
    service: AuthService = Depends(AuthService),
):
    payload = await service.confirm_invitation(invite_token)
    return PayloadResponse(payload=payload, message='Registration confirmed')


@router.post('/sign-up/admin/complete/{invite_token}', status_code=HTTP_201_CREATED)
async def complete_company_with_admin_registration(
    invite_token: str,
    data: SignUpCompleteRequest,
    service: AuthService = Depends(AuthService),
):
    payload = await service.confirm_invitation(invite_token)
    user = await service.complete_company_with_admin_registration(data=data, payload=payload)
    return UserResponse(
        payload=user.to_pydantic_schema(),
        message='Registration complete',
    )


@router.post('/sign-up/user/complete/{invite_token}', status_code=HTTP_200_OK)
async def complete_user_in_company_registration(
    invite_token: str,
    service: AuthService = Depends(AuthService),
):
    payload = await service.confirm_invitation(invite_token)
    user = await service.complete_user_in_company_registration(payload)
    return UserResponse(
        payload=user.to_pydantic_schema(),
        message='Registration complete',
    )
