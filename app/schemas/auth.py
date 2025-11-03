from pydantic import BaseModel, EmailStr


class RegisterIn(BaseModel):
    email: str
    password: str
    full_name: str
    phone: str

class TokenPair(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    role: str          # ✅ thêm role
    full_name: str     # ✅ tùy bạn muốn FE hiển thị
    email: str

class RefreshIn(BaseModel):
    refresh_token: str
