from typing import Annotated

from annotated_types import MaxLen, MinLen
from pydantic import UUID4, BaseModel, EmailStr, Field

from schemas.user import UserRole
from schemas.validators_mixins import EmailValidatorMixin
from src.schemas.response import BaseResponse


class CheckAccountResponse(BaseResponse):
    is_available: bool


class SignUpRequest(BaseModel):
    account: EmailStr


class SignUpConfirmRequest(BaseModel, EmailValidatorMixin):
    email: EmailStr
    invite_token: str


class SignUpConfirmUserInCompanyRequest(BaseModel, EmailValidatorMixin):
    company_id: UUID4
    email: EmailStr
    role: UserRole


class SignUpCompleteRequest(BaseModel):
    username: Annotated[str, MinLen(3), MaxLen(20)]
    email: EmailStr
    password: str = Field(min_length=6, max_length=50)
    first_name: str = Field(max_length=50)
    last_name: str = Field(max_length=50)
    middle_name: str | None = Field(max_length=50, default=None)
    company_name: str = Field(max_length=50)
