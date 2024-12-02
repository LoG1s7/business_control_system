from datetime import datetime

from pydantic import BaseModel, Field

from src.schemas.response import BaseCreateResponse, BaseResponse


class PositionBase(BaseModel):
    title: str = Field(..., max_length=100)


class PositionCreateRequest(PositionBase):
    subdivision_id: int


class PositionUpdateRequest(PositionBase):
    pass


class PositionInDB(PositionBase):
    id: int
    subdivision_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class PositionResponse(BaseResponse):
    payload: PositionInDB


class PositionListResponse(BaseResponse):
    payload: list[PositionInDB]


class PositionCreateResponse(BaseCreateResponse):
    payload: PositionInDB
