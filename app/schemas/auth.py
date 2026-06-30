from pydantic import BaseModel, EmailStr


# -----------------------------
# Register
# -----------------------------
class RegisterSchema(BaseModel):
    name: str
    email: EmailStr
    password: str


# -----------------------------
# Login
# -----------------------------
class LoginSchema(BaseModel):
    email: EmailStr
    password: str


# -----------------------------
# JWT Token
# -----------------------------
class Token(BaseModel):
    access_token: str
    token_type: str
