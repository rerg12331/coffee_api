from typing import List
from pydantic import BaseModel, Field, EmailStr

class RegistrationUserCreate(BaseModel):
    username: str
    first_name: str
    last_name: str
    email: EmailStr
    password: str = Field(min_length=6)

class RegistrationResponse(BaseModel):
    message: str
    user_id: int

class AuthenticationUserLogin(BaseModel):
    email: EmailStr
    password: str

class AuthenticationResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str

class VerificationData(BaseModel):
    verification_code: int

class VerificationResponse(BaseModel):
    status: bool
    message: str

class AccessResponse(BaseModel):
    access_token: str
    token_type: str

class RefreshResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str