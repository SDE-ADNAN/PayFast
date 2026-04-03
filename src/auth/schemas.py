from pydantic import BaseModel, EmailStr, ConfigDict

class UserRegister(BaseModel):
    phone: str
    full_name: str
    password: str
    email: EmailStr | None = None

class UserLogin(BaseModel):
    phone: str
    password: str

class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"

class RefreshRequest(BaseModel):
    refresh_token: str
    
class UserResponse(BaseModel):
    id: str
    phone: str
    full_name: str
    role: str
    
    model_config = ConfigDict(from_attributes=True)
