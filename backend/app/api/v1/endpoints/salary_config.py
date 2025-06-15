from typing import Any, List
from datetime import date
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app import crud, schemas
from app.api import deps
from app.schemas.salary_config import (
    EmployeeSalaryConfig,
    EmployeeSalaryConfigCreate,
    EmployeeSalaryConfigUpdate,
    SalaryConfigItemInDB,
    SalaryGenerateRequest,
    SalaryGenerateResponse
)
from app.crud.crud_salary_config import salary_config as crud_salary_config
from app.services.salary_service import SalaryService

router = APIRouter()

@router.get("/config/{employee_id}", response_model=EmployeeSalaryConfig)
def get_employee_salary_config(
    *,
    db: Session = Depends(deps.get_db),
    employee_id: int,
    effective_date: date = None,
    current_user: schemas.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    获取员工薪资配置
    """
    # 检查员工是否存在
    employee = crud.employee.get(db=db, id=employee_id)
    if not employee:
        raise HTTPException(status_code=404, detail="员工不存在")
    
    # 获取配置
    configs = crud_salary_config.get_employee_config(
        db=db, 
        employee_id=employee_id,
        effective_date=effective_date or date.today()
    )
    
    # 转换为响应格式
    items = []
    for config in configs:
        item = SalaryConfigItemInDB(
            id=config.id,
            employee_id=config.employee_id,
            item_id=config.item_id,
            value=config.value,
            base_item=config.base_item,
            is_active=config.is_active,
            effective_date=config.effective_date,
            item_name=config.salary_item.name if config.salary_item else None,
            type=config.salary_item.type if config.salary_item else None,
            is_percentage=config.salary_item.is_percentage if config.salary_item else None,
            is_system=config.salary_item.is_system if config.salary_item else None
        )
        items.append(item)
    
    return EmployeeSalaryConfig(employee_id=employee_id, items=items)

@router.put("/config/{employee_id}", response_model=EmployeeSalaryConfig)
def update_employee_salary_config(
    *,
    db: Session = Depends(deps.get_db),
    employee_id: int,
    config_in: EmployeeSalaryConfigUpdate,
    current_user: schemas.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    更新员工薪资配置
    """
    # 检查员工是否存在
    employee = crud.employee.get(db=db, id=employee_id)
    if not employee:
        raise HTTPException(status_code=404, detail="员工不存在")
    
    # 更新配置
    configs = crud_salary_config.update_employee_config(
        db=db,
        employee_id=employee_id,
        config_items=config_in.items
    )
    
    # 转换为响应格式
    items = []
    for config in configs:
        item = SalaryConfigItemInDB(
            id=config.id,
            employee_id=config.employee_id,
            item_id=config.item_id,
            value=config.value,
            base_item=config.base_item,
            is_active=config.is_active,
            effective_date=config.effective_date,
            item_name=config.salary_item.name if config.salary_item else None,
            type=config.salary_item.type if config.salary_item else None,
            is_percentage=config.salary_item.is_percentage if config.salary_item else None,
            is_system=config.salary_item.is_system if config.salary_item else None
        )
        items.append(item)
    
    return EmployeeSalaryConfig(employee_id=employee_id, items=items)

@router.post("/generate", response_model=SalaryGenerateResponse)
def generate_salary_records(
    *,
    db: Session = Depends(deps.get_db),
    request: SalaryGenerateRequest,
    current_user: schemas.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    批量生成薪资记录
    """
    try:
        service = SalaryService(db)
        result = service.generate_salary_records(
            year=request.year,
            month=request.month,
            department_id=request.department_id,
            employee_ids=request.employee_ids
        )
        
        return SalaryGenerateResponse(
            success=True,
            message=f"成功生成{result['generated_count']}条薪资记录",
            generated_count=result['generated_count'],
            failed_count=result.get('failed_count', 0),
            errors=result.get('errors', [])
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e)) 