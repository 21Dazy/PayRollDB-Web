from typing import Optional, List
from datetime import date, datetime
from pydantic import BaseModel, Field
from enum import Enum

from .employee import EmployeeResponse

# 工资项目类型枚举
class SalaryItemType(str, Enum):
    addition = "addition"
    deduction = "deduction"

# 工资状态枚举
class SalaryStatus(str, Enum):
    pending = "pending"
    paid = "paid"

# 工资项目基础模型
class SalaryItemBase(BaseModel):
    name: str
    type: SalaryItemType
    is_percentage: bool = False
    is_system: bool = False

# 工资项目创建模型
class SalaryItemCreate(SalaryItemBase):
    pass

# 工资项目更新模型
class SalaryItemUpdate(BaseModel):
    name: Optional[str] = None
    type: Optional[SalaryItemType] = None
    is_percentage: Optional[bool] = None
    is_system: Optional[bool] = None

# 数据库中的工资项目
class SalaryItemInDB(SalaryItemBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True

# 工资项目响应模型
class SalaryItemResponse(SalaryItemInDB):
    pass

# 工资明细基础模型
class SalaryDetailBase(BaseModel):
    salary_id: int
    item_id: int
    amount: float

# 工资明细创建模型
class SalaryDetailCreate(SalaryDetailBase):
    pass

# 工资明细更新模型
class SalaryDetailUpdate(BaseModel):
    amount: Optional[float] = None

# 数据库中的工资明细
class SalaryDetailInDB(SalaryDetailBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True

# 工资明细响应模型 - 基本信息
class SalaryDetailResponse(SalaryDetailInDB):
    pass

# 工资明细响应模型 - 带项目信息
class SalaryDetailWithItemResponse(BaseModel):
    id: int
    item: SalaryItemResponse
    amount: float

    class Config:
        orm_mode = True

# 工资记录基础模型
class SalaryRecordBase(BaseModel):
    employee_id: int
    year: int
    month: int
    base_salary: float
    overtime_pay: float = 0
    bonus: float = 0
    deduction: float = 0
    social_security: float = 0
    personal_tax: float = 0
    net_salary: float
    status: SalaryStatus = SalaryStatus.pending
    payment_date: Optional[datetime] = None
    remark: Optional[str] = None

# 工资记录创建模型
class SalaryRecordCreate(BaseModel):
    employee_id: int
    year: int
    month: int
    details: List[SalaryDetailCreate] = []

# 工资记录更新模型
class SalaryRecordUpdate(BaseModel):
    bonus: Optional[float] = None
    deduction: Optional[float] = None
    remark: Optional[str] = None

# 工资发放模型
class SalaryPaymentRequest(BaseModel):
    record_ids: List[int]
    payment_date: datetime

# 工资发放响应
class SalaryPaymentResponse(BaseModel):
    success: bool
    count: int
    message: str

# 数据库中的工资记录
class SalaryRecordInDB(SalaryRecordBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True

# 工资记录响应模型 - 基本信息
class SalaryRecordResponse(SalaryRecordInDB):
    pass

# 工资记录响应模型 - 带员工信息
class SalaryRecordDetailResponse(BaseModel):
    id: int
    employee: EmployeeResponse
    year: int
    month: int
    base_salary: float
    overtime_pay: float
    bonus: float
    deduction: float
    social_security: float
    personal_tax: float
    net_salary: float
    status: SalaryStatus
    payment_date: Optional[datetime] = None
    remark: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    details: List[SalaryDetailWithItemResponse] = []

    class Config:
        orm_mode = True 