from pydantic import BaseModel

from src.schemas.response import BaseCreateResponse, BaseResponse


class PositionInSubdivisionId(BaseModel):
    id: int


class CreatePositionInSubdivisionRequest(BaseModel):
    subdivision_id: int
    position_id: int


class UpdatePositionInSubdivisionRequest(
    PositionInSubdivisionId,
    CreatePositionInSubdivisionRequest,
):
    pass


class PositionInSubdivisionDB(
    PositionInSubdivisionId,
    CreatePositionInSubdivisionRequest,
):

    class Config:
        from_attributes = True


class PositionInSubdivisionResponse(BaseResponse):
    payload: PositionInSubdivisionDB


class PositionInSubdivisionListResponse(BaseResponse):
    payload: list[PositionInSubdivisionDB]


class PositionInSubdivisionCreateResponse(BaseCreateResponse):
    payload: PositionInSubdivisionDB
