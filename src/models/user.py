from typing import TYPE_CHECKING

from sqlalchemy import UUID, Boolean, Enum, ForeignKey, LargeBinary, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.models import BaseModel
from src.models.mixins import CompanyMixin
from src.schemas.user import UserDB, UserRole
from src.utils.custom_types import created_at, updated_at, uuid_pk

if TYPE_CHECKING:
    from src.models.position import PositionAssignmentModel
    from src.models.subdivision import SubdivisionModel


class UserModel(CompanyMixin, BaseModel):
    __tablename__ = 'user'

    id: Mapped[uuid_pk]
    username: Mapped[str] = mapped_column(String(50), unique=True)
    first_name: Mapped[str] = mapped_column(String(50))
    last_name: Mapped[str] = mapped_column(String(50))
    middle_name: Mapped[str | None] = mapped_column(String(50), default=None)
    email: Mapped[str] = mapped_column(String(50), default=None, unique=True)
    hashed_password: Mapped[bytes] = mapped_column(LargeBinary(60), nullable=False)
    role: Mapped[UserRole | None] = mapped_column(Enum(UserRole))
    company_id: Mapped[UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey('company.id', ondelete='SET NULL'),
        nullable=True,
    )
    active: Mapped[bool] = mapped_column(Boolean(), default=False)
    created_at: Mapped[created_at]
    updated_at: Mapped[updated_at]

    position_assignment: Mapped['PositionAssignmentModel'] = relationship(
        'PositionAssignmentModel',
        back_populates='user',
    )
    managed_subdivisions: Mapped['SubdivisionModel'] = relationship(
        'SubdivisionModel',
        back_populates='manager',
    )

    def to_pydantic_schema(self) -> UserDB:
        return UserDB(**self.__dict__)
