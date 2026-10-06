import re
from typing import Optional
from pydantic import BaseModel, EmailStr, Field, field_validator, model_validator

from app.schemas.user import UserWithProfileResponse


class UserRegisterRequest(BaseModel):
    full_name: str = Field(min_length=2, max_length=100)
    password: str = Field(min_length=6, max_length=128)
    phone: Optional[str] = Field(default=None, max_length=20)
    email: Optional[EmailStr] = None
    preferred_language: str = Field(default="en", max_length=10)

    @field_validator("full_name")
    @classmethod
    def validate_full_name(cls, v: str) -> str:
        trimmed = v.strip()
        if len(trimmed) < 2 or len(trimmed) > 100:
            raise ValueError("Please enter a valid full name.")
        if any(c.isdigit() for c in trimmed):
            raise ValueError("Please enter a valid full name.")
        if not re.match(r"^[A-Za-z\u00C0-\u024F\u1E00-\u1EFF\u0900-\u0D7F\s.'-]+$", trimmed):
            raise ValueError("Please enter a valid full name.")
        if not re.match(r"^[A-Za-z\u00C0-\u024F\u1E00-\u1EFF\u0900-\u0D7F]", trimmed):
            raise ValueError("Please enter a valid full name.")
        letters = re.findall(r"[A-Za-z\u00C0-\u024F\u1E00-\u1EFF\u0900-\u0D7F]", trimmed)
        if len(letters) < 2:
            raise ValueError("Please enter a valid full name.")
        if re.search(r"[.'-]{2,}", trimmed):
            raise ValueError("Please enter a valid full name.")
        return trimmed

    @field_validator("phone")
    @classmethod
    def validate_phone(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return None
        trimmed = v.strip()
        if not trimmed:
            return None
        clean_chars = re.sub(r"[\s\-]", "", trimmed)
        if len(clean_chars) < 10 or len(clean_chars) > 15:
            raise ValueError("Please enter a valid email address or mobile number.")
        if not re.match(r"^\+?[0-9a-zA-Z]+$", clean_chars):
            raise ValueError("Please enter a valid email address or mobile number.")
        if not re.match(r"^(\+91|91|0|[6-9])", clean_chars):
            raise ValueError("Please enter a valid email address or mobile number.")
        return trimmed

    @field_validator("password")
    @classmethod
    def validate_password(cls, v: str) -> str:
        if len(v.strip()) == 0 or len(v) < 6:
            raise ValueError("Password does not meet the required security requirements.")
        if v.isdigit():
            raise ValueError("Password does not meet the required security requirements.")
        return v

    @model_validator(mode="after")
    def check_identifier_provided(self):
        if not self.phone and not self.email:
            raise ValueError("Either a valid phone number or email address must be provided.")
        return self


class UserLoginRequest(BaseModel):
    identifier: str = Field(min_length=3, description="Phone number or email address")
    password: str = Field(min_length=1)


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int
    user: UserWithProfileResponse


class TokenRefreshRequest(BaseModel):
    refresh_token: str


class AccessTokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: int
