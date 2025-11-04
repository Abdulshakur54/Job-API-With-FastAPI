from uuid import UUID, uuid4
from pydantic import BaseModel, EmailStr, Field
from sqlmodel import Field as SQLField

from app.models.timestamps import TimeStamps


class Token(BaseModel):
    access_token: str
    token_type: str
    
class User(TimeStamps, table=True):
    __tablename__ = 'users'
    id: UUID = SQLField(default_factory = uuid4, primary_key=True)
    full_name: str
    email: EmailStr 
    username: str = SQLField(index=True, unique=True)
    hashed_password: str

class UserBase(BaseModel):
    full_name: str =  Field(max_length=50, min_length=3, pattern=r"^[a-z A-Z]+$")
    email: EmailStr
    username: str = Field(max_length=50, min_length=3, pattern=r"^[a-zA-Z]+[a-zA-Z0-9 ]*$")
    

    
class UserPublic(UserBase, TimeStamps):
    id: UUID
    
class UserCreate(UserBase):
    password: str = Field(
        max_length=50,
        min_length=3,
        pattern=r"^[\w ]+$",
        example="strongPass123"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "full_name": "Alice Johnson",
                "email": "alice@example.com",
                "username": "alicej",
                "password": "strongPass123"
            }
        }

class UserUpdate(BaseModel):
    full_name: str | None = Field(
        default=None,
        max_length=50,
        min_length=3,
        pattern=r"^[a-z A-Z]+$",
        example="Alice J. Updated"
    )
    email: EmailStr | None = Field(default=None, example="alice.updated@example.com")
    username: str | None = Field(
        default=None,
        max_length=50,
        min_length=3,
        pattern=r"^[a-zA-Z]+[a-zA-Z0-9 ]*$",
        example="aliceUpdated"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "full_name": "Alice J. Updated",
                "email": "alice.updated@example.com",
                "username": "aliceUpdated"
            }
        }

    
    
