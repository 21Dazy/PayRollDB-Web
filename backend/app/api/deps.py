from typing import Generator, Optional

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import jwt
from pydantic import ValidationError
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.security import ALGORITHM
from app.db.session import SessionLocal
from app.models.user import User
from app.schemas.token import TokenPayload

# OAuth2 配置
reusable_oauth2 = OAuth2PasswordBearer(
    tokenUrl=f"{settings.API_V1_STR}/auth/login"
)

def get_db() -> Generator:
    try:
        db = SessionLocal()
        yield db
    finally:
        db.close()

def get_current_user(
    db: Session = Depends(get_db), token: str = Depends(reusable_oauth2)
) -> User:
    """
    获取当前登录用户
    """
    try:
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[ALGORITHM]
        )
        token_data = TokenPayload(**payload)
    except (jwt.JWTError, ValidationError):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="无效的凭证",
            headers={"WWW-Authenticate": "Bearer"},
        )
    user = db.query(User).filter(User.id == token_data.sub).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="用户不存在")
    if not user.is_active:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="用户未激活")
    return user

def get_current_active_user(
    current_user: User = Depends(get_current_user),
) -> User:
    """
    获取当前激活用户
    """
    if not current_user.is_active:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="用户未激活")
    return current_user

def get_current_hr_user(
    current_user: User = Depends(get_current_user),
) -> User:
    """
    获取当前HR用户或管理员
    """
    if current_user.role not in ["hr", "admin"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, 
            detail="权限不足，需要HR或管理员权限"
        )
    return current_user

def get_current_admin(
    current_user: User = Depends(get_current_user),
) -> User:
    """
    获取当前管理员用户
    """
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, 
            detail="权限不足，需要管理员权限"
        )
    return current_user

def get_current_manager_user(
    current_user: User = Depends(get_current_user),
) -> User:
    """
    获取当前管理层用户（经理、HR或管理员）
    """
    if current_user.role not in ["admin", "hr", "manager"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, 
            detail="权限不足，需要经理、HR或管理员权限"
        )
    return current_user 