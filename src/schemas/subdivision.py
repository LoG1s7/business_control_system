from datetime import datetime
from typing import Annotated

from pydantic import (
    UUID4,
    BaseModel,
    Field,
    PlainSerializer,
    PlainValidator,
    WithJsonSchema,
)
from sqlalchemy_utils import Ltree

from src.schemas.position_in_subdivision import PositionInSubdivisionDB
from src.schemas.response import BaseCreateResponse, BaseResponse

LtreeField = Annotated[
    Ltree,
    PlainValidator(Ltree),
    PlainSerializer(lambda v: v.path),
    WithJsonSchema({'type': 'string', 'examples': ['some.path']}),
]


class SubdivisionId(BaseModel):
    id: int


class SubdivisionBase(BaseModel):
    name: str


class SubdivisionCreateRequest(SubdivisionBase):
    name: str = Field(..., max_length=100)
    parent: str


class SubdivisionUpdateRequest(SubdivisionId, SubdivisionBase):
    pass


class SubdivisionUpdateByNameRequest(SubdivisionBase):
    pass


class SubdivisionInDB(SubdivisionBase):
    id: int
    path: LtreeField
    company_id: UUID4
    manager_id: UUID4 | None
    created_at: datetime
    updated_at: datetime
    position_in_subdivision: list[PositionInSubdivisionDB]

    class Config:
        from_attributes = True


class SubdivisionResponse(BaseResponse):
    payload: SubdivisionInDB


class SubdivisionListResponse(BaseResponse):
    payload: list[SubdivisionInDB]


class SubdivisionCreateResponse(BaseCreateResponse):
    payload: SubdivisionInDB
