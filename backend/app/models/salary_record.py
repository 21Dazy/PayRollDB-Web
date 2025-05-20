from sqlalchemy import Column, Integer, ForeignKey, DECIMAL, Enum, DateTime, String, UniqueConstraint
from sqlalchemy.orm import relationship

from app.db.base_class import Base

class SalaryRecord(Base):
    """工资记录模型"""
    __tablename__ = "salary_records"
    
    employee_id = Column(Integer, ForeignKey('employees.id'), nullable=False, index=True, comment='员工ID')
    year = Column(Integer, nullable=False, comment='年份')
    month = Column(Integer, nullable=False, comment='月份')
    base_salary = Column(DECIMAL(10, 2), nullable=False, comment='基本工资')
    overtime_pay = Column(DECIMAL(10, 2), default=0, comment='加班费')
    bonus = Column(DECIMAL(10, 2), default=0, comment='奖金')
    deduction = Column(DECIMAL(10, 2), default=0, comment='扣款')
    social_security = Column(DECIMAL(10, 2), default=0, comment='社保公积金')
    personal_tax = Column(DECIMAL(10, 2), default=0, comment='个人所得税')
    net_salary = Column(DECIMAL(10, 2), nullable=False, comment='实发工资')
    status = Column(Enum('pending', 'paid', name='salary_status'), default='pending', index=True, comment='发放状态')
    payment_date = Column(DateTime, comment='发放日期')
    remark = Column(String(255), comment='备注')
    
    # 唯一约束，确保一个员工一个月只有一条工资记录
    __table_args__ = (
        UniqueConstraint('employee_id', 'year', 'month', name='uk_employee_year_month'),
    )
    
    # 关系
    employee = relationship("Employee", back_populates="salary_records")
    details = relationship("SalaryDetail", back_populates="salary", cascade="all, delete-orphan") 