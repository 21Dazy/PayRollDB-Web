from sqlalchemy import Column, String, Integer, ForeignKey, TIMESTAMP, func
from sqlalchemy.orm import relationship

from app.db.base_class import Base

class OperationLog(Base):
    """操作日志模型"""
    user_id = Column(Integer, ForeignKey('user.id'), nullable=False, index=True, comment='用户ID')
    operation_type = Column(String(50), nullable=False, comment='操作类型')
    operation_detail = Column(String(255), nullable=False, comment='操作详情')
    ip_address = Column(String(50), comment='IP地址')
    user_agent = Column(String(255), comment='用户代理')
    created_at = Column(TIMESTAMP, server_default=func.now(), comment='创建时间')
    
    # 使用字符串表示类名延迟加载避免循环引用
    user = relationship("User", back_populates="operation_logs") 