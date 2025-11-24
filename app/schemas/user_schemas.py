"""schemas for User"""

import uuid
from pydantic import BaseModel, Field, model_validator, ConfigDict
from pydantic.networks import EmailStr
from fastapi import HTTPException, status
from app.core.auth import hash_password


class UserBase(BaseModel):
    """User Base schema"""

    name: str = Field(min_length=5, max_length=50)
    email: EmailStr
    password: str = Field(min_length=5, max_length=100)


class EmailModel(BaseModel):
    """Email schema"""

    email: EmailStr


class UserLogin(BaseModel):
    """schema for login user"""

    email: EmailStr
    password: str = Field(min_length=5, max_length=50)


class UserInfo(BaseModel):
    """schema for user info"""

    name: str = Field(min_length=5, max_length=50)
    email: EmailStr

    model_config = ConfigDict(from_attributes=True)


class UserRegister(UserBase):
    """shemas for user registration"""

    name: str = Field(min_length=5, max_length=50)
    confirm_password: str = Field(min_length=5, max_length=50)

    @model_validator(mode="after")
    def check_passwords_match(self):
        if self.password != self.confirm_password:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="passwords do not match"
            )
        self.password = hash_password(self.password)
        return self
