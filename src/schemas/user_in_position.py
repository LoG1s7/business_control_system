from pydantic import UUID4, BaseModel

from src.schemas.response import BaseCreateResponse, BaseResponse


class PositionAssignmentId(BaseModel):
    id: int


class CreatePositionAssignmentRequest(BaseModel):
    user_id: list[UUID4]
    position_id: int


class UpdateUserPositionRequest(PositionAssignmentId, CreatePositionAssignmentRequest):
    pass


class PositionAssignmentDB(PositionAssignmentId):
    user_id: UUID4
    position_id: int


class PositionAssignmentResponse(BaseResponse):
    payload: PositionAssignmentDB


class PositionAssignmentListResponse(BaseResponse):
    payload: list[PositionAssignmentDB]


class PositionAssignmentCreateResponse(BaseCreateResponse):
    payload: PositionAssignmentDB
