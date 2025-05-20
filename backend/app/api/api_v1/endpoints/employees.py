from typing import Any, List, Optional
from datetime import date

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from sqlalchemy import or_

from app.api.deps import get_current_hr_user, get_current_user, get_db
from app.crud.crud_employee import employee
from app.models.user import User
from app.schemas.employee import (
    EmployeeCreate, EmployeeUpdate, EmployeeResponse, EmployeeDetailResponse,
    EmployeeLeaveRequest
)
from app.core.security import encrypt_bank_account
from app.utils.log import log_operation

router = APIRouter()

@router.get("/", response_model=List[EmployeeDetailResponse])
def read_employees(
    skip: int = 0,
    limit: int = 100,
    department_id: Optional[int] = None,
    position_id: Optional[int] = None,
    status: Optional[bool] = None,
    name: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Any:
    """
    获取员工列表
    """
    return employee.get_multi_with_filters(
        db, skip=skip, limit=limit, department_id=department_id,
        position_id=position_id, status=status, name=name
    )

@router.post("/", response_model=EmployeeResponse, status_code=status.HTTP_201_CREATED)
def create_employee(
    *,
    db: Session = Depends(get_db),
    employee_in: EmployeeCreate,
    current_user: User = Depends(get_current_hr_user)
) -> Any:
    """
    创建新员工
    """
    employee_obj = employee.create(db=db, obj_in=employee_in)
    log_operation(
        db=db,
        user_id=current_user.id,
        operation_type="创建员工",
        operation_detail=f"创建了员工: {employee_obj.name}, ID: {employee_obj.id}"
    )
    return employee_obj

@router.get("/{employee_id}", response_model=EmployeeDetailResponse)
def read_employee(
    employee_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Any:
    """
    获取特定员工详情
    """
    employee_obj = employee.get_with_relations(db, id=employee_id)
    if not employee_obj:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="员工不存在"
        )
    return employee_obj

@router.put("/{employee_id}", response_model=EmployeeResponse)
def update_employee(
    *,
    db: Session = Depends(get_db),
    employee_id: int,
    employee_in: EmployeeUpdate,
    current_user: User = Depends(get_current_hr_user)
) -> Any:
    """
    更新员工信息
    """
    employee_obj = employee.get(db, id=employee_id)
    if not employee_obj:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="员工不存在"
        )
    
    employee_obj = employee.update(db=db, db_obj=employee_obj, obj_in=employee_in)
    log_operation(
        db=db,
        user_id=current_user.id,
        operation_type="更新员工",
        operation_detail=f"更新了员工: {employee_obj.name}, ID: {employee_obj.id}"
    )
    return employee_obj

@router.put("/{employee_id}/leave", response_model=EmployeeResponse)
def leave_employee(
    *,
    db: Session = Depends(get_db),
    employee_id: int,
    leave_data: EmployeeLeaveRequest,
    current_user: User = Depends(get_current_hr_user)
) -> Any:
    """
    设置员工离职状态
    """
    employee_obj = employee.get(db, id=employee_id)
    if not employee_obj:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="员工不存在"
        )
    
    # 更新员工状态为离职
    employee_update = EmployeeUpdate(status=False)
    employee_obj = employee.update(db=db, db_obj=employee_obj, obj_in=employee_update)
    
    log_operation(
        db=db,
        user_id=current_user.id,
        operation_type="员工离职",
        operation_detail=f"设置员工: {employee_obj.name}, ID: {employee_obj.id} 为离职状态，离职日期: {leave_data.leave_date}"
    )
    return employee_obj

@router.get("/{employee_id}/salaries", response_model=List)
def read_employee_salaries(
    employee_id: int,
    year: Optional[int] = None,
    month: Optional[int] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Any:
    """
    获取特定员工的工资记录
    """
    # 检查是否有权限查看（HR、管理员或本人）
    if current_user.role not in ["admin", "hr"] and current_user.employee_id != employee_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="没有权限查看该员工的工资记录"
        )

    # 获取员工工资记录
    employee_obj = employee.get(db, id=employee_id)
    if not employee_obj:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="员工不存在"
        )
    
    # 使用筛选条件获取工资记录
    # 这里需要实现工资记录的获取逻辑
    return []

@router.get("/{employee_id}/attendance", response_model=List)
def read_employee_attendance(
    employee_id: int,
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Any:
    """
    获取特定员工的考勤记录
    """
    # 检查是否有权限查看（HR、管理员或本人）
    if current_user.role not in ["admin", "hr"] and current_user.employee_id != employee_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="没有权限查看该员工的考勤记录"
        )

    # 获取员工考勤记录
    employee_obj = employee.get(db, id=employee_id)
    if not employee_obj:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="员工不存在"
        )
    
    # 使用筛选条件获取考勤记录
    # 这里需要实现考勤记录的获取逻辑
    return [] 