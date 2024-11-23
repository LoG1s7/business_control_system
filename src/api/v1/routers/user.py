"""The module contains base routes for working with user."""

from typing import TYPE_CHECKING

from fastapi import APIRouter, Depends, HTTPException
from pydantic import UUID4
from starlette.status import HTTP_200_OK, HTTP_204_NO_CONTENT, HTTP_403_FORBIDDEN

from src.api.v1.services.user import UserService
from src.utils.auth.validators import get_current_active_auth_user
from src.schemas.user import (
    UpdateUserRequest,
    UserFilters,
    UserResponse,
    UserSchema,
    UsersListResponse,
)

if TYPE_CHECKING:
    from src.models import UserModel

router = APIRouter(prefix='/user')


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
