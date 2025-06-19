from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel, EmailStr, Field, validator
from enum import Enum

# 枚举类型
class RegistrationStatus(str, Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"

class PermissionType(str, Enum):
    VIEW_SALARY = "view_salary"
    VIEW_ATTENDANCE = "view_attendance"
    EDIT_PROFILE = "edit_profile"
    VIEW_PAYSLIP = "view_payslip"

class ChangeType(str, Enum):
    PHONE = "phone"
    EMAIL = "email"
    ADDRESS = "address"
    BANK_INFO = "bank_info"
    EMERGENCY_CONTACT = "emergency_contact"

class ChangeRequestStatus(str, Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"

# 员工验证请求
class EmployeeVerifyRequest(BaseModel):
    real_name: str = Field(..., min_length=2, max_length=50, description="真实姓名")
    id_card: Optional[str] = Field(None, pattern=r"^\d{17}[\dXx]$", description="身份证号")
    employee_id: Optional[int] = Field(None, description="员工工号")
    
    @validator('id_card', 'employee_id')
    def at_least_one_required(cls, v, values):
        """至少需要身份证或员工工号其中一个"""
        if not v and not values.get('id_card') and not values.get('employee_id'):
            raise ValueError('身份证号或员工工号至少需要提供一个')
        return v

# 员工验证响应
class EmployeeVerifyResponse(BaseModel):
    found: bool
    employee_id: Optional[int] = None
    employee_name: Optional[str] = None
    department_name: Optional[str] = None
    position_name: Optional[str] = None
    message: str

# 用户注册请求
class UserRegistrationRequest(BaseModel):
    username: str = Field(..., min_length=3, max_length=50, description="用户名")
    password: str = Field(..., min_length=6, max_length=128, description="密码")
    real_name: str = Field(..., min_length=2, max_length=50, description="真实姓名")
    id_card: Optional[str] = Field(None, pattern=r"^\d{17}[\dXx]$", description="身份证号")
    phone: str = Field(..., pattern=r"^1[3-9]\d{9}$", description="手机号")
    email: Optional[EmailStr] = Field(None, description="邮箱")
    employee_id: Optional[int] = Field(None, description="要绑定的员工ID")
    verification_code: Optional[str] = Field(None, description="验证码")
    
    @validator('username')
    def validate_username(cls, v):
        """验证用户名格式"""
        if not v.replace('_', '').replace('-', '').isalnum():
            raise ValueError('用户名只能包含字母、数字、下划线和短横线')
        return v

# 用户注册响应
class UserRegistrationResponse(BaseModel):
    id: int
    username: str
    real_name: str
    phone: str
    email: Optional[str]
    status: RegistrationStatus
    employee_id: Optional[int]
    created_at: datetime
    message: str
    
    class Config:
        from_attributes = True

# 注册申请列表响应（管理员用）
class RegistrationListResponse(BaseModel):
    id: int
    username: str
    real_name: str
    phone: str
    email: Optional[str]
    status: RegistrationStatus
    employee_name: Optional[str]
    department_name: Optional[str]
    position_name: Optional[str]
    created_at: datetime
    admin_remarks: Optional[str]
    
    class Config:
        from_attributes = True

# 注册审核请求
class RegistrationApprovalRequest(BaseModel):
    action: str = Field(..., pattern="^(approve|reject)$", description="审核动作：approve或reject")
    remarks: Optional[str] = Field(None, max_length=255, description="审核备注")

# 用户权限响应
class UserPermissionResponse(BaseModel):
    id: int
    permission_type: PermissionType
    is_granted: bool
    granted_at: Optional[datetime]
    expires_at: Optional[datetime]
    
    class Config:
        from_attributes = True

# 信息变更申请请求
class ChangeRequestCreate(BaseModel):
    change_type: ChangeType
    field_name: str = Field(..., max_length=50, description="字段名称")
    new_value: str = Field(..., max_length=500, description="新值")
    reason: Optional[str] = Field(None, max_length=255, description="变更原因")

# 信息变更申请响应
class ChangeRequestResponse(BaseModel):
    id: int
    change_type: ChangeType
    field_name: str
    old_value: Optional[str]
    new_value: str
    reason: Optional[str]
    status: ChangeRequestStatus
    admin_remarks: Optional[str]
    approved_at: Optional[datetime]
    created_at: datetime
    
    class Config:
        from_attributes = True

# 紧急联系人基础模型
class EmergencyContactBase(BaseModel):
    contact_name: str = Field(..., min_length=2, max_length=50, description="联系人姓名")
    relationship: str = Field(..., max_length=20, description="关系")
    phone: str = Field(..., pattern=r"^1[3-9]\d{9}$", description="联系电话")
    address: Optional[str] = Field(None, max_length=255, description="联系地址")
    is_primary: bool = Field(False, description="是否主要联系人")

# 紧急联系人创建
class EmergencyContactCreate(EmergencyContactBase):
    pass

# 紧急联系人响应
class EmergencyContactResponse(EmergencyContactBase):
    id: int
    employee_id: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

# 用户设置基础模型
class UserSettingBase(BaseModel):
    setting_key: str = Field(..., max_length=50, description="设置键")
    setting_value: str = Field(..., max_length=255, description="设置值")
    description: Optional[str] = Field(None, max_length=255, description="设置描述")

# 用户设置创建
class UserSettingCreate(UserSettingBase):
    pass

# 用户设置更新
class UserSettingUpdate(BaseModel):
    setting_value: str = Field(..., max_length=255, description="设置值")
    description: Optional[str] = Field(None, max_length=255, description="设置描述")

# 用户设置响应
class UserSettingResponse(UserSettingBase):
    id: int
    user_id: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

# 活动日志响应
class ActivityLogResponse(BaseModel):
    id: int
    action_type: str
    resource_type: Optional[str]
    resource_id: Optional[int]
    description: Optional[str]
    ip_address: Optional[str]
    created_at: datetime
    
    class Config:
        from_attributes = True

# 发送验证码请求
class SendVerificationCodeRequest(BaseModel):
    phone: str = Field(..., pattern=r"^1[3-9]\d{9}$", description="手机号")

# 验证码验证请求
class VerifyCodeRequest(BaseModel):
    phone: str = Field(..., pattern=r"^1[3-9]\d{9}$", description="手机号")
    code: str = Field(..., min_length=4, max_length=6, description="验证码") 