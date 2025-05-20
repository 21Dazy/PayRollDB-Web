from sqlalchemy import Column, Integer, Date, ForeignKey, DECIMAL, String, UniqueConstraint
from sqlalchemy.orm import relationship

from app.db.base_class import Base

class Attendance(Base):
    """考勤记录模型"""
    employee_id = Column(Integer, ForeignKey('employee.id'), nullable=False, index=True, comment='员工ID')
    date = Column(Date, nullable=False, comment='日期')
    status_id = Column(Integer, ForeignKey('attendance_status.id'), nullable=False, comment='出勤状态ID')
    overtime_hours = Column(DECIMAL(5, 2), default=0, comment='加班时长(小时)')
    remarks = Column(String(255), comment='备注')
    
    # 唯一约束，确保一个员工一天只有一条考勤记录
    __table_args__ = (
        UniqueConstraint('employee_id', 'date', name='uk_employee_date'),
    )
    
    # 关系
    employee = relationship("Employee", back_populates="attendances")
    status = relationship("AttendanceStatus", back_populates="attendances") 