from typing import Any, List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_admin, get_current_user, get_db
from app.core.security import get_password_hash, verify_password
from app.models.user import User
from app.schemas.user import UserCreate, UserUpdate, UserResponse, UserPasswordUpdate
from app.utils.log import log_operation

router = APIRouter()

@router.get("/", response_model=List[UserResponse])
def read_users(
    skip: int = 0,
    limit: int = 100,
    role: str = None,
    is_active: bool = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin)
) -> Any:
    """
    获取用户列表
    """
    query = db.query(User)
    if role:
        query = query.filter(User.role == role)
    if is_active is not None:
        query = query.filter(User.is_active == is_active)
    
    users = query.offset(skip).limit(limit).all()
    return users

@router.post("/", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def create_user(
    *,
    db: Session = Depends(get_db),
    user_in: UserCreate,
    current_user: User = Depends(get_current_admin)
) -> Any:
    """
    创建新用户
    """
    # 检查用户名是否已存在
    user = db.query(User).filter(User.username == user_in.username).first()
    if user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="用户名已存在"
        )
    
    # 创建新用户
    user = User(
        username=user_in.username,
        password=get_password_hash(user_in.password),
        employee_id=user_in.employee_id,
        role=user_in.role,
        is_active=True
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    
    # 记录操作日志
    log_operation(
        db=db,
        user_id=current_user.id,
        operation_type="创建用户",
        operation_detail=f"创建了用户: {user.username}"
    )
    
    return user

@router.get("/{user_id}", response_model=UserResponse)
def read_user(
    *,
    db: Session = Depends(get_db),
    user_id: int,
    current_user: User = Depends(get_current_admin)
) -> Any:
    """
    获取用户详情
    """
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="用户不存在"
        )
    return user

@router.put("/{user_id}", response_model=UserResponse)
def update_user(
    *,
    db: Session = Depends(get_db),
    user_id: int,
    user_in: UserUpdate,
    current_user: User = Depends(get_current_admin)
) -> Any:
    """
    更新用户信息
    """
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="用户不存在"
        )
    
    # 检查用户名是否已存在
    if user_in.username and user_in.username != user.username:
        existing_user = db.query(User).filter(User.username == user_in.username).first()
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="用户名已存在"
            )
    
    # 更新用户信息
    update_data = user_in.dict(exclude_unset=True)
    if "password" in update_data:
        update_data["password"] = get_password_hash(update_data["password"])
    
    for field, value in update_data.items():
        setattr(user, field, value)
    
    db.commit()
    db.refresh(user)
    
    # 记录操作日志
    log_operation(
        db=db,
        user_id=current_user.id,
        operation_type="更新用户",
        operation_detail=f"更新了用户: {user.username}"
    )
    
    return user

@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user(
    *,
    db: Session = Depends(get_db),
    user_id: int,
    current_user: User = Depends(get_current_admin)
) -> None:
    """
    删除用户
    """
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="用户不存在"
        )
    
    # 记录操作日志
    log_operation(
        db=db,
        user_id=current_user.id,
        operation_type="删除用户",
        operation_detail=f"删除了用户: {user.username}"
    )
    
    db.delete(user)
    db.commit()
    
    return None

@router.post("/{user_id}/change-password", status_code=status.HTTP_200_OK)
def change_user_password(
    *,
    db: Session = Depends(get_db),
    user_id: int,
    password_in: UserPasswordUpdate,
    current_user: User = Depends(get_current_user)
) -> Any:
    """
    修改用户密码
    """
    # 检查是否为管理员或本人
    if current_user.role != "admin" and current_user.id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="权限不足"
        )
    
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="用户不存在"
        )
    
    # 如果是本人修改密码，需要验证当前密码
    if current_user.id == user_id:
        if not verify_password(password_in.current_password, user.password):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="当前密码错误"
            )
    
    # 更新密码
    user.password = get_password_hash(password_in.new_password)
    db.commit()
    
    # 记录操作日志
    log_operation(
        db=db,
        user_id=current_user.id,
        operation_type="修改密码",
        operation_detail=f"修改了用户密码: {user.username}"
    )
    
    return {"message": "密码修改成功"}