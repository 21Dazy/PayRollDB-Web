from typing import Optional, List
from datetime import date, datetime
from pydantic import BaseModel, EmailStr, Field, validator

from .department import DepartmentResponse
from .position import PositionResponse

# 基础员工模式
class EmployeeBase(BaseModel):
    name: str
    department_id: int
    position_id: int
    base_salary: float
    hire_date: date
    phone: Optional[str] = None
    email: Optional[str] = None
    address: Optional[str] = None
    id_card: Optional[str] = None
    bank_name: Optional[str] = None
    bank_account: Optional[str] = None
    status: bool = True

# 创建员工模式
class EmployeeCreate(EmployeeBase):
    pass

# 更新员工模式
class EmployeeUpdate(BaseModel):
    name: Optional[str] = None
    department_id: Optional[int] = None
    position_id: Optional[int] = None
    base_salary: Optional[float] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    address: Optional[str] = None
    id_card: Optional[str] = None
    bank_name: Optional[str] = None
    bank_account: Optional[str] = None
    status: Optional[bool] = None

# 员工离职请求
class EmployeeLeaveRequest(BaseModel):
    leave_date: date
    remarks: Optional[str] = None

# 数据库中的员工
class EmployeeInDB(EmployeeBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True

# 员工响应模式 - 基本信息
class EmployeeResponse(EmployeeInDB):
    pass

# 员工响应模式 - 带部门和职位信息
class EmployeeDetailResponse(BaseModel):
    id: int
    name: str
    department: DepartmentResponse
    position: PositionResponse
    base_salary: float
    hire_date: date
    status: bool
    phone: Optional[str] = None
    email: Optional[str] = None
    address: Optional[str] = None
    id_card: Optional[str] = None
    bank_name: Optional[str] = None
    bank_account: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True 