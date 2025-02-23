"""The module contains base routes for working with user."""

from typing import TYPE_CHECKING

from fastapi import APIRouter, Depends
from pydantic import UUID4
from starlette.status import HTTP_200_OK, HTTP_201_CREATED, HTTP_204_NO_CONTENT

from src.api.v1.services import UserInCompanyService, UserService
from src.schemas.user import (
    CreateUserResponse,
    CreateUserWithCompanyRequest,
    UpdateUserRequest,
    UserFilters,
    UserResponse,
    UserSchema,
    UsersListResponse,
)
from src.utils.auth.validators import get_current_active_auth_user, get_current_admin_auth_user

if TYPE_CHECKING:
    from src.models import UserModel

router = APIRouter(prefix='/user')


@router.post(
    path='/{company_id}',
    status_code=HTTP_201_CREATED,
)
async def create_user_in_company(
    company_id: UUID4,
    user_request: CreateUserWithCompanyRequest,
    user_in_company_service: UserInCompanyService = Depends(UserInCompanyService),
    admin: UserSchema = Depends(get_current_admin_auth_user),
) -> CreateUserResponse:
    """Get company by ID."""
    created_user: UserModel = await user_in_company_service.create_user_in_company(
        user_request=user_request,
        company_id=company_id,
        current_user=admin,
    )
    return CreateUserResponse(payload=created_user.to_pydantic_schema())


@router.get(
    path='/{user_id}',
    status_code=HTTP_200_OK,
)
async def get_user(
    user_id: UUID4,
    service: UserService = Depends(UserService),
) -> UserResponse:
    """Get user by ID."""
    user: UserModel | None = await service.get_user_by_id(user_id)
    return UserResponse(payload=user.to_pydantic_schema())


@router.put(
    path='/{user_id}',
    status_code=HTTP_200_OK,
)
async def update_user(
    user_id: UUID4,
    user: UpdateUserRequest,
    service: UserService = Depends(UserService),
    current_user: UserSchema = Depends(get_current_active_auth_user),
) -> UserResponse:
    """Update user."""
    updated_user: UserModel = await service.update_user(user_id, user, current_user)
    return UserResponse(payload=updated_user.to_pydantic_schema())


@router.delete(
    '/{user_id}',
    status_code=HTTP_204_NO_CONTENT,
)
async def delete_user(
    user_id: UUID4,
    service: UserService = Depends(UserService),
    current_user: UserSchema = Depends(get_current_active_auth_user),
) -> None:
    """Delete user."""
    await service.delete_user(current_user=current_user, user_id=user_id)


@router.get(
    '/filters/',
    status_code=HTTP_200_OK,
)
async def get_users_by_filters(
    filters: UserFilters = Depends(UserFilters),
    service: UserService = Depends(UserService),
) -> UsersListResponse:
    """Get users by filters."""
    users = await service.get_users_by_filters(filters)
    return UsersListResponse(payload=users)
