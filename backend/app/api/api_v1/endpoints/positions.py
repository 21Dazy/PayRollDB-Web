from typing import Any, List, Optional

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session, joinedload

from app.api.deps import get_current_hr_user, get_current_user, get_db
from app.models.user import User
from app.models.position import Position
from app.models.department import Department
from app.models.employee import Employee
from app.schemas.position import PositionCreate, PositionUpdate, PositionResponse, PositionWithDeptResponse
from app.utils.log import log_operation

router = APIRouter()

@router.get("/", response_model=List[PositionWithDeptResponse])
def read_positions(
    skip: int = 0,
    limit: int = 100,
    department_id: Optional[int] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Any:
    """
    获取职位列表，可以按部门筛选
    """
    query = db.query(Position).join(Department)
    
    # 如果指定了部门ID，进行过滤
    if department_id is not None:
        query = query.filter(Position.department_id == department_id)
    
    positions = query.offset(skip).limit(limit).all()
    
    # 构造响应数据，添加部门名称
    result = []
    for position in positions:
        position_dict = {
            "id": position.id,
            "name": position.name,
            "department_id": position.department_id,
            "description": position.description,
            "created_at": position.created_at,
            "updated_at": position.updated_at,
            "department_name": position.department.name if position.department else None
        }
        result.append(position_dict)
    
    return result

@router.post("/", response_model=PositionResponse, status_code=status.HTTP_201_CREATED)
def create_position(
    *,
    db: Session = Depends(get_db),
    position_in: PositionCreate,
    current_user: User = Depends(get_current_hr_user)
) -> Any:
    """
    创建新职位（需要HR或管理员权限）
    """
    # 检查部门是否存在
    department = db.query(Department).filter(Department.id == position_in.department_id).first()
    if not department:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="所选部门不存在"
        )
        
    position = Position(
        name=position_in.name,
        department_id=position_in.department_id,
        description=position_in.description
    )
    db.add(position)
    db.commit()
    db.refresh(position)
    
    # 记录操作日志
    log_operation(
        db=db,
        user_id=current_user.id,
        operation_type="创建职位",
        operation_content=f"创建了职位: {position.name}, 所属部门: {department.name}"
    )
    
    return position

@router.get("/{position_id}", response_model=PositionWithDeptResponse)
def read_position(
    *,
    db: Session = Depends(get_db),
    position_id: int,
    current_user: User = Depends(get_current_user)
) -> Any:
    """
    获取特定职位详情
    """
    position = db.query(Position).filter(Position.id == position_id).first()
    if not position:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="职位不存在"
        )
    
    # 获取部门名称
    department = db.query(Department).filter(Department.id == position.department_id).first()
    
    # 构造响应
    response = {
        "id": position.id,
        "name": position.name,
        "department_id": position.department_id,
        "description": position.description,
        "created_at": position.created_at,
        "updated_at": position.updated_at,
        "department_name": department.name if department else None
    }
    
    return response

@router.put("/{position_id}", response_model=PositionResponse)
def update_position(
    *,
    db: Session = Depends(get_db),
    position_id: int,
    position_in: PositionUpdate,
    current_user: User = Depends(get_current_hr_user)
) -> Any:
    """
    更新职位信息（需要HR或管理员权限）
    """
    position = db.query(Position).filter(Position.id == position_id).first()
    if not position:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="职位不存在"
        )
    
    # 如果更新了部门ID，检查部门是否存在
    if position_in.department_id is not None:
        department = db.query(Department).filter(Department.id == position_in.department_id).first()
        if not department:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="所选部门不存在"
            )
    
    update_data = position_in.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(position, field, value)
    
    db.commit()
    db.refresh(position)
    
    # 记录操作日志
    log_operation(
        db=db,
        user_id=current_user.id,
        operation_type="更新职位",
        operation_content=f"更新了职位: {position.name}"
    )
    
    return position

@router.get("/by-department/{department_id}", response_model=List[PositionResponse])
def read_positions_by_department(
    *,
    db: Session = Depends(get_db),
    department_id: int,
    current_user: User = Depends(get_current_user)
) -> Any:
    """
    获取指定部门下的所有职位
    """
    # 检查部门是否存在
    department = db.query(Department).filter(Department.id == department_id).first()
    if not department:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="部门不存在"
        )
    
    positions = db.query(Position).filter(Position.department_id == department_id).all()
    return positions

@router.delete("/{position_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_position(
    *,
    db: Session = Depends(get_db),
    position_id: int,
    current_user: User = Depends(get_current_hr_user)
) -> None:
    """
    删除职位
    """
    # 检查职位是否存在
    position = db.query(Position).filter(Position.id == position_id).first()
    if not position:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="职位不存在"
        )
    
    # 检查职位下是否有员工
    employee_count = db.query(Employee).filter(Employee.position_id == position_id).count()
    if employee_count > 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="职位下有员工，无法删除"
        )
    
    # 记录操作日志
    log_operation(
        db=db,
        user_id=current_user.id,
        operation_type="删除职位",
        operation_detail=f"删除了职位: {position.name}, ID: {position.id}"
    )
    
    # 删除职位
    db.delete(position)
    db.commit()
    
    return None 