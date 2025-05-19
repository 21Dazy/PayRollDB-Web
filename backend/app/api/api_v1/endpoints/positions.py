from typing import Any, List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_hr_user, get_current_user, get_db
from app.models.user import User
from app.models.position import Position
from app.models.employee import Employee
from app.schemas.position import PositionCreate, PositionUpdate, PositionResponse
from app.utils.log import log_operation

router = APIRouter()

@router.get("/", response_model=List[PositionResponse])
def read_positions(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Any:
    """
    获取所有职位列表
    """
    positions = db.query(Position).offset(skip).limit(limit).all()
    return positions

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
    position = Position(
        name=position_in.name,
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
        operation_content=f"创建了职位: {position.name}"
    )
    
    return position

@router.get("/{position_id}", response_model=PositionResponse)
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
    return position

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

@router.delete("/{position_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_position(
    *,
    db: Session = Depends(get_db),
    position_id: int,
    current_user: User = Depends(get_current_hr_user)
) -> None:
    """
    删除职位（需要HR或管理员权限）
    
    注意：如果职位下有员工，将无法删除
    """
    position = db.query(Position).filter(Position.id == position_id).first()
    if not position:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="职位不存在"
        )
    
    # 检查职位是否有员工
    employee_count = db.query(Employee).filter(Employee.position_id == position_id).count()
    if employee_count > 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"职位下有{employee_count}名员工，无法删除"
        )
    
    # 记录操作日志
    log_operation(
        db=db,
        user_id=current_user.id,
        operation_type="删除职位",
        operation_content=f"删除了职位: {position.name}"
    )
    
    db.delete(position)
    db.commit() 