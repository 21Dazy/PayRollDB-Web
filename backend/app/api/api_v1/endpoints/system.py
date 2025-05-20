from typing import Any, List, Optional
from datetime import datetime, timedelta

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from sqlalchemy import func, desc

from app.api.deps import get_current_admin, get_current_user, get_db
from app.models.user import User
from app.models.system_parameter import SystemParameter
from app.models.operation_log import OperationLog
from app.models.employee import Employee
from app.schemas.system import (
    SystemParameterCreate, SystemParameterUpdate, SystemParameterResponse,
    OperationLogResponse, SystemStatusResponse
)
from app.utils.log import log_operation
from app.core.config import settings

router = APIRouter()

# 系统参数相关接口
@router.get("/parameters", response_model=List[SystemParameterResponse])
def read_system_parameters(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Any:
    """
    获取系统参数列表
    """
    return db.query(SystemParameter).offset(skip).limit(limit).all()

@router.post("/parameters", response_model=SystemParameterResponse, status_code=status.HTTP_201_CREATED)
def create_system_parameter(
    *,
    db: Session = Depends(get_db),
    parameter_in: SystemParameterCreate,
    current_user: User = Depends(get_current_admin)
) -> Any:
    """
    创建系统参数
    """
    # 检查参数键是否已存在
    existing = db.query(SystemParameter).filter(SystemParameter.param_key == parameter_in.param_key).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="参数键已存在"
        )
    
    parameter = SystemParameter(**parameter_in.dict())
    db.add(parameter)
    db.commit()
    db.refresh(parameter)
    
    log_operation(
        db=db,
        user_id=current_user.id,
        operation_type="创建系统参数",
        operation_detail=f"创建了系统参数: {parameter.param_key}"
    )
    
    return parameter

@router.put("/parameters/{param_id}", response_model=SystemParameterResponse)
def update_system_parameter(
    *,
    db: Session = Depends(get_db),
    param_id: int,
    parameter_in: SystemParameterUpdate,
    current_user: User = Depends(get_current_admin)
) -> Any:
    """
    更新系统参数
    """
    parameter = db.query(SystemParameter).filter(SystemParameter.id == param_id).first()
    if not parameter:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="系统参数不存在"
        )
    
    update_data = parameter_in.dict(exclude_unset=True)
    
    for key, value in update_data.items():
        setattr(parameter, key, value)
    
    db.add(parameter)
    db.commit()
    db.refresh(parameter)
    
    log_operation(
        db=db,
        user_id=current_user.id,
        operation_type="更新系统参数",
        operation_detail=f"更新了系统参数: {parameter.param_key}"
    )
    
    return parameter

@router.delete("/parameters/{param_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_system_parameter(
    *,
    db: Session = Depends(get_db),
    param_id: int,
    current_user: User = Depends(get_current_admin)
) -> None:
    """
    删除系统参数
    """
    parameter = db.query(SystemParameter).filter(SystemParameter.id == param_id).first()
    if not parameter:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="系统参数不存在"
        )
    
    param_key = parameter.param_key
    
    db.delete(parameter)
    db.commit()
    
    log_operation(
        db=db,
        user_id=current_user.id,
        operation_type="删除系统参数",
        operation_detail=f"删除了系统参数: {param_key}"
    )
    
    return None

# 操作日志相关接口
@router.get("/logs", response_model=List[OperationLogResponse])
def read_operation_logs(
    skip: int = 0,
    limit: int = 100,
    user_id: Optional[int] = None,
    operation_type: Optional[str] = None,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin)
) -> Any:
    """
    获取操作日志列表
    """
    query = db.query(OperationLog).join(User, OperationLog.user_id == User.id)
    
    # 应用筛选条件
    if user_id is not None:
        query = query.filter(OperationLog.user_id == user_id)
    
    if operation_type:
        query = query.filter(OperationLog.operation_type == operation_type)
    
    if start_date:
        query = query.filter(OperationLog.created_at >= start_date)
    
    if end_date:
        query = query.filter(OperationLog.created_at <= end_date)
    
    # 按创建时间降序排序
    query = query.order_by(desc(OperationLog.created_at))
    
    return query.offset(skip).limit(limit).all()

@router.get("/status", response_model=SystemStatusResponse)
def get_system_status(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin)
) -> Any:
    """
    获取系统状态信息
    """
    # 获取用户总数
    total_users = db.query(func.count(User.id)).scalar()
    
    # 获取员工总数
    total_employees = db.query(func.count(Employee.id)).scalar()
    
    # 简化的系统状态信息
    uptime = "1小时23分钟"  # 实际应该通过查询系统启动时间计算
    
    return {
        "status": "运行中",
        "uptime": uptime,
        "db_status": "正常",
        "total_users": total_users,
        "total_employees": total_employees,
        "version": settings.VERSION
    } 