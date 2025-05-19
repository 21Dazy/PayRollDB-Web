from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Text
from sqlalchemy.orm import relationship

from app.db.base_class import Base

class OperationLog(Base):
    """操作日志模型"""
    user_id = Column(Integer, ForeignKey('user.id'), nullable=False, index=True, comment='用户ID')
    operation_type = Column(String(50), nullable=False, comment='操作类型')
    operation_content = Column(Text, comment='操作内容')
    ip_address = Column(String(50), comment='IP地址')
    operation_time = Column(DateTime, nullable=False, index=True, comment='操作时间')
    
    # 关系
    user = relationship("User", back_populates="operation_logs") 