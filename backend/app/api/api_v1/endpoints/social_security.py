from typing import Any, List, Optional

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_hr_user, get_current_user, get_db
from app.models.user import User
from app.models.social_security_config import SocialSecurityConfig
from app.models.employee_social_security import EmployeeSocialSecurity
from app.models.employee import Employee
from app.schemas.social_security import (
    SocialSecurityConfigCreate, SocialSecurityConfigUpdate, SocialSecurityConfigResponse,
    EmployeeSocialSecurityCreate, EmployeeSocialSecurityUpdate, EmployeeSocialSecurityDetailResponse,
    EmployeeSocialSecurityBatchCreate, SetDefaultConfigResponse
)
from app.utils.log import log_operation

router = APIRouter()

# 社保配置相关接口
@router.get("/configs", response_model=List[SocialSecurityConfigResponse])
def read_social_security_configs(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Any:
    """
    获取社保公积金配置列表
    """
    configs = db.query(SocialSecurityConfig).all()
    return configs

@router.post("/configs", response_model=SocialSecurityConfigResponse, status_code=status.HTTP_201_CREATED)
def create_social_security_config(
    *,
    db: Session = Depends(get_db),
    config_in: SocialSecurityConfigCreate,
    current_user: User = Depends(get_current_hr_user)
) -> Any:
    """
    创建新社保公积金配置
    """
    # 如果设置为默认配置，需要重置其他配置
    if config_in.is_default:
        db.query(SocialSecurityConfig).filter(SocialSecurityConfig.is_default == True).update(
            {"is_default": False}
        )
    
    config = SocialSecurityConfig(**config_in.dict())
    db.add(config)
    db.commit()
    db.refresh(config)
    
    log_operation(
        db=db,
        user_id=current_user.id,
        operation_type="创建社保配置",
        operation_detail=f"创建了社保配置: {config.name}, ID: {config.id}"
    )
    
    return config

@router.put("/configs/{config_id}", response_model=SocialSecurityConfigResponse)
def update_social_security_config(
    *,
    db: Session = Depends(get_db),
    config_id: int,
    config_in: SocialSecurityConfigUpdate,
    current_user: User = Depends(get_current_hr_user)
) -> Any:
    """
    更新社保公积金配置
    """
    config = db.query(SocialSecurityConfig).filter(SocialSecurityConfig.id == config_id).first()
    if not config:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="社保配置不存在"
        )
    
    update_data = config_in.dict(exclude_unset=True)
    
    # 如果设置为默认配置，需要重置其他配置
    if update_data.get("is_default"):
        db.query(SocialSecurityConfig).filter(SocialSecurityConfig.id != config_id).update(
            {"is_default": False}
        )
    
    for key, value in update_data.items():
        setattr(config, key, value)
    
    db.add(config)
    db.commit()
    db.refresh(config)
    
    log_operation(
        db=db,
        user_id=current_user.id,
        operation_type="更新社保配置",
        operation_detail=f"更新了社保配置: {config.name}, ID: {config.id}"
    )
    
    return config

@router.put("/configs/{config_id}/set-default", response_model=SetDefaultConfigResponse)
def set_default_config(
    *,
    db: Session = Depends(get_db),
    config_id: int,
    current_user: User = Depends(get_current_hr_user)
) -> Any:
    """
    设置指定配置为默认配置
    """
    config = db.query(SocialSecurityConfig).filter(SocialSecurityConfig.id == config_id).first()
    if not config:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="社保配置不存在"
        )
    
    # 重置所有配置的默认状态
    db.query(SocialSecurityConfig).update({"is_default": False})
    
    # 设置当前配置为默认
    config.is_default = True
    db.add(config)
    db.commit()
    
    log_operation(
        db=db,
        user_id=current_user.id,
        operation_type="设置默认社保配置",
        operation_detail=f"设置社保配置: {config.name}, ID: {config.id} 为默认配置"
    )
    
    return {"success": True, "message": "成功设置默认配置"}

# 员工社保配置相关接口
@router.get("/employees", response_model=List[EmployeeSocialSecurityDetailResponse])
def read_employee_social_security(
    department_id: Optional[int] = None,
    employee_id: Optional[int] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Any:
    """
    获取员工社保公积金配置列表
    """
    query = db.query(EmployeeSocialSecurity)
    
    if department_id:
        query = query.join(Employee).filter(Employee.department_id == department_id)
    
    if employee_id:
        query = query.filter(EmployeeSocialSecurity.employee_id == employee_id)
    
    return query.all()

@router.post("/employees", response_model=EmployeeSocialSecurityDetailResponse, status_code=status.HTTP_201_CREATED)
def create_employee_social_security(
    *,
    db: Session = Depends(get_db),
    employee_ss_in: EmployeeSocialSecurityCreate,
    current_user: User = Depends(get_current_hr_user)
) -> Any:
    """
    为员工设置社保公积金配置
    """
    # 检查员工是否存在
    employee = db.query(Employee).filter(Employee.id == employee_ss_in.employee_id).first()
    if not employee:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="员工不存在"
        )
    
    # 检查社保配置是否存在
    config = db.query(SocialSecurityConfig).filter(SocialSecurityConfig.id == employee_ss_in.config_id).first()
    if not config:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="社保配置不存在"
        )
    
    # 创建员工社保配置
    employee_ss = EmployeeSocialSecurity(**employee_ss_in.dict())
    db.add(employee_ss)
    db.commit()
    db.refresh(employee_ss)
    
    log_operation(
        db=db,
        user_id=current_user.id,
        operation_type="设置员工社保配置",
        operation_detail=f"为员工 ID: {employee_ss.employee_id} 设置社保配置 ID: {employee_ss.config_id}"
    )
    
    return employee_ss

@router.put("/employees/{record_id}", response_model=EmployeeSocialSecurityDetailResponse)
def update_employee_social_security(
    *,
    db: Session = Depends(get_db),
    record_id: int,
    employee_ss_in: EmployeeSocialSecurityUpdate,
    current_user: User = Depends(get_current_hr_user)
) -> Any:
    """
    更新员工社保公积金配置
    """
    employee_ss = db.query(EmployeeSocialSecurity).filter(EmployeeSocialSecurity.id == record_id).first()
    if not employee_ss:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="员工社保配置不存在"
        )
    
    update_data = employee_ss_in.dict(exclude_unset=True)
    
    # 如果更新了社保配置ID，需要检查配置是否存在
    if "config_id" in update_data:
        config = db.query(SocialSecurityConfig).filter(SocialSecurityConfig.id == update_data["config_id"]).first()
        if not config:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="社保配置不存在"
            )
    
    for key, value in update_data.items():
        setattr(employee_ss, key, value)
    
    db.add(employee_ss)
    db.commit()
    db.refresh(employee_ss)
    
    log_operation(
        db=db,
        user_id=current_user.id,
        operation_type="更新员工社保配置",
        operation_detail=f"更新了员工 ID: {employee_ss.employee_id} 的社保配置"
    )
    
    return employee_ss

@router.post("/employees/batch", response_model=List[EmployeeSocialSecurityDetailResponse], status_code=status.HTTP_201_CREATED)
def batch_create_employee_social_security(
    *,
    db: Session = Depends(get_db),
    batch_in: EmployeeSocialSecurityBatchCreate,
    current_user: User = Depends(get_current_hr_user)
) -> Any:
    """
    批量设置员工社保公积金配置
    """
    # 检查社保配置是否存在
    config = db.query(SocialSecurityConfig).filter(SocialSecurityConfig.id == batch_in.config_id).first()
    if not config:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="社保配置不存在"
        )
    
    # 创建员工社保配置列表
    result = []
    for employee_id in batch_in.employee_ids:
        # 检查员工是否存在
        employee = db.query(Employee).filter(Employee.id == employee_id).first()
        if not employee:
            continue
        
        employee_ss = EmployeeSocialSecurity(
            employee_id=employee_id,
            config_id=batch_in.config_id,
            base_number=batch_in.base_number,
            housing_fund_base=batch_in.housing_fund_base,
            effective_date=batch_in.effective_date
        )
        db.add(employee_ss)
        result.append(employee_ss)
    
    db.commit()
    for item in result:
        db.refresh(item)
    
    log_operation(
        db=db,
        user_id=current_user.id,
        operation_type="批量设置员工社保配置",
        operation_detail=f"为 {len(result)} 名员工批量设置了社保配置 ID: {batch_in.config_id}"
    )
    
    return result 