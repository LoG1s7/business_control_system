from typing import Annotated

from annotated_types import MaxLen, MinLen
from pydantic import BaseModel, EmailStr, Field

from src.schemas.response import BaseResponse


class CheckAccountResponse(BaseResponse):
    is_available: bool


class SignUpRequest(BaseModel):
    account: EmailStr


class SignUpConfirmRequest(BaseModel):
    account: EmailStr
    invite_token: str


class SignUpCompleteRequest(BaseModel):
    username: Annotated[str, MinLen(3), MaxLen(20)]
    email: EmailStr
    password: str = Field(min_length=6, max_length=50)
    first_name: str = Field(max_length=50)
    last_name: str = Field(max_length=50)
    company_name: str = Field(max_length=50)
