from pydantic import BaseModel, EmailStr


class LoginRequest(BaseModel):
    email: EmailStr
    mot_de_passe: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class MotDePasseOublieRequest(BaseModel):
    email: EmailStr


class ReinitialiserMotDePasseRequest(BaseModel):
    token: str
    nouveau_mot_de_passe: str


class MessageResponse(BaseModel):
    message: str
