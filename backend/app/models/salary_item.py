from sqlalchemy import Column, String, Enum, Boolean
from sqlalchemy.orm import relationship

from app.db.base_class import Base

class SalaryItem(Base):
    """工资组成项目模型"""
    __tablename__ = "salary_items"
    
    name = Column(String(50), nullable=False, comment='项目名称')
    type = Column(Enum('addition', 'deduction', name='salary_item_type'), nullable=False, comment='类型(addition:加项, deduction:减项)')
    is_percentage = Column(Boolean, default=False, comment='是否百分比(1:是, 0:否)')
    is_system = Column(Boolean, default=False, comment='是否系统项(1:是, 0:否)') 