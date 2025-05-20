from sqlalchemy import Column, String, DECIMAL, Boolean
from sqlalchemy.orm import relationship

from app.db.base_class import Base

class SocialSecurityConfig(Base):
    """社保公积金配置模型"""
    __tablename__ = "social_security_config"
    
    name = Column(String(50), nullable=False, comment='配置名称')
    pension_rate = Column(DECIMAL(5, 2), nullable=False, comment='养老保险比例')
    medical_rate = Column(DECIMAL(5, 2), nullable=False, comment='医疗保险比例')
    unemployment_rate = Column(DECIMAL(5, 2), nullable=False, comment='失业保险比例')
    injury_rate = Column(DECIMAL(5, 2), nullable=False, comment='工伤保险比例')
    maternity_rate = Column(DECIMAL(5, 2), nullable=False, comment='生育保险比例')
    housing_fund_rate = Column(DECIMAL(5, 2), nullable=False, comment='住房公积金比例')
    is_default = Column(Boolean, default=False, comment='是否默认(1:是, 0:否)')
    
    # 关系
    employee_configs = relationship("EmployeeSocialSecurity", back_populates="config") 