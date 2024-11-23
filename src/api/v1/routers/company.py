"""The module contains base routes for working with company."""

from typing import TYPE_CHECKING

from fastapi import APIRouter, Depends
from pydantic import UUID4
from starlette.status import HTTP_200_OK, HTTP_201_CREATED

from src.api.v1.services import CompanyService, UserInCompanyService
from src.schemas.company import (
    CompanyResponse,
    CompanyWithUsers,
    CreateCompanyRequest,
    CreateCompanyResponse,
)
from src.schemas.user import CreateUserResponse, CreateUserWithCompanyRequest, UserSchema
from src.utils.auth.validators import get_current_active_auth_user

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
    status_code=HTTP_201_CREATED,
)
async def create_user_in_company(
    company_id: UUID4,
    user_request: CreateUserWithCompanyRequest,
    user_in_company_service: UserInCompanyService = Depends(UserInCompanyService),
    current_user: UserSchema = Depends(get_current_active_auth_user),
) -> CreateUserResponse:
    """Get company by ID."""
    created_user: UserModel = await user_in_company_service.create_user_in_company(
        user_request=user_request,
        company_id=company_id,
        current_user=current_user,
    )
    created_user.active = True
    return CreateUserResponse(payload=created_user.to_pydantic_schema())
