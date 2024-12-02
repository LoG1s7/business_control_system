from typing import TYPE_CHECKING

from sqlalchemy import Column, ForeignKey, String, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy_utils import Ltree, LtreeType

from src.models import BaseModel
from src.schemas.subdivision import SubdivisionInDB
from src.utils.custom_types import created_at, integer_pk, updated_at

if TYPE_CHECKING:
    from src.models.company import CompanyModel
    from src.models.position_in_subdivision import PositionInSubdivisionModel
    from src.models.user import UserModel


class SubdivisionModel(BaseModel):
    __tablename__ = 'subdivision'
    __table_args__ = (
        UniqueConstraint(
            'name',
            'company_id',
            name='unique_subdivision_name',
        ),
    )

    id: Mapped[integer_pk]
    name: Mapped[str] = Column(String(100), nullable=False)
    path: Mapped[Ltree] = Column(LtreeType, nullable=False)
    company_id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey('company.id', ondelete='CASCADE'),
        nullable=False,
    )
    manager_id: Mapped[UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey('user.id', ondelete='SET NULL'),
        nullable=True,
    )
    created_at: Mapped[created_at]
    updated_at: Mapped[updated_at]

    company: Mapped['CompanyModel'] = relationship('CompanyModel', back_populates='subdivisions')
    manager: Mapped['UserModel'] = relationship('UserModel', back_populates='managed_subdivisions')
    position_in_subdivision: Mapped[list['PositionInSubdivisionModel']] = relationship(
        'PositionInSubdivisionModel',
        back_populates='subdivisions',
        cascade='all, delete',
        passive_deletes=True,
    )

    def to_pydantic_schema(self) -> SubdivisionInDB:
        return SubdivisionInDB(**self.__dict__)
