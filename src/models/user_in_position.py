from typing import TYPE_CHECKING

from sqlalchemy import UUID, ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.models import BaseModel
from src.schemas.user_in_position import PositionAssignmentDB
from src.utils.custom_types import created_at, integer_pk, updated_at

if TYPE_CHECKING:
    from src.models.position import PositionModel
    from src.models.user import UserModel


class PositionAssignmentModel(BaseModel):
    __tablename__ = 'position_assignment'
    __table_args__ = (UniqueConstraint('user_id', 'position_id', name='uq_user_position'),)

    id: Mapped[integer_pk]
    user_id: Mapped[UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey('user.id', ondelete='CASCADE'),
        nullable=False,
    )
    position_id: Mapped[int] = mapped_column(
        ForeignKey('position.id', ondelete='CASCADE'),
        nullable=False,
    )
    created_at: Mapped[created_at]
    updated_at: Mapped[updated_at]

    user: Mapped['UserModel'] = relationship('UserModel', back_populates='position_assignment')
    position: Mapped['PositionModel'] = relationship('PositionModel', back_populates='position_assignment')

    def to_pydantic_schema(self) -> PositionAssignmentDB:
        return PositionAssignmentDB(**self.__dict__)
