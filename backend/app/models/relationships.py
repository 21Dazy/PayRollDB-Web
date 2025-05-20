"""
此文件用于在所有模型初始化后设置关系，避免循环引用问题
"""
from sqlalchemy.orm import relationship
from sqlalchemy import Integer

from app.models.user import User
from app.models.operation_log import OperationLog

# 设置User和OperationLog之间的关系，使用primaryjoin参数明确指定连接条件
User.operation_logs = relationship(
    "OperationLog",
    primaryjoin="User.id == OperationLog.user_id",
    foreign_keys="OperationLog.user_id",
    backref="user"
) 