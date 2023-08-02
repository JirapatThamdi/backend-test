import time
import re
from pydantic import BaseModel, Field, EmailStr, validator
from passlib.context import CryptContext
from bson.objectid import ObjectId
from datetime import datetime

password_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def generate_password_hash(password):
    """
    Generate password hash using bcrypt.
    This includes a built-in salt.
    """
    return password_context.hash(password)

def verify_password(plain_password, hased_password):

    return password_context.verify(plain_password, hased_password)

class UserModel(BaseModel):
    name: str = Field(...)
    email: EmailStr = Field(...)
    password: str = Field(...)
    hashed_password: str = Field(None, alias="hashedPassword")
    refresh_token: str = Field(None, alias="refreshToken")
    max_refresh_token_mins: int = Field(None, alias="maxRefreshTokenMins")
    created_at: float = Field(None, alias="createdAt")
    updated_at: float = Field(None, alias="updatedAt")
    api_quota_limit: int = 100


    @validator("created_at", "updated_at", pre=True,
               always=True)
    def get_unix_timestamp(cls, value):
        """
        Get UTC timestamp in seconds.
        """
        return time.time()

    @validator("max_refresh_token_mins", pre=True,
               always=True)
    def set_default_max_refresh_token_mins(cls, value):
        """
        Set default value for max_refresh_token_mins if not provided.
        """
        if value is None:
            return 60*24  # 1 day in minutes
        return value

    @validator("hashed_password", pre=True,
               always=True)
    def hash_password(cls, _, values):
        """
        Hash password.
        Get the value to hash from password field.
        and return the hashed value.
        """
        raw_password = values.get("password")

        if (len(raw_password) < 8 or
            len(raw_password) > 20 or
            raw_password is None or
                raw_password == ""):
            raise ValueError(
                "Invalid password format, password should be 8-20 characters")

        if not bool(re.search(r"(?=.*\d)(?=.*[A-Z])", raw_password)):
            raise ValueError("Password should contain alfa numeric \
characters and at least one capital letter")

        return generate_password_hash(raw_password)

    class Config:
        allow_population_by_field_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}
        schema_extra = {
            "example": {
                "name": "Jane Doe",
                "email": "jdoe@example.com",
                "password": "123456",
            }
        }

class UserResponseModel(BaseModel):
    """
    Extends BaseModel to define the User model for response.
    """
    id: str = Field(..., alias="_id")
    name: str = Field(..., alias="fullName")
    email: EmailStr = Field(...)
    max_refresh_token_mins: int = Field(None, alias="maxRefreshTokenMins")
    created_at: str = Field(..., alias="createdAt")
    updated_at: str = Field(..., alias="updatedAt")

    @validator("id", pre=True, always=True)
    def convert_object_id_to_str(cls, value):
        """
        Convert ObjectId to str for response.
        """
        return str(value)

    @validator("created_at", "updated_at", pre=True,
               always=True)
    def convert_unix_timestamp_to_readable(cls, value):
        """
        Convert unix timestamp to readable format for response.
        """
        return datetime.utcfromtimestamp(value).isoformat()

    class Config:
        """
        Extends BaseModel.Config to define the User model's configuration.
        """
        arbitrary_types_allowed = True
        allow_population_by_field_name = True
        schema_extra = {
            "example": {
                "full_name": "Jane Doe",
                "email": "example@example.com",
                "contact_umber": "1234567890",
                "address": "123, Example Street, Example City",
                "company": "Example Company",
                "refresh_token_days": 1,
                "createdAt": "2021-01-01 00:00:00",
                "updatedAt": "2021-01-01 00:00:00"
            }
        }


class UserLoginModel(BaseModel):
    """
    Extends BaseModel to define the User model for login.
    """
    email: EmailStr = Field(...)
    password: str = Field(...)


    @validator("password", pre=True,
               always=True)
    def validate_format(cls, value):
        """
        Validate password format.
        """
        if (len(value) < 8 or
            len(value) > 20 or
            value is None or
                value == ""):
            raise ValueError("Invalid email or password format")
        return value

    class Config:
        """
        Extends BaseModel.Config to define the User model's configuration.
        """
        arbitrary_types_allowed = True
        allow_population_by_field_name = True
        schema_extra = {
            "example": {
                "email": "example@example.com",
                "password": "example"
            }
        }

class RefreshTokenModel(BaseModel):
    """
    Extends BaseModel to define the RefreshToken model.
    """
    refresh_token: str = Field(..., alias="refreshToken")

    @validator("refresh_token", pre=True,
               always=True)
    def validate_format(cls, value):
        """
        Validate refresh token format.
        """
        if (value is None or value == ""):
            raise ValueError("Invalid refresh token format or token empty")
        
        return value

class AccessResponseModel(BaseModel):
    """
    Extends BaseModel to define the Access model.
    """
    user_id: str = Field(..., alias="userId")

    @validator("user_id", pre=True, always=True)
    def convert_object_id_to_str(cls, value):
        """
        Convert ObjectId to str for response.
        """
        return str(value)
    
    class Config:
        """
        Extends BaseModel.Config to define the Access model's configuration.
        """
        arbitrary_types_allowed = True

        schema_extra = {
            "example": {
                "user_id": "60a2b6e4f1d4e0f1f8b4c8c0",
            }
        }

class ImageModel(BaseModel):
    base64: str = Field(...)
    created_at: float = Field(None, alias="createdAt")
    updated_at: float = Field(None, alias="updatedAt")

    @validator("created_at", "updated_at", pre=True,
               always=True)
    def get_unix_timestamp(cls, value):
        """
        Get UTC timestamp in seconds.
        """
        return time.time()
    
    class Config:
        """
        Extends BaseModel.Config to define the User model's configuration.
        """
        arbitrary_types_allowed = True
        allow_population_by_field_name = True
        schema_extra = {
            "example": {
                "base64": "example@example.com",
            }
        }

class ImageResponseModel(BaseModel):
    """
    Extends BaseModel to define the User model for response.
    """
    id: str = Field(..., alias="_id")
    base64: str = Field(...)
    created_at: str = Field(..., alias="createdAt")
    updated_at: str = Field(..., alias="updatedAt")
    access: list[AccessResponseModel] = Field(...)

    @validator("created_at", "updated_at", pre=True,
               always=True)
    def convert_unix_timestamp_to_readable(cls, value):
        """
        Convert unix timestamp to readable format for response.
        """
        return datetime.utcfromtimestamp(value).isoformat()
    
    @validator("id", pre=True, always=True)
    def convert_object_id_to_str(cls, value):
        """
        Convert ObjectId to str for response.
        """
        return str(value)

    class Config:
        """
        Extends BaseModel.Config to define the User model's configuration.
        """
        arbitrary_types_allowed = True
        allow_population_by_field_name = True
        schema_extra = {
            "example": {
                "base64":"base64.format",
                "createdAt": "2021-01-01 00:00:00",
                "updatedAt": "2021-01-01 00:00:00",
                "access": [
                    {'user_id': '64900637b5326bc1b4c0396b'}
                ]

            }
        }
