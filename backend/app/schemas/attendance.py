from typing import Optional, List
from datetime import date, datetime
from pydantic import BaseModel, Field

from .employee import EmployeeResponse

# 考勤状态基础模型
class AttendanceStatusBase(BaseModel):
    name: str
    description: Optional[str] = None
    is_deduction: bool = False
    deduction_value: float = 0

# 考勤状态创建模型
class AttendanceStatusCreate(AttendanceStatusBase):
    pass

# 考勤状态更新模型
class AttendanceStatusUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    is_deduction: Optional[bool] = None
    deduction_value: Optional[float] = None

# 数据库中的考勤状态
class AttendanceStatusInDB(AttendanceStatusBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True

# 考勤状态响应模型
class AttendanceStatusResponse(AttendanceStatusInDB):
    pass

# 考勤记录基础模型
class AttendanceBase(BaseModel):
    employee_id: int
    date: date
    status_id: int
    overtime_hours: float = 0
    remarks: Optional[str] = None

# 考勤记录创建模型
class AttendanceCreate(AttendanceBase):
    pass

# 考勤记录批量创建模型
class AttendanceBatchCreate(BaseModel):
    employee_ids: List[int]
    date: date
    status_id: int
    overtime_hours: float = 0
    remarks: Optional[str] = None

# 考勤记录更新模型
class AttendanceUpdate(BaseModel):
    status_id: Optional[int] = None
    overtime_hours: Optional[float] = None
    remarks: Optional[str] = None

# 数据库中的考勤记录
class AttendanceInDB(AttendanceBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True

# 考勤记录响应模型 - 基本信息
class AttendanceResponse(AttendanceInDB):
    pass

# 考勤记录响应模型 - 带员工和状态信息
class AttendanceDetailResponse(BaseModel):
    id: int
    employee: EmployeeResponse
    date: date
    status: AttendanceStatusResponse
    overtime_hours: float
    remarks: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True

# 考勤统计响应模型
class AttendanceStatResponse(BaseModel):
    normal_days: int
    late_days: int
    early_leave_days: int
    absent_days: int
    sick_leave_days: int
    personal_leave_days: int
    annual_leave_days: int
    overtime_hours: float 