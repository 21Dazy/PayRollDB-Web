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

# 员工搜索响应模式 - 包含前端需要的部门名称和职位名称
class EmployeeSearchResponse(BaseModel):
    id: int
    employee_id: str
    name: str
    department_id: int
    department_name: str
    position_id: int
    position_name: str
    base_salary: float
    hire_date: date
    status: bool
    phone: Optional[str] = None
    email: Optional[str] = None
    bank_name: Optional[str] = None
    bank_account: Optional[str] = None

    class Config:
        orm_mode = True
        
    @validator('employee_id', pre=True, always=True)
    def set_employee_id(cls, v, values):
        """确保employee_id有值，如果没有就使用id作为员工工号"""
        if v:
            return v
        return str(values.get('id', ''))
        
    @validator('department_name', pre=True, always=True)
    def extract_department_name(cls, v, values):
        """从department对象中提取部门名称"""
        if v:
            return v
        department = values.get('department')
        if department and hasattr(department, 'name'):
            return department.name
        return ""
        
    @validator('position_name', pre=True, always=True)
    def extract_position_name(cls, v, values):
        """从position对象中提取职位名称"""
        if v:
            return v
        position = values.get('position')
        if position and hasattr(position, 'name'):
            return position.name
        return "" 