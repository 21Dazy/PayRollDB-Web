from typing import Optional, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field

# 系统参数基础模型
class SystemParameterBase(BaseModel):
    param_key: str
    param_value: str
    description: Optional[str] = None

# 系统参数创建模型
class SystemParameterCreate(SystemParameterBase):
    pass

# 系统参数更新模型
class SystemParameterUpdate(BaseModel):
    param_value: str
    description: Optional[str] = None

# 数据库中的系统参数
class SystemParameterInDB(SystemParameterBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True

# 系统参数响应模型
class SystemParameterResponse(SystemParameterInDB):
    pass

# 操作日志基础模型
class OperationLogBase(BaseModel):
    user_id: int
    operation_type: str
    operation_detail: str
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None

# 操作日志创建模型
class OperationLogCreate(OperationLogBase):
    pass

# 数据库中的操作日志
class OperationLogInDB(OperationLogBase):
    id: int
    created_at: datetime

    class Config:
        orm_mode = True

# 操作日志响应模型
class OperationLogResponse(OperationLogInDB):
    username: str

# 系统状态响应模型
class SystemStatusResponse(BaseModel):
    status: str
    uptime: str
    db_status: str
    total_users: int
    total_employees: int
    version: str 