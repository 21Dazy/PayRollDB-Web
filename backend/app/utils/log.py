from typing import Optional
from datetime import datetime
from sqlalchemy.orm import Session

from app.models.operation_log import OperationLog

def log_operation(
    db: Session,
    user_id: int,
    operation_type: str,
    operation_content: str,
    ip_address: Optional[str] = None
) -> OperationLog:
    """
    记录用户操作日志
    
    参数:
    - db: 数据库会话
    - user_id: 用户ID
    - operation_type: 操作类型
    - operation_content: 操作内容
    - ip_address: IP地址，可选
    
    返回:
    - 创建的日志记录
    """
    log = OperationLog(
        user_id=user_id,
        operation_type=operation_type,
        operation_content=operation_content,
        ip_address=ip_address,
        operation_time=datetime.now()
    )
    db.add(log)
    db.commit()
    db.refresh(log)
    return log 