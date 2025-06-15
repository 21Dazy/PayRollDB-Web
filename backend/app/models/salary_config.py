from sqlalchemy import Column, Integer, String, DECIMAL, Date, ForeignKey, Boolean, UniqueConstraint
from sqlalchemy.orm import relationship
from app.db.base_class import Base

class EmployeeSalaryConfig(Base):
    """员工薪资配置模型"""
    __tablename__ = "employee_salary_config"
    
    id = Column(Integer, primary_key=True, index=True)
    employee_id = Column(Integer, ForeignKey("employees.id"), nullable=False, comment="员工ID")
    item_id = Column(Integer, ForeignKey("salary_items.id"), nullable=False, comment="薪资项目ID")
    value = Column(DECIMAL(10, 2), nullable=False, comment="金额或百分比值")
    base_item = Column(String(50), comment="基准项目(用于百分比计算)")
    is_active = Column(Boolean, default=True, comment="是否启用")
    effective_date = Column(Date, nullable=False, comment="生效日期")
    expiry_date = Column(Date, comment="失效日期")
    
    # 关系
    employee = relationship("Employee", back_populates="salary_configs")
    salary_item = relationship("SalaryItem", back_populates="employee_configs")
    
    # 添加唯一约束
    __table_args__ = (
        UniqueConstraint('employee_id', 'item_id', 'effective_date', name='uk_employee_item_date'),
    ) 