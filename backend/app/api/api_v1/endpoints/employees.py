from typing import Any, List, Optional
from datetime import date

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from sqlalchemy import or_, String, cast

from app.api.deps import get_current_hr_user, get_current_user, get_db
from app.crud.crud_employee import employee
from app.models.user import User
from app.models.department import Department
from app.models.position import Position
from app.schemas.employee import (
    EmployeeCreate, EmployeeUpdate, EmployeeResponse, EmployeeDetailResponse,
    EmployeeLeaveRequest, EmployeeSearchResponse
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

@router.get("/search", response_model=List[EmployeeSearchResponse])
def search_employees(
    keyword: Optional[str] = None,
    department_id: Optional[int] = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Any:
    """
    搜索员工，支持关键词搜索和部门筛选
    """
    # 添加调试日志
    print(f"搜索参数 - keyword: {keyword}, department_id: {department_id}, skip: {skip}, limit: {limit}")
    
    # 执行数据库查询，获取符合条件的员工列表
    employees_query = db.query(employee.model)
    
    # 应用部门筛选
    if department_id is not None:
        print(f"应用部门筛选: department_id = {department_id}")
        employees_query = employees_query.filter(employee.model.department_id == department_id)
    
    # 应用关键词搜索
    if keyword:
        print(f"应用关键词搜索: keyword = {keyword}")
        employees_query = employees_query.filter(
            or_(
                employee.model.name.ilike(f"%{keyword}%"),  # 姓名匹配
                cast(employee.model.id, String).ilike(f"%{keyword}%"),  # 将ID转为字符串进行匹配
                employee.model.phone.ilike(f"%{keyword}%"),  # 电话匹配
                employee.model.email.ilike(f"%{keyword}%") if employee.model.email is not None else False  # 邮箱匹配
            )
        )
    
    # 默认只返回在职员工
    employees_query = employees_query.filter(employee.model.status == True)
    
    # 先测试不用join，看看基本查询是否正确
    employees_list = (
        employees_query
        .offset(skip)
        .limit(limit)
        .all()
    )
    
    print(f"查询到 {len(employees_list)} 个员工")
    
    # 手动构建响应数据，手动获取关联的部门和职位信息
    response_results = []
    for emp in employees_list:
        # 手动查询部门和职位信息
        dept = db.query(Department).filter(Department.id == emp.department_id).first()
        pos = db.query(Position).filter(Position.id == emp.position_id).first()
        
        response_item = {
            "id": emp.id,
            "employee_id": str(emp.id),  # 使用id作为员工工号
            "name": emp.name,
            "department_id": emp.department_id,
            "department_name": dept.name if dept else "",
            "position_id": emp.position_id,
            "position_name": pos.name if pos else "",
            "base_salary": emp.base_salary,
            "hire_date": emp.hire_date,
            "status": emp.status,
            "phone": emp.phone,
            "email": emp.email,
            "bank_name": emp.bank_name,
            "bank_account": emp.bank_account
        }
        response_results.append(response_item)
        print(f"员工: {emp.name}, 部门ID: {emp.department_id}, 部门名称: {dept.name if dept else 'N/A'}")
    
    return response_results

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
    # 先检查数据库中是否存在该用户ID
    user = db.query(User).filter(User.id == current_user.id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="当前用户ID在数据库中不存在"
        )
    
    # 创建员工
    employee_obj = employee.create(db=db, obj_in=employee_in)
    
    try:
        # 记录操作日志
        log_operation(
            db=db,
            user_id=current_user.id,
            operation_type="创建员工",
            operation_detail=f"创建了员工: {employee_obj.name}, ID: {employee_obj.id}"
        )
    except Exception as e:
        # 如果记录日志失败，记录错误但不影响员工创建
        print(f"记录操作日志失败: {str(e)}")
    
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
    # 先检查数据库中是否存在该用户ID
    user = db.query(User).filter(User.id == current_user.id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="当前用户ID在数据库中不存在"
        )
    
    employee_obj = employee.get(db, id=employee_id)
    if not employee_obj:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="员工不存在"
        )
    
    employee_obj = employee.update(db=db, db_obj=employee_obj, obj_in=employee_in)
    
    try:
        log_operation(
            db=db,
            user_id=current_user.id,
            operation_type="更新员工",
            operation_detail=f"更新了员工: {employee_obj.name}, ID: {employee_obj.id}"
        )
    except Exception as e:
        # 如果记录日志失败，记录错误但不影响更新操作
        print(f"记录操作日志失败: {str(e)}")
    
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
    # 先检查数据库中是否存在该用户ID
    user = db.query(User).filter(User.id == current_user.id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="当前用户ID在数据库中不存在"
        )
    
    employee_obj = employee.get(db, id=employee_id)
    if not employee_obj:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="员工不存在"
        )
    
    # 更新员工状态为离职
    employee_update = EmployeeUpdate(status=False)
    employee_obj = employee.update(db=db, db_obj=employee_obj, obj_in=employee_update)
    
    try:
        log_operation(
            db=db,
            user_id=current_user.id,
            operation_type="员工离职",
            operation_detail=f"设置员工: {employee_obj.name}, ID: {employee_obj.id} 为离职状态，离职日期: {leave_data.leave_date}"
        )
    except Exception as e:
        # 如果记录日志失败，记录错误但不影响离职操作
        print(f"记录操作日志失败: {str(e)}")
    
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