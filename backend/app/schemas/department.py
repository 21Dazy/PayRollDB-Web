from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel

# 基础部门模式
class DepartmentBase(BaseModel):
    name: str
    description: Optional[str] = None

# 创建部门
class DepartmentCreate(DepartmentBase):
    pass

# 更新部门
class DepartmentUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None

# 部门响应模式
class DepartmentResponse(DepartmentBase):
    id: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

# 包含员工数量的部门响应
class DepartmentWithEmployeeCount(DepartmentResponse):
    employee_count: int 