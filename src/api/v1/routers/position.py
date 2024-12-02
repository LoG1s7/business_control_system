from typing import TYPE_CHECKING

from fastapi import APIRouter, Depends
from pydantic import UUID4
from starlette.status import HTTP_200_OK, HTTP_201_CREATED, HTTP_204_NO_CONTENT

from src.api.v1.services.position import PositionService
from src.schemas.position import PositionCreateRequest, PositionInDB, PositionResponse, PositionUpdateRequest
from src.schemas.position_in_subdivision import CreatePositionInSubdivisionRequest, PositionInSubdivisionDB
from src.schemas.subdivision import SubdivisionInDB
from src.schemas.user import UserSchema
from src.schemas.user_in_position import CreatePositionAssignmentRequest, PositionAssignmentDB
from src.utils.auth.validators import get_current_admin_auth_user

if TYPE_CHECKING:
    from src.models import PositionModel

router = APIRouter(prefix='/position')


@router.post(
    '/create_position',
    status_code=HTTP_201_CREATED,
)
async def create_position(
    position_data: PositionCreateRequest,
    admin: UserSchema = Depends(get_current_admin_auth_user),
    service: PositionService = Depends(PositionService),
) -> PositionResponse | None:
    """Create position of subdivision."""
    if admin:
        created_position: PositionInDB = await service.create_position(
            position_data=position_data.model_dump(),
        )
        return PositionResponse(payload=created_position)
    return None


@router.get('/{position_id}', status_code=HTTP_200_OK)
async def get_position(
    position_id: int,
    admin: UserSchema = Depends(get_current_admin_auth_user),
    service: PositionService = Depends(PositionService),
) -> PositionResponse:
    """Get position of company by id."""
    if admin:
        position: PositionModel = await service.get_position_by_id(
            position_id=position_id,
        )
        return PositionResponse(payload=position.to_pydantic_schema())


@router.put(
    '/update_position/{position_id}',
    status_code=HTTP_200_OK)
async def update_position(
    position_id: int,
    position_data: PositionUpdateRequest,
    admin: UserSchema = Depends(get_current_admin_auth_user),
    service: PositionService = Depends(PositionService),
) -> PositionInDB:
    """Update position of department by id."""
    if admin:
        updated_position: PositionInDB = await service.update_position_by_id(
            position_id=position_id, position_data=position_data.model_dump(),
        )
        return updated_position


@router.delete(
    '/delete_position/{position_id}',
    status_code=HTTP_204_NO_CONTENT,
)
async def delete_position(
    position_id: int,
    admin: UserSchema = Depends(get_current_admin_auth_user),
    service: PositionService = Depends(PositionService),
) -> None:
    """Delete position of department by id."""
    if admin:
        await service.delete_position_by_id(position_id=position_id)


@router.post(
    '/add_users_to_position',
    status_code=HTTP_201_CREATED,
)
async def add_users_to_position(
    users_position_data: CreatePositionAssignmentRequest,
    admin: UserSchema = Depends(get_current_admin_auth_user),
    service: PositionService = Depends(PositionService),
) -> list[PositionAssignmentDB]:
    """Add users to position."""
    if admin:
        user_position: list[PositionAssignmentDB] = await service.add_users_to_position(
            users_position_data=users_position_data.model_dump(),
        )
        return user_position


@router.post(
    '/add_position_to_subdivision',
    status_code=HTTP_201_CREATED,
)
async def add_position_to_subdivision(
    position_in_subdivision_data: CreatePositionInSubdivisionRequest,
    admin: UserSchema = Depends(get_current_admin_auth_user),
    service: PositionService = Depends(PositionService),
) -> PositionInSubdivisionDB:
    """Add position to subdivision."""
    if admin:
        position_in_subdivision: PositionInSubdivisionDB = await service.add_position_to_subdivision(
            position_in_subdivision_data=position_in_subdivision_data.model_dump(),
        )
        return position_in_subdivision


@router.put(
    '/add_subdivision_manager/{user_id}/{subdivision_id}',
    status_code=HTTP_200_OK,
)
async def add_subdivision_manager(
    user_id: UUID4,
    subdivision_id: int,
    admin: UserSchema = Depends
    (get_current_admin_auth_user),
    service: PositionService = Depends(PositionService),
) -> SubdivisionInDB:
    """Add subdivision manager."""
    if admin:
        subdivision_manager: SubdivisionInDB = await service.add_subdivision_manager(
            user_id=user_id, subdivision_id=subdivision_id,
        )
        return subdivision_manager
