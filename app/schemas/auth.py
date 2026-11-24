from pydantic import BaseModel, EmailStr, Field


class LoginRequest(BaseModel):
    email: EmailStr
    mot_de_passe: str = Field(min_length=1, max_length=128)


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class MotDePasseOublieRequest(BaseModel):
    email: EmailStr


class ReinitialiserMotDePasseRequest(BaseModel):
    token: str = Field(min_length=10, max_length=2048)
    nouveau_mot_de_passe: str = Field(min_length=8, max_length=128)


class MessageResponse(BaseModel):
    message: str
