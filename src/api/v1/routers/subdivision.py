from typing import TYPE_CHECKING

from fastapi import APIRouter, Depends
from pydantic import UUID4
from starlette.status import HTTP_200_OK, HTTP_201_CREATED, HTTP_204_NO_CONTENT

from src.api.v1.services.subdivision import SubdivisionService
from src.schemas.subdivision import (
    SubdivisionCreateRequest,
    SubdivisionCreateResponse,
    SubdivisionInDB,
    SubdivisionResponse,
    SubdivisionUpdateByNameRequest,
)
from src.schemas.user import UserSchema
from src.utils.auth.validators import get_current_admin_auth_user

if TYPE_CHECKING:
    from src.models import SubdivisionModel

router = APIRouter(prefix='/subdivision')


@router.post('/{company_id}', status_code=HTTP_201_CREATED)
async def create_subdivision(
    company_id: UUID4,
    subdivision_data: SubdivisionCreateRequest,
    admin: UserSchema = Depends(get_current_admin_auth_user),
    service: SubdivisionService = Depends(SubdivisionService),
) -> SubdivisionCreateResponse:
    """Create subdivision of company."""
    if admin:
        new_subdivision: SubdivisionInDB = await service.create_subdivision(
            company_id=company_id,
            subdivision_data=subdivision_data.model_dump(),
            admin=admin,
        )
        return SubdivisionCreateResponse(payload=new_subdivision)


@router.get('/{subdivision_id}', status_code=HTTP_200_OK)
async def get_subdivision(
    subdivision_id: int,
    admin: UserSchema = Depends(get_current_admin_auth_user),
    service: SubdivisionService = Depends(SubdivisionService),
) -> SubdivisionResponse:
    """Get subdivision of company by id."""
    if admin:
        subdivision: SubdivisionModel = await service.get_subdivision_by_id(
            subdivision_id=subdivision_id,
        )
        return SubdivisionResponse(payload=subdivision.to_pydantic_schema())


@router.put('/{subdivision_id}', status_code=HTTP_200_OK)
async def update_subdivision(
    subdivision_id: int,
    subdivision_data: SubdivisionUpdateByNameRequest,
    admin: UserSchema = Depends(get_current_admin_auth_user),
    service: SubdivisionService = Depends(SubdivisionService),
) -> SubdivisionResponse:
    """Update subdivision of company by id."""
    if admin:
        updated_subdivision: SubdivisionInDB = await service.update_subdivision_by_id(
            subdivision_id=subdivision_id,
            subdivision_data=subdivision_data.model_dump(),
        )
        return SubdivisionResponse(payload=updated_subdivision)


@router.delete(
    '/{subdivision_id}', status_code=HTTP_204_NO_CONTENT,
)
async def delete_subdivision(
    subdivision_id: int,
    admin: UserSchema = Depends(get_current_admin_auth_user),
    service: SubdivisionService = Depends(SubdivisionService),
) -> None:
    """Delete subdivision of company by id."""
    if admin:
        await service.delete_subdivision_by_id(
            subdivision_id=subdivision_id,
        )
