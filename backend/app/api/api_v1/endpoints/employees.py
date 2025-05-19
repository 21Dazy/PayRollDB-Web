from typing import Any, List, Optional
from datetime import date

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session

from app.api.deps import get_current_hr_user, get_current_user, get_db
from app.models.user import User
from app.models.employee import Employee
from app.core.security import encrypt_bank_account
from app.utils.log import log_operation

router = APIRouter()

@router.get("/")
def read_employees(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Any:
    """
    获取员工列表
    """
    employees = db.query(Employee).offset(skip).limit(limit).all()
    return employees 