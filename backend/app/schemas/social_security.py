from typing import Optional, List
from datetime import date, datetime
from pydantic import BaseModel, Field

from .employee import EmployeeResponse

# 社保配置基础模型
class SocialSecurityConfigBase(BaseModel):
    name: str
    pension_rate: float
    medical_rate: float
    unemployment_rate: float
    injury_rate: float
    maternity_rate: float
    housing_fund_rate: float
    is_default: bool = False

# 社保配置创建模型
class SocialSecurityConfigCreate(SocialSecurityConfigBase):
    pass

# 社保配置更新模型
class SocialSecurityConfigUpdate(BaseModel):
    name: Optional[str] = None
    pension_rate: Optional[float] = None
    medical_rate: Optional[float] = None
    unemployment_rate: Optional[float] = None
    injury_rate: Optional[float] = None
    maternity_rate: Optional[float] = None
    housing_fund_rate: Optional[float] = None
    is_default: Optional[bool] = None

# 数据库中的社保配置
class SocialSecurityConfigInDB(SocialSecurityConfigBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True

# 社保配置响应模型
class SocialSecurityConfigResponse(SocialSecurityConfigInDB):
    pass

# 员工社保配置基础模型
class EmployeeSocialSecurityBase(BaseModel):
    employee_id: int
    config_id: int
    base_number: float
    housing_fund_base: float
    effective_date: date

# 员工社保配置创建模型
class EmployeeSocialSecurityCreate(EmployeeSocialSecurityBase):
    pass

# 员工社保配置批量创建模型
class EmployeeSocialSecurityBatchCreate(BaseModel):
    employee_ids: List[int]
    config_id: int
    base_number: float
    housing_fund_base: float
    effective_date: date

# 员工社保配置更新模型
class EmployeeSocialSecurityUpdate(BaseModel):
    config_id: Optional[int] = None
    base_number: Optional[float] = None
    housing_fund_base: Optional[float] = None
    effective_date: Optional[date] = None

# 数据库中的员工社保配置
class EmployeeSocialSecurityInDB(EmployeeSocialSecurityBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True

# 员工社保配置响应模型 - 基本信息
class EmployeeSocialSecurityResponse(EmployeeSocialSecurityInDB):
    pass

# 员工社保配置响应模型 - 带员工和配置信息
class EmployeeSocialSecurityDetailResponse(BaseModel):
    id: int
    employee: EmployeeResponse
    config: SocialSecurityConfigResponse
    base_number: float
    housing_fund_base: float
    effective_date: date
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True

# 默认配置设置响应
class SetDefaultConfigResponse(BaseModel):
    success: bool
    message: str 