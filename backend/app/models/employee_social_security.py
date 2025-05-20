from sqlalchemy import Column, Integer, ForeignKey, DECIMAL, Date
from sqlalchemy.orm import relationship

from app.db.base_class import Base

class EmployeeSocialSecurity(Base):
    """员工社保公积金配置模型"""
    __tablename__ = "employee_social_security"
    
    employee_id = Column(Integer, ForeignKey('employees.id'), nullable=False, index=True, comment='员工ID')
    config_id = Column(Integer, ForeignKey('social_security_config.id'), nullable=False, comment='社保配置ID')
    base_number = Column(DECIMAL(10, 2), nullable=False, comment='社保基数')
    housing_fund_base = Column(DECIMAL(10, 2), nullable=False, comment='公积金基数')
    effective_date = Column(Date, nullable=False, comment='生效日期')
    
    # 关系
    employee = relationship("Employee", back_populates="social_security")
    config = relationship("SocialSecurityConfig", back_populates="employee_configs") 