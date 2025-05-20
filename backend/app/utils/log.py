from typing import Optional
from datetime import datetime
from sqlalchemy.orm import Session

from app.models.operation_log import OperationLog

def log_operation(
    db: Session,
    user_id: int,
    operation_type: str,
    operation_content: str = None,
    ip_address: Optional[str] = None,
    operation_detail: str = None,
    user_agent: Optional[str] = None,
) -> OperationLog:
    """
    记录操作日志
    
    Args:
        db: 数据库会话
        user_id: 用户ID
        operation_type: 操作类型
        operation_content: 操作内容
        ip_address: IP地址
        operation_detail: 操作详情（已弃用，请使用operation_content）
        user_agent: 用户代理（已弃用）
        
    Returns:
        创建的日志记录
    """
    if operation_content is None and operation_detail is not None:
        operation_content = operation_detail
    
    log = OperationLog(
        user_id=user_id,
        operation_type=operation_type,
        operation_content=operation_content,
        ip_address=ip_address,
        operation_time=datetime.now(),
    )
    
    db.add(log)
    db.commit()
    db.refresh(log)
    
    return log 