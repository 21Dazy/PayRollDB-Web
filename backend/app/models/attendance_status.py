from sqlalchemy import Column, String, Boolean, DECIMAL
from sqlalchemy.orm import relationship

from app.db.base_class import Base

class AttendanceStatus(Base):
    """考勤状态模型"""
    name = Column(String(20), nullable=False, comment='状态名称')
    description = Column(String(100), comment='状态描述')
    is_deduction = Column(Boolean, default=False, comment='是否扣款(1:是, 0:否)')
    deduction_value = Column(DECIMAL(10, 2), default=0, comment='扣款金额或比例')
    
    # 关系
    attendances = relationship("Attendance", back_populates="status") 