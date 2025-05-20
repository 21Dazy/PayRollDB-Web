from sqlalchemy import Column, String, UniqueConstraint

from app.db.base_class import Base

class SystemParameter(Base):
    """系统参数模型"""
    __tablename__ = "system_parameters"
    
    param_key = Column(String(50), nullable=False, unique=True, comment='参数键')
    param_value = Column(String(255), nullable=False, comment='参数值')
    description = Column(String(255), comment='参数描述') 