from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.models import BaseModel
from src.schemas.position_in_subdivision import PositionInSubdivisionDB
from src.utils.custom_types import integer_pk

if TYPE_CHECKING:
    from src.models.position import PositionModel
    from src.models.subdivision import SubdivisionModel


class PositionInSubdivisionModel(BaseModel):
    __tablename__ = 'position_in_subdivision'

    id: Mapped[integer_pk]
    subdivision_id: Mapped[int] = mapped_column(
        ForeignKey('subdivision.id', ondelete='CASCADE'),
        nullable=False,
    )
    position_id: Mapped[int] = mapped_column(
        ForeignKey('position.id', ondelete='CASCADE'),
        nullable=False,
    )
    subdivisions: Mapped['SubdivisionModel'] = relationship(
        back_populates='position_in_subdivision',
    )
    positions: Mapped['PositionModel'] = relationship(
        back_populates='position_in_subdivision',
    )

    def to_pydantic_schema(self) -> PositionInSubdivisionDB:
        return PositionInSubdivisionDB(**self.__dict__)
