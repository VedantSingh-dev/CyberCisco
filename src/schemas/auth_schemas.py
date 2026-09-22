from pydantic import BaseModel, EmailStr


class UserRegisterRequest(BaseModel):
    full_name: str
    email: EmailStr
    password: str


class VerifyOTPRequest(BaseModel):
    email: EmailStr
    otp: str


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class ForgotPasswordRequest(BaseModel):
    email: EmailStr


class ResetPasswordRequest(BaseModel):
    email: EmailStr
    otp: str
    new_password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"