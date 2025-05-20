from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Boolean, Enum
from sqlalchemy.orm import relationship

from app.db.base_class import Base

class User(Base):
    """用户模型"""
    __tablename__ = "users"
    
    username = Column(String(50), unique=True, nullable=False, index=True, comment='用户名')
    password = Column(String(255), nullable=False, comment='密码(加密存储)')
    employee_id = Column(Integer, ForeignKey('employees.id', ondelete="SET NULL"), nullable=True, comment='关联员工ID')
    role = Column(
        Enum('admin', 'hr', 'manager', 'employee', name='user_role'), 
        nullable=False, 
        index=True,
        comment='角色'
    )
    is_active = Column(Boolean, default=True, index=True, comment='是否激活(1:是, 0:否)')
    last_login = Column(DateTime, comment='上次登录时间')
    
    # 关系
    employee = relationship("Employee", foreign_keys=[employee_id], back_populates="user") 