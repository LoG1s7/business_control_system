from typing import TYPE_CHECKING

from fastapi import HTTPException
from pydantic import UUID4
from starlette.status import HTTP_403_FORBIDDEN, HTTP_404_NOT_FOUND

from src.models import UserModel
from src.schemas.user import CreateUserRequest, UpdateUserRequest, UserDB, UserFilters, UserSchema
from src.utils.service import BaseService
from src.utils.unit_of_work import transaction_mode
from utils.auth.jwt_tools import hash_password

if TYPE_CHECKING:
    from collections.abc import Sequence


class UserService(BaseService):
    base_repository: str = 'user'

    @transaction_mode
    async def create_user(
        self,
        user: CreateUserRequest,
        company_id: UUID4,
    ) -> UserModel:
        """Create user."""
        user_data = user.model_dump()
        plain_password = user_data.pop('password')
        user_data['hashed_password'] = hash_password(plain_password)
        user_data['company_id'] = company_id
        return await self.uow.user.add_one_and_get_obj(**user_data)

    @transaction_mode
    async def get_user_by_id(self, user_id: UUID4) -> UserModel:
        """Get user by ID."""
        user: UserModel | None = await self.uow.user.get_by_query_one_or_none(id=user_id)
        self._check_user_exists(user)
        return user

    @transaction_mode
    async def get_user_by_username(self, username: str) -> UserModel:
        """Get user by username."""
        username = username.lower()
        user: UserModel | None = await self.uow.user.get_by_query_one_or_none(username=username)
        self._check_user_exists(user)
        return user

    @transaction_mode
    async def delete_user(self, current_user: UserSchema, user_id: UUID4) -> None:
        """Delete user by ID."""
        if not await self.get_user_by_id(user_id):
            raise HTTPException(
                status_code=HTTP_404_NOT_FOUND,
                detail='User does not exist.',
            )
        if not current_user.id == user_id:
            raise HTTPException(
                status_code=HTTP_403_FORBIDDEN,
                detail='Not allowed for other users',
            )
        await self.uow.user.delete_by_query(id=user_id)

    @transaction_mode
    async def get_users_by_filters(self, filters: UserFilters) -> list[UserDB]:
        """Get list of user by filters."""
        users: Sequence[UserModel] = await self.uow.user.get_users_by_filter(filters)
        return [user.to_pydantic_schema() for user in users]

    @transaction_mode
    async def update_user(
        self,
        user_id: UUID4,
        user_request: UpdateUserRequest,
        current_user: UserSchema,
    ) -> UserModel:
        update_data = user_request.model_dump(exclude_unset=True)
        if not current_user.id == user_id:
            raise HTTPException(
                status_code=HTTP_403_FORBIDDEN,
                detail='Not allowed for other users',
            )
        if 'password' in update_data:
            update_data['hashed_password'] = hash_password(update_data.pop('password'))
        user = await self.uow.user.update_one_by_id(obj_id=user_id, **update_data)
        self._check_user_exists(user)
        return user

    @staticmethod
    def _check_user_exists(user: UserModel | None) -> None:
        """..."""
        if not user:
            raise HTTPException(status_code=HTTP_404_NOT_FOUND, detail='User not found')
