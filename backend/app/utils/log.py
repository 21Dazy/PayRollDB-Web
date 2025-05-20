from typing import Optional
from sqlalchemy.orm import Session

from app.models.operation_log import OperationLog

def log_operation(
    db: Session,
    user_id: int,
    operation_type: str,
    operation_detail: str,
    ip_address: Optional[str] = None,
    user_agent: Optional[str] = None,
) -> OperationLog:
    """
    记录操作日志
    
    Args:
        db: 数据库会话
        user_id: 用户ID
        operation_type: 操作类型
        operation_detail: 操作详情
        ip_address: IP地址
        user_agent: 用户代理
        
    Returns:
        创建的日志记录
    """
    log = OperationLog(
        user_id=user_id,
        operation_type=operation_type,
        operation_detail=operation_detail,
        ip_address=ip_address,
        user_agent=user_agent,
    )
    
    db.add(log)
    db.commit()
    db.refresh(log)
    
    return log 