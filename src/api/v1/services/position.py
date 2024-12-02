from fastapi import HTTPException
from pydantic import UUID4
from starlette import status

from src.models import (
    PositionAssignmentModel,
    PositionInSubdivisionModel,
    PositionModel,
    SubdivisionModel,
    UserModel,
)
from src.schemas.position import PositionInDB
from src.schemas.position_in_subdivision import PositionInSubdivisionDB
from src.schemas.subdivision import SubdivisionInDB
from src.schemas.user_in_position import PositionAssignmentDB
from src.utils.service import BaseService
from src.utils.unit_of_work import transaction_mode


class PositionService(BaseService):
    base_repository = 'position'

    @transaction_mode
    async def create_position(self, position_data: dict) -> PositionInDB:
        """Create position of subdivision."""
        position: PositionModel = await self.uow.position.get_by_query_one_or_none(
            subdivision_id=position_data['subdivision_id'],
        )
        self._check_position_already_exists(position=position)
        created_position: PositionModel = await self.uow.position.add_one_and_get_obj(
            **position_data,
        )
        return created_position.to_pydantic_schema()

    @transaction_mode
    async def get_position_by_id(
            self,
            position_id: int,
    ) -> PositionModel:
        """Get position by ID."""
        position: PositionModel | None = await self.uow.position.get_by_query_one_or_none(
            id=position_id,
        )
        self._check_position_exists(position)
        return position

    @transaction_mode
    async def update_position_by_id(
            self, position_id: int, position_data: dict,
    ) -> PositionInDB:
        """Update position of subdivision by id."""
        position: PositionModel = await self.uow.position.get_by_query_one_or_none(
            id=position_id,
        )
        self._check_position_exists(position=position)
        updated_position: PositionModel = await self.uow.position.update_one_by_id(
            id=position_id, **position_data,
        )
        return updated_position.to_pydantic_schema()

    @transaction_mode
    async def delete_position_by_id(self, position_id: str) -> None:
        """Delete position of subdivision by id."""
        position: PositionModel = await self.uow.position.get_by_query_one_or_none(
            id=position_id,
        )
        self._check_position_exists(position=position)
        await self.uow.position.delete_by_query(id=position_id)

    @transaction_mode
    async def add_users_to_position(
            self, users_position_data: dict,
    ) -> list[PositionAssignmentDB]:
        """Add users to position."""
        position: PositionModel = await self.uow.position.get_by_query_one_or_none(
            id=users_position_data['position_id'],
        )
        self._check_position_exists(position=position)
        users_position_list = []
        for user_id in users_position_data['user_id']:
            user: UserModel = await self.uow.user.get_by_query_one_or_none(id=user_id)
            self._check_user_exists(user=user)
            user_position: PositionAssignmentModel = (
                await self.uow.position_assignment.add_one_and_get_obj(
                    user_id=user_id, position_id=position.id,
                )
            )
            users_position_list.append(user_position.to_pydantic_schema())
        return users_position_list

    @transaction_mode
    async def add_position_to_subdivision(
            self, position_in_subdivision_data: dict,
    ) -> PositionInSubdivisionDB:
        """Add position to subdivision."""
        subdivision: SubdivisionModel = await self.uow.subdivision.get_by_query_one_or_none(
            id=position_in_subdivision_data['subdivision_id'],
        )
        self._check_subdivision_exists(subdivision=subdivision)
        position: PositionModel = await self.uow.position.get_by_query_one_or_none(
            id=position_in_subdivision_data['position_id'],
        )
        self._check_position_exists(position=position)
        position_in_subdivision: PositionInSubdivisionModel = (
            await self.uow.position_in_subdivision.add_one_and_get_obj(
                subdivision_id=subdivision.id, position_id=position.id,
            )
        )
        return position_in_subdivision.to_pydantic_schema()

    @transaction_mode
    async def add_subdivision_manager(
            self, user_id: UUID4, subdivision_id: int,
    ) -> SubdivisionInDB:
        """Add subdivision manager."""
        user: UserModel = await self.uow.user.get_by_query_one_or_none(id=user_id)
        self._check_user_exists(user=user)
        subdivision: SubdivisionModel = await self.uow.subdivision.get_by_query_one_or_none(
            id=subdivision_id,
        )
        self._check_subdivision_exists(subdivision=subdivision)
        subdivision_manager: SubdivisionModel = (
            await self.uow.subdivision.update_one_by_id(
                obj_id=subdivision.id, id=subdivision_id, manager_id=user.id,
            )
        )
        return subdivision_manager.to_pydantic_schema()

    @staticmethod
    def _check_position_already_exists(position: PositionModel | None) -> None:
        if position:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail='Position already exists!',
            )

    @staticmethod
    def _check_position_exists(position: PositionModel | None) -> None:
        if not position:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail='Position not found!',
            )

    @staticmethod
    def _check_user_exists(user: UserModel | None) -> None:
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail='User not found!',
            )

    @staticmethod
    def _check_subdivision_exists(subdivision: SubdivisionModel | None) -> None:
        if not subdivision:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail='Subdivision not found',
            )
