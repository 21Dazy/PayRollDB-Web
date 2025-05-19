from typing import Optional
from datetime import datetime
from pydantic import BaseModel

# 基础职位模式
class PositionBase(BaseModel):
    name: str
    description: Optional[str] = None

# 创建职位
class PositionCreate(PositionBase):
    pass

# 更新职位
class PositionUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None

# 职位响应模式
class PositionResponse(PositionBase):
    id: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True 