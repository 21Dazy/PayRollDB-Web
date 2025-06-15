from sqlalchemy import Column, String, Integer, ForeignKey
from sqlalchemy.orm import relationship

from app.db.base_class import Base

class Position(Base):
    """职位模型"""
    __tablename__ = "positions"
    
    name = Column(String(50), nullable=False, comment='职位名称')
    department_id = Column(Integer, ForeignKey('departments.id'), nullable=False, index=True, comment='所属部门ID')
    description = Column(String(255), comment='职位描述')
    
    # 关系
    department = relationship("Department", back_populates="positions")
    employees = relationship("Employee", back_populates="position") 