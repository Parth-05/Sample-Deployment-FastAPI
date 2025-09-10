from typing import Optional, Union, List
from pydantic import BaseModel, EmailStr, Field
from app.models.enums import UserRole

class ProfileBase(BaseModel):
    name: Optional[str] = None
    email: EmailStr
    phone: Optional[str] = None
    user_type: Optional[UserRole] = None   # <-- Enum here

class RegisterTrainerFields(BaseModel):
    bio: Optional[str] = None
    certifications: Optional[Union[str, List[str]]] = None
    organization_id: Optional[str] = None
    years_exp: Optional[int] = None

class RegisterClientFields(BaseModel):
    fitness_goal: Optional[str] = None

class ProfileRegister(ProfileBase):
    password: str = Field(min_length=8)
    trainer: Optional[RegisterTrainerFields] = None
    client: Optional[RegisterClientFields] = None

class ProfileOut(BaseModel):
    id: str
    name: Optional[str]
    email: EmailStr
    phone: Optional[str]
    user_type: Optional[UserRole]          # <-- Enum in responses too
    is_active: bool

    class Config:
        from_attributes = True
        
class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    refresh_token: Optional[str] = None

class Login(BaseModel):
    email: EmailStr
    password: str

class AuthData(BaseModel):
    token: Token
    profile: ProfileOut
