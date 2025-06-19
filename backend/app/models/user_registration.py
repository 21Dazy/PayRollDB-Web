from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Boolean, Enum, Text
from sqlalchemy.orm import relationship

from app.db.base_class import Base, NoUpdateBase

class UserRegistration(Base):
    """用户注册申请模型"""
    __tablename__ = "user_registrations"
    
    username = Column(String(50), nullable=False, index=True, comment='用户名')
    password = Column(String(255), nullable=False, comment='密码(加密存储)')
    real_name = Column(String(50), nullable=False, comment='真实姓名')
    id_card = Column(String(18), nullable=False, index=True, comment='身份证号')
    phone = Column(String(20), nullable=False, index=True, comment='手机号')
    email = Column(String(100), comment='邮箱')
    employee_id = Column(Integer, ForeignKey('employees.id'), comment='申请绑定的员工ID')
    verification_code = Column(String(10), comment='验证码')
    verification_expires = Column(DateTime, comment='验证码过期时间')
    status = Column(
        Enum('pending', 'approved', 'rejected', name='registration_status'), 
        default='pending', 
        index=True,
        comment='审核状态'
    )
    admin_id = Column(Integer, ForeignKey('users.id'), comment='审核管理员ID')
    admin_remarks = Column(String(255), comment='管理员审核备注')
    
    # 关系 - 使用正确的字符串引用方式
    employee = relationship("Employee")
    admin = relationship("User", foreign_keys=[admin_id])

class UserPermission(Base):
    """用户权限配置模型"""
    __tablename__ = "user_permissions"
    
    user_id = Column(Integer, ForeignKey('users.id', ondelete="CASCADE"), nullable=False, index=True, comment='用户ID')
    permission_type = Column(
        Enum('view_salary', 'view_attendance', 'edit_profile', 'view_payslip', name='permission_type'), 
        nullable=False, 
        index=True,
        comment='权限类型'
    )
    is_granted = Column(Boolean, default=True, comment='是否授权(1:是, 0:否)')
    granted_by = Column(Integer, ForeignKey('users.id'), comment='授权人ID')
    granted_at = Column(DateTime, comment='授权时间')
    expires_at = Column(DateTime, comment='权限过期时间')
    
    # 关系 - 使用正确的字符串引用方式
    user = relationship("User", foreign_keys=[user_id], back_populates="permissions")
    granter = relationship("User", foreign_keys=[granted_by])

class EmployeeChangeRequest(Base):
    """员工信息变更申请模型"""
    __tablename__ = "employee_change_requests"
    
    employee_id = Column(Integer, ForeignKey('employees.id'), nullable=False, index=True, comment='员工ID')
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False, index=True, comment='申请用户ID')
    change_type = Column(
        Enum('phone', 'email', 'address', 'bank_info', 'emergency_contact', name='change_type'), 
        nullable=False, 
        index=True,
        comment='变更类型'
    )
    field_name = Column(String(50), nullable=False, comment='字段名称')
    old_value = Column(Text, comment='原值')
    new_value = Column(Text, nullable=False, comment='新值')
    reason = Column(String(255), comment='变更原因')
    status = Column(
        Enum('pending', 'approved', 'rejected', name='change_request_status'), 
        default='pending', 
        index=True,
        comment='审核状态'
    )
    admin_id = Column(Integer, ForeignKey('users.id'), comment='审核管理员ID')
    admin_remarks = Column(String(255), comment='管理员审核备注')
    approved_at = Column(DateTime, comment='审核时间')
    
    # 关系 - 使用正确的字符串引用方式
    employee = relationship("Employee")
    user = relationship("User", foreign_keys=[user_id])
    admin = relationship("User", foreign_keys=[admin_id])

class EmployeeEmergencyContact(Base):
    """员工紧急联系人模型"""
    __tablename__ = "employee_emergency_contacts"
    
    employee_id = Column(Integer, ForeignKey('employees.id', ondelete="CASCADE"), nullable=False, index=True, comment='员工ID')
    contact_name = Column(String(50), nullable=False, comment='联系人姓名')
    relation_type = Column(String(20), nullable=False, comment='关系')
    phone = Column(String(20), nullable=False, comment='联系电话')
    address = Column(String(255), comment='联系地址')
    is_primary = Column(Boolean, default=False, comment='是否主要联系人')
    
    # 关系 - 使用正确的字符串引用方式
    employee = relationship("Employee", back_populates="emergency_contacts")

class UserSetting(Base):
    """用户个人设置模型"""
    __tablename__ = "user_settings"
    
    user_id = Column(Integer, ForeignKey('users.id', ondelete="CASCADE"), nullable=False, index=True, comment='用户ID')
    setting_key = Column(String(50), nullable=False, comment='设置键')
    setting_value = Column(String(255), nullable=False, comment='设置值')
    description = Column(String(255), comment='设置描述')
    
    # 关系 - 使用正确的字符串引用方式
    user = relationship("User", foreign_keys=[user_id])

class UserActivityLog(NoUpdateBase):
    """用户活动日志模型"""
    __tablename__ = "user_activity_logs"
    
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False, index=True, comment='用户ID')
    action_type = Column(String(50), nullable=False, index=True, comment='操作类型')
    resource_type = Column(String(50), comment='资源类型')
    resource_id = Column(Integer, comment='资源ID')
    description = Column(Text, comment='操作描述')
    ip_address = Column(String(50), comment='IP地址')
    user_agent = Column(String(255), comment='用户代理')
    
    # 使用字符串引用避免循环导入
    user = relationship("User", foreign_keys=[user_id], backref="activity_logs") 