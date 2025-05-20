from sqlalchemy import Column, String
from sqlalchemy.orm import relationship

from app.db.base_class import Base

class Department(Base):
    """部门模型"""
    __tablename__ = "departments"
    
    name = Column(String(50), nullable=False, comment='部门名称')
    description = Column(String(255), comment='部门描述')
    
    # 关系
    employees = relationship("Employee", back_populates="department") 