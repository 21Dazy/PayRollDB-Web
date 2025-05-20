from typing import Any
from sqlalchemy.ext.declarative import declared_attr
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy import Column, Integer, TIMESTAMP, func

class Base(DeclarativeBase):
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    created_at = Column(TIMESTAMP, server_default=func.current_timestamp())
    updated_at = Column(
        TIMESTAMP, 
        server_default=func.current_timestamp(),
        onupdate=func.current_timestamp()
    )
    
    # 根据类名生成表名
    @declared_attr
    def __tablename__(cls) -> str:
        # 直接使用类名的小写形式作为表名，而不是自动转为复数
        # 具体的表名应该在模型类中显式指定，以匹配SQL脚本
        return cls.__name__.lower()

class NoUpdateBase(DeclarativeBase):
    """没有updated_at字段的基类，用于那些在数据库中没有updated_at字段的表"""
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    created_at = Column(TIMESTAMP, server_default=func.current_timestamp())
    
    # 根据类名生成表名
    @declared_attr
    def __tablename__(cls) -> str:
        # 直接使用类名的小写形式作为表名
        # 具体的表名应该在模型类中显式指定，以匹配SQL脚本
        return cls.__name__.lower() 