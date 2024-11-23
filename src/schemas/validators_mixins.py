from typing import Annotated

from annotated_types import MaxLen, MinLen
from pydantic import field_validator, EmailStr


class EmailValidatorMixin:
    email: EmailStr

    @field_validator('email', mode="before")
    def lowercase_email(cls, v):
        return v.lower() if isinstance(v, str) else v


class UsernameValidatorMixin:
    username: Annotated[str, MinLen(3), MaxLen(20)]

    @field_validator('username', mode="before")
    def lowercase_email(cls, v):
        return v.lower() if isinstance(v, str) else v
