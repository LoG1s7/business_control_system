from typing import TYPE_CHECKING, Any

from fastapi import HTTPException
from pydantic import UUID4
from sqlalchemy.exc import IntegrityError
from sqlalchemy_utils import Ltree
from starlette import status

from src.models import CompanyModel, SubdivisionModel
from src.schemas.subdivision import SubdivisionInDB
from src.schemas.user import UserSchema
from src.utils.auth.validators import check_company_is_yours
from src.utils.service import BaseService
from src.utils.unit_of_work import transaction_mode

if TYPE_CHECKING:
    from collections.abc import Sequence

    from sqlalchemy import Row


class SubdivisionService(BaseService):
    base_repository = 'subdivision'

    @transaction_mode
    async def create_subdivision(
            self, company_id: UUID4, subdivision_data: dict, admin: UserSchema,
    ) -> SubdivisionInDB:
        """Create subdivision of company."""
        subdivision_name, subdivision_parent = (
            subdivision_data['name'],
            subdivision_data['parent'],
        )
        company: CompanyModel = await self.uow.company.get_by_query_one_or_none(
            id=company_id,
        )
        self._check_company_exists(company=company)
        check_company_is_yours(user=admin, company_id=company.id)
        if subdivision_name == company.company_name:
            self._incorrect_parent_or_name_exists_error()
        elif subdivision_name == subdivision_parent:
            try:
                subdivision: SubdivisionModel = (
                    await self.uow.subdivision.add_one_and_get_obj(
                        name=subdivision_name,
                        company_id=company.id,
                        path=Ltree(subdivision_parent),
                    )
                )
                return subdivision.to_pydantic_schema()
            except IntegrityError:
                self._subdivision_exists_error()
        parent_subdivision: Ltree | None = (
            await self.uow.subdivision.get_all_path_of_parent(subdivision_parent)
        )
        self._check_parent_subdivision_exists(parent_subdivision=parent_subdivision)
        try:
            subdivision: SubdivisionModel = await self.uow.subdivision.add_one_and_get_obj(
                name=subdivision_name,
                company_id=company.id,
                path=Ltree(str(parent_subdivision) + f'.{subdivision_name}'),
            )
            return subdivision.to_pydantic_schema()
        except IntegrityError:
            self._subdivision_exists_error()

    @transaction_mode
    async def get_subdivision_by_id(
            self,
            subdivision_id: int,
    ) -> SubdivisionModel:
        """Get subdivision by ID."""
        subdivision: SubdivisionModel | None = await self.uow.subdivision.get_by_query_one_or_none(
            id=subdivision_id,
        )
        self._check_subdivision_exists(subdivision)
        return subdivision

    @transaction_mode
    async def update_subdivision_by_id(
            self,
            subdivision_id: int,
            subdivision_data: dict,
    ) -> SubdivisionInDB:
        """Update subdivision of company by name."""
        subdivision: SubdivisionModel = await self.uow.subdivision.get_by_query_one_or_none(
            id=subdivision_id,
        )
        self._check_subdivision_exists(subdivision)
        children: Sequence[Row[tuple[Any, ...] | Any]] = (
            await self.uow.subdivision.get_children_paths(
                subdivision_name=subdivision.name,
            )
        )
        path = str(subdivision.path)
        subdivision_data_name = subdivision_data['name']
        new_path = path.replace(f'{subdivision.name}', f'{subdivision_data_name}')
        try:
            updated_subdivision: SubdivisionModel = (
                await self.uow.subdivision.update_one_by_id(
                    obj_id=subdivision.id, name=subdivision_data_name, path=Ltree(new_path),
                )
            )
            await self.uow.subdivision.update_children_paths(children, subdivision_data_name)
            return updated_subdivision.to_pydantic_schema()
        except IntegrityError:
            self._subdivision_name_exists_error()

    @transaction_mode
    async def delete_subdivision_by_id(self, subdivision_id: int) -> None:
        """Delete subdivision of company by name."""
        subdivision: SubdivisionModel = await self.uow.subdivision.get_by_query_one_or_none(
            id=subdivision_id,
        )
        children: Sequence[Row[tuple[Any, ...] | Any]] = (
            await self.uow.subdivision.get_children_paths(
                subdivision_name=subdivision.name,
            )
        )
        self._check_subdivision_exists(subdivision=subdivision)
        await self.uow.subdivision.change_children_paths(children)
        await self.uow.subdivision.delete_by_query(name=subdivision.name)

    @staticmethod
    def _check_subdivision_exists(subdivision: SubdivisionModel | None) -> None:
        """Check if subdivision exists."""
        if not subdivision:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Subdivision not found')

    @staticmethod
    def _check_company_exists(company: CompanyModel | None) -> None:
        """Check if company exists."""
        if not company:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail='Company not found',
            )

    @staticmethod
    def _check_parent_subdivision_exists(parent_subdivision: Ltree | None) -> None:
        """Check if parent subdivision exists."""
        if not parent_subdivision:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Parent doesn't exists!",
            )

    @staticmethod
    def _incorrect_parent_or_name_exists_error() -> None:
        """Raises incorrect parent or name error."""
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail='Incorrect parent or name already exists!',
        )

    @staticmethod
    def _subdivision_exists_error() -> None:
        """Raises subdivision exists error."""
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail='Subdivision already exists!',
        )

    @staticmethod
    def _subdivision_name_exists_error() -> None:
        """Raises subdivision name exists error."""
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail='Subdivision name already exists!',
        )
