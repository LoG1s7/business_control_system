from typing import Any

from fastapi import HTTPException
from pydantic import UUID4
from starlette.status import HTTP_403_FORBIDDEN, HTTP_404_NOT_FOUND

from src.models import CompanyModel, UserModel
from src.schemas.company import CompanyWithUsers
from src.schemas.user import CreateUserRequest, UserSchema
from src.utils.auth.jwt_tools import hash_password
from src.utils.service import BaseService
from src.utils.unit_of_work import transaction_mode
from utils.auth.validators import check_company_is_yours


class UserInCompanyService(BaseService):
    @staticmethod
    def _check_company_exists(company: CompanyModel | None) -> None:
        if not company:
            raise HTTPException(
                status_code=HTTP_404_NOT_FOUND,
                detail='Company not found',
            )

    async def _check_user_exists(self, user_data: dict[str, Any] | None) -> None:
        user: UserModel = await self.get_user_by_username(user_data.get('username'))
        if user:
            raise HTTPException(
                status_code=HTTP_403_FORBIDDEN,
                detail='User with this username already exists',
            )

    @transaction_mode
    async def get_user_by_username(self, username: str) -> UserModel:
        """Get user by username."""
        user: UserModel | None = await self.uow.user.get_by_query_one_or_none(username=username)
        return user

    @transaction_mode
    async def get_company_with_users(self, company_id: UUID4) -> CompanyWithUsers:
        """Find company by ID with all users."""
        company: CompanyModel | None = await self.uow.company.get_company_with_users(company_id)
        self._check_company_exists(company)
        return CompanyWithUsers(
            id=company.id,
            inn=company.inn,
            company_name=company.company_name,
            is_active=company.is_active,
            users=[user.to_pydantic_schema() for user in company.users],
        )

    @transaction_mode
    async def create_user_in_company(
        self,
        user_request: CreateUserRequest,
        current_user: UserSchema,
        company_id: UUID4,
    ) -> UserModel:
        """Create user in company."""
        check_company_is_yours(current_user, company_id)
        user_data = user_request.model_dump()
        await self._check_user_exists(user_data)
        plain_password = user_data.pop('password')
        user_data['hashed_password'] = hash_password(plain_password)
        user_data['company_id'] = company_id
        return await self.uow.user.add_one_and_get_obj(**user_data)
