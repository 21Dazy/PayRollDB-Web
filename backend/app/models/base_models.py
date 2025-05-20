"""
基础模型定义
只包含表结构，不包含关系定义，避免循环引用问题
"""
from sqlalchemy import Column, String, Integer, ForeignKey, DateTime, Boolean, Enum, DECIMAL, Date, TIMESTAMP, Text, UniqueConstraint, func, VARBINARY
from app.db.base_class import Base

# 部门模型
class Department(Base):
    """部门模型"""
    name = Column(String(50), nullable=False, comment='部门名称')
    description = Column(String(255), comment='部门描述')

# 职位模型
class Position(Base):
    """职位模型"""
    name = Column(String(50), nullable=False, comment='职位名称')
    description = Column(String(255), comment='职位描述')

# 员工模型
class Employee(Base):
    """员工模型"""
    name = Column(String(50), nullable=False, comment='姓名')
    department_id = Column(Integer, ForeignKey('department.id'), nullable=False, index=True, comment='部门ID')
    position_id = Column(Integer, ForeignKey('position.id'), nullable=False, index=True, comment='职位ID')
    base_salary = Column(DECIMAL(10, 2), nullable=False, comment='基本工资')
    hire_date = Column(Date, nullable=False, comment='入职日期')
    phone = Column(String(20), comment='联系电话')
    email = Column(String(100), comment='电子邮箱')
    address = Column(String(255), comment='地址')
    id_card = Column(String(18), comment='身份证号')
    bank_name = Column(String(100), comment='开户行')
    bank_account = Column(String(100), comment='银行账号')
    bank_account_encrypted = Column(VARBINARY(255), comment='加密后的银行账号')
    status = Column(Boolean, default=True, index=True, comment='状态(1:在职, 0:离职)')

# 用户模型
class User(Base):
    """用户模型"""
    username = Column(String(50), unique=True, nullable=False, index=True, comment='用户名')
    hashed_password = Column(String(255), nullable=False, comment='密码(加密存储)')
    employee_id = Column(Integer, ForeignKey('employee.id', ondelete="SET NULL"), nullable=True, comment='关联员工ID')
    role = Column(
        Enum('admin', 'hr', 'manager', 'employee', name='user_role'), 
        nullable=False, 
        comment='角色'
    )
    is_active = Column(Boolean, default=True, comment='是否激活(1:是, 0:否)')
    last_login = Column(DateTime, comment='上次登录时间')

# 操作日志模型
class OperationLog(Base):
    """操作日志模型"""
    user_id = Column(Integer, ForeignKey('user.id'), nullable=False, index=True, comment='用户ID')
    operation_type = Column(String(50), nullable=False, comment='操作类型')
    operation_detail = Column(String(255), nullable=False, comment='操作详情')
    ip_address = Column(String(50), comment='IP地址')
    user_agent = Column(String(255), comment='用户代理')
    created_at = Column(TIMESTAMP, server_default=func.now(), comment='创建时间') 