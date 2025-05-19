from typing import Any, List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.api.deps import get_current_hr_user, get_current_user, get_db
from app.models.user import User
from app.models.department import Department
from app.models.employee import Employee
from app.schemas.department import (
    DepartmentCreate, DepartmentUpdate, DepartmentResponse,
    DepartmentWithEmployeeCount
)
from app.utils.log import log_operation

router = APIRouter()

@router.get("/", response_model=List[DepartmentResponse])
def read_departments(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Any:
    """
    获取所有部门列表
    """
    departments = db.query(Department).offset(skip).limit(limit).all()
    return departments

@router.get("/with-employee-count", response_model=List[DepartmentWithEmployeeCount])
def read_departments_with_count(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Any:
    """
    获取部门列表及各部门员工数量
    """
    departments_with_count = (
        db.query(
            Department,
            func.count(Employee.id).label("employee_count")
        )
        .outerjoin(Employee, Department.id == Employee.department_id)
        .group_by(Department.id)
        .all()
    )
    
    result = []
    for dept, count in departments_with_count:
        dept_dict = {
            "id": dept.id,
            "name": dept.name,
            "description": dept.description,
            "created_at": dept.created_at,
            "updated_at": dept.updated_at,
            "employee_count": count
        }
        result.append(dept_dict)
    
    return result

@router.post("/", response_model=DepartmentResponse, status_code=status.HTTP_201_CREATED)
def create_department(
    *,
    db: Session = Depends(get_db),
    department_in: DepartmentCreate,
    current_user: User = Depends(get_current_hr_user)
) -> Any:
    """
    创建新部门（需要HR或管理员权限）
    """
    department = Department(
        name=department_in.name,
        description=department_in.description
    )
    db.add(department)
    db.commit()
    db.refresh(department)
    
    # 记录操作日志
    log_operation(
        db=db,
        user_id=current_user.id,
        operation_type="创建部门",
        operation_content=f"创建了部门: {department.name}"
    )
    
    return department

@router.get("/{department_id}", response_model=DepartmentResponse)
def read_department(
    *,
    db: Session = Depends(get_db),
    department_id: int,
    current_user: User = Depends(get_current_user)
) -> Any:
    """
    获取特定部门详情
    """
    department = db.query(Department).filter(Department.id == department_id).first()
    if not department:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="部门不存在"
        )
    return department

@router.put("/{department_id}", response_model=DepartmentResponse)
def update_department(
    *,
    db: Session = Depends(get_db),
    department_id: int,
    department_in: DepartmentUpdate,
    current_user: User = Depends(get_current_hr_user)
) -> Any:
    """
    更新部门信息（需要HR或管理员权限）
    """
    department = db.query(Department).filter(Department.id == department_id).first()
    if not department:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="部门不存在"
        )
    
    update_data = department_in.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(department, field, value)
    
    db.commit()
    db.refresh(department)
    
    # 记录操作日志
    log_operation(
        db=db,
        user_id=current_user.id,
        operation_type="更新部门",
        operation_content=f"更新了部门: {department.name}"
    )
    
    return department

@router.delete("/{department_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_department(
    *,
    db: Session = Depends(get_db),
    department_id: int,
    current_user: User = Depends(get_current_hr_user)
) -> Any:
    """
    删除部门（需要HR或管理员权限）
    
    注意：如果部门下有员工，将无法删除
    """
    department = db.query(Department).filter(Department.id == department_id).first()
    if not department:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="部门不存在"
        )
    
    # 检查部门是否有员工
    employee_count = db.query(Employee).filter(Employee.department_id == department_id).count()
    if employee_count > 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"部门下有{employee_count}名员工，无法删除"
        )
    
    # 记录操作日志
    log_operation(
        db=db,
        user_id=current_user.id,
        operation_type="删除部门",
        operation_content=f"删除了部门: {department.name}"
    )
    
    db.delete(department)
    db.commit()
    
    return None 