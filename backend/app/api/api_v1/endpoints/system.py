from typing import Any, List, Optional
from datetime import datetime, timedelta
from decimal import Decimal

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from sqlalchemy import func, desc

from app.api.deps import get_current_admin, get_current_user, get_db
from app.models.user import User
from app.models.system_parameter import SystemParameter
from app.models.operation_log import OperationLog
from app.models.employee import Employee
from app.models.department import Department
from app.models.salary_record import SalaryRecord
from app.models.attendance import Attendance
from app.models.attendance_status import AttendanceStatus
from app.schemas.system import (
    SystemParameterCreate, SystemParameterUpdate, SystemParameterResponse,
    OperationLogResponse, SystemStatusResponse, SystemOverviewResponse
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

@router.get("/health", response_model=dict)
def health_check() -> Any:
    """
    系统健康检查接口，不需要认证
    前端可以用来检查系统是否在线和API可用性
    """
    return {
        "status": "ok",
        "message": "系统正常运行",
        "timestamp": datetime.now().isoformat(),
        "version": settings.VERSION
    }

@router.get("/overview", response_model=SystemOverviewResponse)
def get_system_overview(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Any:
    """
    获取系统概览数据，用于Dashboard展示
    """
    # 1. 获取员工总数
    employee_count = db.query(func.count(Employee.id)).scalar() or 0
    
    # 2. 获取部门数据
    departments_with_count = (
        db.query(
            Department.name,
            func.count(Employee.id).label("value")
        )
        .outerjoin(Employee, Department.id == Employee.department_id)
        .group_by(Department.id, Department.name)
        .all()
    )
    
    department_data = [
        {"name": dept_name, "value": count or 0} 
        for dept_name, count in departments_with_count
    ]
    
    # 3. 获取薪资总额 - 从最近的工资记录中计算
    from sqlalchemy import desc
    from app.models.salary_record import SalaryRecord
    
    current_month = datetime.now().month
    current_year = datetime.now().year
    
    # 获取最近6个月的工资数据
    months = []
    basic_salary = []
    performance_pay = []
    bonus_pay = []
    allowance_pay = []
    
    for i in range(5, -1, -1):
        # 计算月份
        month = current_month - i
        year = current_year
        if month <= 0:
            month += 12
            year -= 1
        
        # 添加月份标签
        months.append(f"{month}月")
        
        # 查询该月的工资数据
        month_salary = (
            db.query(
                func.sum(SalaryRecord.base_salary).label("base"),
                func.sum(SalaryRecord.bonus).label("bonus")
            )
            .filter(SalaryRecord.year == year, SalaryRecord.month == month)
            .first()
        )
        
        base_value = month_salary.base or 0
        bonus_value = month_salary.bonus or 0
        
        basic_salary.append(float(base_value))
        # 先转换为Decimal计算，再转为float
        performance_pay.append(float(base_value * Decimal('0.2') if base_value else 0))  # 假设绩效是基本工资的20%
        bonus_pay.append(float(bonus_value))
        allowance_pay.append(float(base_value * Decimal('0.1') if base_value else 0))  # 假设补贴是基本工资的10%
    
    # 计算当前月的工资总额
    total_salary = (
        db.query(func.sum(SalaryRecord.net_salary))
        .filter(SalaryRecord.year == current_year, SalaryRecord.month == current_month)
        .scalar() or 0
    )
    
    # 4. 获取考勤问题数量
    from app.models.attendance import Attendance
    from app.models.attendance_status import AttendanceStatus
    
    # 获取当月异常考勤记录数(非"正常"状态)
    attendance_issues = (
        db.query(func.count(Attendance.id))
        .join(AttendanceStatus, Attendance.status_id == AttendanceStatus.id)
        .filter(
            AttendanceStatus.name != "正常",
            func.extract('year', Attendance.date) == current_year,
            func.extract('month', Attendance.date) == current_month
        )
        .scalar() or 0
    )
    
    # 5. 获取待审批的数量 (未发放的工资记录)
    pending_approvals = (
        db.query(func.count(SalaryRecord.id))
        .filter(
            SalaryRecord.status == "pending",
            SalaryRecord.year == current_year,
            SalaryRecord.month == current_month
        )
        .scalar() or 0
    )
    
    # 构建并返回响应
    return {
        "employee_count": employee_count,
        "total_salary": float(total_salary),
        "attendance_issues": attendance_issues,
        "pending_approvals": pending_approvals,
        "department_data": department_data,
        "salary_data": {
            "months": months,
            "basic": basic_salary,
            "performance": performance_pay,
            "bonus": bonus_pay,
            "allowance": allowance_pay
        }
    } 