from fastapi import HTTPException
from pydantic import UUID4
from starlette.status import HTTP_400_BAD_REQUEST, HTTP_403_FORBIDDEN

from src.models import UserModel
from src.schemas.auth import (
    SignUpCompleteRequest,
)
from src.schemas.user import UserRole, UserSchema
from src.utils.auth.invite_token import (
    generate_admin_invite_token,
    generate_employee_invite_token,
    send_invitation_email,
    verify_invite_token,
)
from src.utils.auth.jwt_tools import hash_password
from src.utils.auth.validators import check_company_is_yours, check_user_is_admin
from src.utils.service import BaseService
from src.utils.unit_of_work import transaction_mode


class AuthService(BaseService):
    @transaction_mode
    async def check_account_availability(self, account: str) -> bool:
        user = await self.uow.user.get_by_query_one_or_none(
            email=account.lower(),
        )
        return user is None

    @transaction_mode
    async def initiate_admin_registration(self, account: str) -> None:
        account = account.lower()
        if not await self.check_account_availability(account):
            raise HTTPException(
                status_code=HTTP_400_BAD_REQUEST,
                detail='Account already exists',
            )
        invite_token = generate_admin_invite_token(account, role=UserRole.ADMIN)
        await send_invitation_email(account, invite_token)

    @transaction_mode
    async def initiate_employee_registration(
            self,
            company_id: UUID4,
            account: str,
            role: UserRole,
            current_user: UserSchema,

    ) -> None:
        check_user_is_admin(current_user)
        check_company_is_yours(current_user, company_id)
        account = account.lower()
        invite_token = generate_employee_invite_token(company_id, account, role)
        await send_invitation_email(account, invite_token)

    @transaction_mode
    async def confirm_invitation(self, invite_token: str) -> dict:
        payload = verify_invite_token(invite_token)
        if not payload:
            raise HTTPException(
                status_code=HTTP_400_BAD_REQUEST,
                detail='Invalid invite token',
            )
        return payload

    @transaction_mode
    async def complete_company_with_admin_registration(self, data: SignUpCompleteRequest) -> UserModel:
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

    @transaction_mode
    async def complete_user_in_company_registration(
            self,
            payload: dict,
    ) -> UserModel:

        account_email = payload.get('sub')
        role_value = payload.get('role', UserRole.EMPLOYEE.value)
        role = UserRole(role_value)
        company_id = payload.get('company_id')

        user: UserModel | None = await self.uow.user.get_by_query_one_or_none(
            email=account_email,
            company_id=company_id,
        )
        if not user:
            raise HTTPException(
                status_code=HTTP_403_FORBIDDEN,
                detail='User in this company not found',
            )
        if not account_email:
            raise HTTPException(
                status_code=HTTP_400_BAD_REQUEST,
                detail='Invalid token payload',
            )

        user = await self.uow.user.update_one_by_email(
            obj_email=account_email,
            role=role,
            active=True,
        )
        return user
