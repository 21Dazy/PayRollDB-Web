from sqlalchemy import Column, String, Integer, ForeignKey, TIMESTAMP, DateTime, Text, func, Index
from sqlalchemy.orm import relationship

from app.db.base_class import NoUpdateBase

class OperationLog(NoUpdateBase):
    """操作日志模型"""
    __tablename__ = "operation_logs"
    
    user_id = Column(Integer, index=True, nullable=False, comment='用户ID')
    operation_type = Column(String(50), nullable=False, comment='操作类型')
    operation_content = Column(Text, comment='操作内容')
    ip_address = Column(String(50), comment='IP地址')
    operation_time = Column(DateTime, nullable=False, comment='操作时间')
    created_at = Column(TIMESTAMP, server_default=func.now(), comment='创建时间')
    
    __table_args__ = (
        Index('idx_user_id', user_id),
        Index('idx_operation_time', operation_time),
    ) 