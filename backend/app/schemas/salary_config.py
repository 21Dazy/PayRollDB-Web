from typing import Optional, List
from datetime import date
from decimal import Decimal
from pydantic import BaseModel

# 薪资配置项基础模式
class SalaryConfigItemBase(BaseModel):
    item_id: int
    value: Decimal
    base_item: Optional[str] = None
    is_active: bool = True
    effective_date: date

class SalaryConfigItemCreate(SalaryConfigItemBase):
    pass

class SalaryConfigItemUpdate(BaseModel):
    value: Optional[Decimal] = None
    base_item: Optional[str] = None
    is_active: Optional[bool] = None
    effective_date: Optional[date] = None

class SalaryConfigItemInDB(SalaryConfigItemBase):
    id: int
    employee_id: int
    item_name: Optional[str] = None
    type: Optional[str] = None
    is_percentage: Optional[bool] = None
    is_system: Optional[bool] = None
    
    class Config:
        from_attributes = True

# 员工薪资配置模式
class EmployeeSalaryConfigBase(BaseModel):
    employee_id: int
    items: List[SalaryConfigItemInDB]

class EmployeeSalaryConfigCreate(BaseModel):
    items: List[SalaryConfigItemCreate]

class EmployeeSalaryConfigUpdate(BaseModel):
    items: List[SalaryConfigItemCreate]

class EmployeeSalaryConfig(EmployeeSalaryConfigBase):
    class Config:
        from_attributes = True

# 薪资生成请求模式
class SalaryGenerateRequest(BaseModel):
    year: int
    month: int
    department_id: Optional[int] = None
    employee_ids: Optional[List[int]] = None

class SalaryGenerateResponse(BaseModel):
    success: bool
    message: str
    generated_count: int
    failed_count: int = 0
    errors: Optional[List[str]] = None 