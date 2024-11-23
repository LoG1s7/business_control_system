from fastapi import HTTPException, Depends
from starlette.status import HTTP_404_NOT_FOUND, HTTP_403_FORBIDDEN

from pydantic import UUID4

from src.schemas.company import CompanyWithUsers
from src.models import UserModel, CompanyModel
from src.schemas.user import CreateUserRequest, UserSchema, UserRole
from src.utils.service import BaseService
from src.utils.unit_of_work import transaction_mode
from src.utils.auth.jwt_tools import hash_password


class UserInCompanyService(BaseService):

    @staticmethod
    def _check_company_exists(company: CompanyModel | None) -> None:
        if not company:
            raise HTTPException(status_code=HTTP_404_NOT_FOUND, detail='Company not found')

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
        company = await self.get_company_with_users(company_id)
        if not current_user.role == UserRole.ADMIN:
            raise HTTPException(status_code=HTTP_403_FORBIDDEN, detail='Allowed only for admin')
        if current_user.company_id != company.id:
            raise HTTPException(status_code=HTTP_403_FORBIDDEN, detail='Allowed only for your company')
        user_data = user_request.model_dump()
        plain_password = user_data.pop('password')
        user_data['hashed_password'] = hash_password(plain_password)
        user_data['company_id'] = company.id
        return await self.uow.user.add_one_and_get_obj(**user_data)
