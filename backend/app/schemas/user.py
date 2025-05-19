from typing import Optional
from datetime import datetime
from pydantic import BaseModel, EmailStr, Field

# 基础用户模式
class UserBase(BaseModel):
    username: str
    employee_id: Optional[int] = None
    role: str

# 创建用户
class UserCreate(UserBase):
    password: str
    
# 更新用户
class UserUpdate(BaseModel):
    username: Optional[str] = None
    password: Optional[str] = None
    employee_id: Optional[int] = None
    role: Optional[str] = None
    is_active: Optional[bool] = None
    
# 用户响应模式
class UserResponse(UserBase):
    id: int
    is_active: bool
    last_login: Optional[datetime] = None
    
    class Config:
        from_attributes = True

# 密码修改
class UserPasswordUpdate(BaseModel):
    current_password: str
    new_password: str 