from typing import Any, List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_hr_user, get_current_user, get_db
from app.models.user import User
from app.utils.log import log_operation

router = APIRouter()

@router.get("/")
def read_salaries(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Any:
    """
    获取工资记录列表
    """
    # 基本实现，后续完善
    return {"message": "工资记录功能待实现"} 