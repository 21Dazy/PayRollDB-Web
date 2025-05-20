from sqlalchemy import Column, String
from sqlalchemy.orm import relationship

from app.db.base_class import Base

class Position(Base):
    """职位模型"""
    __tablename__ = "positions"
    
    name = Column(String(50), nullable=False, comment='职位名称')
    description = Column(String(255), comment='职位描述')
    
    # 关系
    employees = relationship("Employee", back_populates="position") 