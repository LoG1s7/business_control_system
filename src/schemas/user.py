from dataclasses import dataclass
from enum import Enum
from typing import Annotated

from annotated_types import MaxLen, MinLen
from fastapi import Query
from pydantic import UUID4, BaseModel, ConfigDict, EmailStr, Field

from src.schemas.filter import TypeFilter
from src.schemas.response import BaseCreateResponse, BaseResponse
from src.schemas.validators_mixins import EmailValidatorMixin, UsernameValidatorMixin


class UserRole(Enum):
    ADMIN = 'admin'
    EMPLOYEE = 'employee'


class UserID(BaseModel):
    id: UUID4


class CreateUserWithCompanyRequest(BaseModel, UsernameValidatorMixin, EmailValidatorMixin):
    username: Annotated[str, MinLen(3), MaxLen(20)]
    first_name: str = Field(max_length=50)
    last_name: str = Field(max_length=50)
    middle_name: str | None = Field(max_length=50, default=None)
    email: EmailStr
    password: str = Field(min_length=6, max_length=50)
    role: UserRole = Field(default=UserRole.EMPLOYEE)


class CreateUserRequest(CreateUserWithCompanyRequest):
    company_id: UUID4


class UserSchema(BaseModel, UsernameValidatorMixin, EmailValidatorMixin):
    model_config = ConfigDict(strict=True)

    id: UUID4
    username: str
    first_name: str = Field(max_length=50)
    last_name: str = Field(max_length=50)
    middle_name: str | None = Field(max_length=50, default=None)
    company_id: UUID4
    email: EmailStr | None = None
    active: bool = True
    role: UserRole = Field(default=UserRole.EMPLOYEE)


class UpdateUserRequest(CreateUserWithCompanyRequest):
    first_name: str | None = Field(max_length=50)
    last_name: str | None = Field(max_length=50)
    middle_name: str | None = Field(max_length=50, default=None)
    email: EmailStr | None = None
    password: str | None = Field(min_length=6, max_length=50)
    role: UserRole | None = None


class UserDB(UserID, UserSchema):
    pass


class CreateUserResponse(BaseCreateResponse):
    payload: UserDB


class UserResponse(BaseResponse):
    payload: UserDB


class UsersListResponse(BaseResponse):
    payload: list[UserDB]


@dataclass
class UserFilters(TypeFilter):
    ids: list[UUID4] | None = Query(None)
    first_name: list[str] | None = Query(None)
    last_name: list[str] | None = Query(None)
    middle_name: list[str] | None = Query(None)
