from sqlalchemy import Column, Integer, ForeignKey, DECIMAL
from sqlalchemy.orm import relationship

from app.db.base_class import Base

class SalaryDetail(Base):
    """工资明细模型"""
    salary_id = Column(Integer, ForeignKey('salary_record.id', ondelete='CASCADE'), nullable=False, index=True, comment='工资记录ID')
    item_id = Column(Integer, ForeignKey('salary_item.id'), nullable=False, comment='工资项目ID')
    amount = Column(DECIMAL(10, 2), nullable=False, comment='金额')
    
    # 关系
    salary = relationship("SalaryRecord", back_populates="details")
    item = relationship("SalaryItem") 