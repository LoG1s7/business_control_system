from fastapi import HTTPException
from starlette.status import HTTP_400_BAD_REQUEST

from src.utils.auth.invite_token import (
    generate_invite_token,
    send_invitation_email,
    verify_invite_token,
)
from src.utils.auth.jwt_tools import hash_password
from src.models import UserModel
from src.schemas.auth import (
    SignUpCompleteRequest,
    SignUpConfirmRequest,
)
from src.schemas.user import UserRole
from src.utils.service import BaseService
from src.utils.unit_of_work import transaction_mode


class AuthService(BaseService):
    @transaction_mode
    async def check_account_availability(self, account: str) -> bool:
        user = await self.uow.user.get_by_query_one_or_none(email=account)
        return user is None

    @transaction_mode
    async def initiate_registration(self, account: str) -> None:
        if not await self.check_account_availability(account):
            raise HTTPException(
                status_code=HTTP_400_BAD_REQUEST,
                detail='Account already exists',
            )
        invite_token = generate_invite_token(account)
        await send_invitation_email(account, invite_token)

    @transaction_mode
    async def confirm_invitation(self, data: SignUpConfirmRequest) -> bool:
        if not verify_invite_token(data.account, data.invite_token):
            raise HTTPException(
                status_code=HTTP_400_BAD_REQUEST,
                detail='Invalid invite token',
            )
        return True

    @transaction_mode
    async def complete_registration(self, data: SignUpCompleteRequest) -> UserModel:
        if not await self.check_account_availability(data.email):
            raise HTTPException(
                status_code=HTTP_400_BAD_REQUEST,
                detail='Account already exists',
            )

        company = await self.uow.company.add_one_and_get_obj(
            company_name=data.company_name,
            inn=None,
        )

        hashed_pwd = hash_password(data.password)
        user = await self.uow.user.add_one_and_get_obj(
            email=data.email,
            hashed_password=hashed_pwd,
            first_name=data.first_name,
            last_name=data.last_name,
            username=data.username,
            company_id=company.id,
            role=UserRole.ADMIN,
            active=True,
        )
        return user
