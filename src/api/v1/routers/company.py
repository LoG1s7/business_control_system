"""The module contains base routes for working with company."""

from typing import TYPE_CHECKING

from fastapi import APIRouter, Depends, HTTPException
from pydantic import UUID4
from starlette.status import HTTP_200_OK, HTTP_201_CREATED, HTTP_403_FORBIDDEN

from src.api.v1.services import CompanyService, UserService
from src.api.v1.utils.validators import get_current_active_auth_user
from src.schemas.company import (
    CompanyResponse,
    CompanyWithUsers,
    CreateCompanyRequest,
    CreateCompanyResponse,
)
from src.schemas.user import CreateUserResponse, CreateUserWithCompanyRequest, UserRole, UserSchema

if TYPE_CHECKING:
    from src.models import CompanyModel, UserModel

router = APIRouter(prefix='/company')


@router.post(
    path='/',
    status_code=HTTP_201_CREATED,
)
async def create_company(
    company: CreateCompanyRequest,
    service: CompanyService = Depends(CompanyService),
) -> CreateCompanyResponse:
    """Create company."""
    created_user: CompanyModel = await service.create_company(company)
    return CreateCompanyResponse(payload=created_user.to_pydantic_schema())


@router.get(
    path='/{company_id}',
    status_code=HTTP_200_OK,
)
async def get_company_with_users(
    company_id: UUID4,
    service: CompanyService = Depends(CompanyService),
) -> CompanyResponse:
    """Get company by ID."""
    company: CompanyWithUsers = await service.get_company_with_users(company_id)
    return CompanyResponse(payload=company)


@router.post(
    path='/user/{company_id}',
    status_code=HTTP_200_OK,
)
async def create_user_in_company(
    company_id: UUID4,
    create_user: CreateUserWithCompanyRequest,
    company_service: CompanyService = Depends(CompanyService),
    user_service: UserService = Depends(UserService),
    current_user: UserSchema = Depends(get_current_active_auth_user),
) -> CreateUserResponse:
    """Get company by ID."""
    if not current_user.role == UserRole.ADMIN:
        raise HTTPException(status_code=HTTP_403_FORBIDDEN, detail='Allowed only for admin')
    if current_user.company_id != company_id:
        raise HTTPException(status_code=HTTP_403_FORBIDDEN, detail='Allowed only for your company')
    company: CompanyWithUsers = await company_service.get_company_with_users(company_id)
    created_user: UserModel = await user_service.create_user(create_user, company.id)
    created_user.active = True
    return CreateUserResponse(payload=created_user.to_pydantic_schema())
