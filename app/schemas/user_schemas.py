"""schemas for User"""

import uuid
from pydantic import BaseModel, Field, model_validator
from pydantic.networks import EmailStr
from fastapi import HTTPException, status


class UserBase(BaseModel):
    """User Base schema"""

    name: str = Field(min_length=5, max_length=50)
    email: EmailStr
    password: str = Field(min_length=5, max_length=50)


class UserRegister(UserBase):
    """shemas for user registration"""

    confirm_password: str = Field(min_length=5, max_length=50)

    @model_validator(mode="after")
    def check_passwords_match(self):
        if self.password != self.confirm_password:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="passwords do not match"
            )
        return self
