from typing import TYPE_CHECKING

from sqlalchemy import Column, ForeignKey, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.models import BaseModel
from src.schemas.position import PositionInDB
from src.utils.custom_types import created_at, integer_pk, updated_at

if TYPE_CHECKING:
    from src.models.position_in_subdivision import PositionInSubdivisionModel
    from src.models.user_in_position import PositionAssignmentModel


class PositionModel(BaseModel):
    __tablename__ = 'position'
    __table_args__ = (
        UniqueConstraint(
            'title',
            'subdivision_id',
            name='unique_position_in_subdivision_name',
        ),
    )

    id: Mapped[integer_pk]
    title: Mapped[str] = Column(String(100), nullable=False)
    subdivision_id: Mapped[int] = mapped_column(
        ForeignKey('subdivision.id', ondelete='CASCADE'),
        nullable=False,
    )
    created_at: Mapped[created_at]
    updated_at: Mapped[updated_at]

    position_in_subdivision: Mapped['PositionInSubdivisionModel'] = relationship(
        'PositionInSubdivisionModel',
        back_populates='positions',
        cascade='all, delete',
        passive_deletes=True,
    )
    position_assignment: Mapped[list['PositionAssignmentModel']] = relationship(
        'PositionAssignmentModel',
        back_populates='position',
        cascade='all, delete',
        passive_deletes=True,
    )

    def to_pydantic_schema(self) -> PositionInDB:
        return PositionInDB(**self.__dict__)
