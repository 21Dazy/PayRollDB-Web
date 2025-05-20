from sqlalchemy import Column, String, Integer, DECIMAL, Date, ForeignKey, VARBINARY, Boolean
from sqlalchemy.orm import relationship

from app.db.base_class import Base

class Employee(Base):
    """员工模型"""
    __tablename__ = "employees"
    
    name = Column(String(50), nullable=False, comment='姓名')
    department_id = Column(Integer, ForeignKey('departments.id'), nullable=False, index=True, comment='部门ID')
    position_id = Column(Integer, ForeignKey('positions.id'), nullable=False, index=True, comment='职位ID')
    base_salary = Column(DECIMAL(10, 2), nullable=False, comment='基本工资')
    hire_date = Column(Date, nullable=False, comment='入职日期')
    phone = Column(String(20), comment='联系电话')
    email = Column(String(100), comment='电子邮箱')
    address = Column(String(255), comment='地址')
    id_card = Column(String(18), comment='身份证号')
    bank_name = Column(String(100), comment='开户行')
    bank_account = Column(String(100), comment='银行账号')
    bank_account_encrypted = Column(VARBINARY(255), comment='加密后的银行账号')
    status = Column(Boolean, default=True, index=True, comment='状态(1:在职, 0:离职)')
    
    # 关系
    department = relationship("Department", back_populates="employees")
    position = relationship("Position", back_populates="employees")
    user = relationship("User", back_populates="employee", uselist=False, primaryjoin="Employee.id == User.employee_id")
    attendances = relationship("Attendance", back_populates="employee")
    salary_records = relationship("SalaryRecord", back_populates="employee")
    social_security = relationship("EmployeeSocialSecurity", back_populates="employee") 