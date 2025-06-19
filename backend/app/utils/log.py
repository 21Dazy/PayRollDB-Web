from typing import Optional
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import text

def log_operation(
    db: Session,
    user_id: int,
    operation_type: str,
    operation_content: str = None,
    ip_address: Optional[str] = None,
    operation_detail: str = None,
    user_agent: Optional[str] = None,
) -> None:
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
    """
    if operation_content is None and operation_detail is not None:
        operation_content = operation_detail
    
    # 使用原生SQL插入日志，避免模型类导入问题
    sql = """
    INSERT INTO operation_logs 
    (user_id, operation_type, operation_content, ip_address, operation_time, created_at)
    VALUES (:user_id, :operation_type, :operation_content, :ip_address, :operation_time, :created_at)
    """
    
    try:
        now = datetime.now()
        db.execute(
            text(sql),
            {
                "user_id": user_id,
                "operation_type": operation_type,
                "operation_content": operation_content,
                "ip_address": ip_address,
                "operation_time": now,
                "created_at": now
            }
        )
        db.commit()
    except Exception as e:
        db.rollback()
        print(f"记录操作日志失败: {str(e)}")
        # 不抛出异常，避免影响主流程 