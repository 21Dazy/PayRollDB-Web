from typing import Any, List, Optional
from datetime import datetime, date

from fastapi import APIRouter, Depends, HTTPException, Query, status, Response
from sqlalchemy.orm import Session
from sqlalchemy import and_, extract, func

from app.api.deps import get_current_hr_user, get_current_user, get_db
from app.models.user import User
from app.models.employee import Employee
from app.models.salary_item import SalaryItem
from app.models.salary_record import SalaryRecord
from app.models.salary_detail import SalaryDetail
from app.schemas.salary import (
    SalaryItemCreate, SalaryItemUpdate, SalaryItemResponse,
    SalaryRecordCreate, SalaryRecordUpdate, SalaryRecordResponse,
    SalaryRecordDetailResponse, SalaryDetailResponse,
    SalaryPaymentRequest, SalaryPaymentResponse
)
from app.utils.log import log_operation

router = APIRouter()

# 工资项目相关接口
@router.get("/items", response_model=List[SalaryItemResponse])
def read_salary_items(
    skip: int = 0,
    limit: int = 100,
    type: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Any:
    """
    获取工资项目列表
    """
    query = db.query(SalaryItem)
    
    if type:
        query = query.filter(SalaryItem.type == type)
    
    return query.offset(skip).limit(limit).all()

@router.post("/items", response_model=SalaryItemResponse, status_code=status.HTTP_201_CREATED)
def create_salary_item(
    *,
    db: Session = Depends(get_db),
    item_in: SalaryItemCreate,
    current_user: User = Depends(get_current_hr_user)
) -> Any:
    """
    创建工资项目
    """
    # 检查名称是否已存在
    existing = db.query(SalaryItem).filter(SalaryItem.name == item_in.name).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="工资项目名称已存在"
        )
    
    item = SalaryItem(**item_in.dict())
    db.add(item)
    db.commit()
    db.refresh(item)
    
    log_operation(
        db=db,
        user_id=current_user.id,
        operation_type="创建工资项目",
        operation_detail=f"创建了工资项目: {item.name}, ID: {item.id}"
    )
    
    return item

@router.put("/items/{item_id}", response_model=SalaryItemResponse)
def update_salary_item(
    *,
    db: Session = Depends(get_db),
    item_id: int,
    item_in: SalaryItemUpdate,
    current_user: User = Depends(get_current_hr_user)
) -> Any:
    """
    更新工资项目
    """
    item = db.query(SalaryItem).filter(SalaryItem.id == item_id).first()
    if not item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="工资项目不存在"
        )
    
    # 如果是系统项目，不允许修改类型
    if item.is_system and hasattr(item_in, "type") and item_in.type != item.type:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="系统项目不允许修改类型"
        )
    
    update_data = item_in.dict(exclude_unset=True)
    
    # 如果更新了名称，检查名称是否已存在
    if "name" in update_data and update_data["name"] != item.name:
        existing = db.query(SalaryItem).filter(SalaryItem.name == update_data["name"]).first()
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="工资项目名称已存在"
            )
    
    for key, value in update_data.items():
        setattr(item, key, value)
    
    db.add(item)
    db.commit()
    db.refresh(item)
    
    log_operation(
        db=db,
        user_id=current_user.id,
        operation_type="更新工资项目",
        operation_detail=f"更新了工资项目: {item.name}, ID: {item.id}"
    )
    
    return item

@router.delete("/items/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_salary_item(
    *,
    db: Session = Depends(get_db),
    item_id: int,
    current_user: User = Depends(get_current_hr_user)
) -> None:
    """
    删除工资项目
    """
    item = db.query(SalaryItem).filter(SalaryItem.id == item_id).first()
    if not item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="工资项目不存在"
        )
    
    # 系统项目不允许删除
    if item.is_system:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="系统项目不允许删除"
        )
    
    # 检查是否有工资明细使用此项目
    detail_count = db.query(SalaryDetail).filter(SalaryDetail.item_id == item_id).count()
    if detail_count > 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="该工资项目已被使用，无法删除"
        )
    
    item_name = item.name
    item_id_copy = item.id
    
    db.delete(item)
    db.commit()
    
    log_operation(
        db=db,
        user_id=current_user.id,
        operation_type="删除工资项目",
        operation_detail=f"删除了工资项目: {item_name}, ID: {item_id_copy}"
    )
    
    return None

# 工资记录相关接口
@router.get("/records", response_model=List[SalaryRecordResponse])
def read_salary_records(
    skip: int = 0,
    limit: int = 100,
    department_id: Optional[int] = None,
    employee_id: Optional[int] = None,
    year: Optional[int] = None,
    month: Optional[int] = None,
    status: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Any:
    """
    获取工资记录列表
    """
    query = db.query(SalaryRecord).join(Employee)
    
    # 应用筛选条件
    if department_id is not None:
        query = query.filter(Employee.department_id == department_id)
    
    if employee_id is not None:
        query = query.filter(SalaryRecord.employee_id == employee_id)
    
    if year is not None:
        query = query.filter(SalaryRecord.year == year)
    
    if month is not None:
        query = query.filter(SalaryRecord.month == month)
    
    if status is not None:
        query = query.filter(SalaryRecord.status == status)
    
    return query.offset(skip).limit(limit).all()

@router.post("/records", response_model=SalaryRecordResponse, status_code=status.HTTP_201_CREATED)
def create_salary_record(
    *,
    db: Session = Depends(get_db),
    record_in: SalaryRecordCreate,
    current_user: User = Depends(get_current_hr_user)
) -> Any:
    """
    创建工资记录
    """
    # 检查员工是否存在
    employee = db.query(Employee).filter(Employee.id == record_in.employee_id).first()
    if not employee:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="员工不存在"
        )
    
    # 检查是否已存在相同年月的工资记录
    existing = db.query(SalaryRecord).filter(
        and_(
            SalaryRecord.employee_id == record_in.employee_id,
            SalaryRecord.year == record_in.year,
            SalaryRecord.month == record_in.month
        )
    ).first()
    
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="该员工在此年月已有工资记录"
        )
    
    # 创建工资记录
    # 这里需要根据业务逻辑计算工资相关数据
    # 简化处理，使用员工基本工资作为总工资
    record = SalaryRecord(
        employee_id=record_in.employee_id,
        year=record_in.year,
        month=record_in.month,
        base_salary=employee.base_salary,
        net_salary=employee.base_salary  # 简化计算，实际应该是所有加项减去所有减项
    )
    
    db.add(record)
    db.commit()
    db.refresh(record)
    
    # 创建工资明细
    if record_in.details:
        for detail in record_in.details:
            # 检查工资项目是否存在
            item = db.query(SalaryItem).filter(SalaryItem.id == detail.item_id).first()
            if not item:
                continue
            
            salary_detail = SalaryDetail(
                salary_id=record.id,
                item_id=detail.item_id,
                amount=detail.amount
            )
            db.add(salary_detail)
        
        db.commit()
    
    log_operation(
        db=db,
        user_id=current_user.id,
        operation_type="创建工资记录",
        operation_detail=f"为员工 ID: {record.employee_id} 创建了 {record.year}年{record.month}月 的工资记录"
    )
    
    return record

@router.get("/records/{record_id}", response_model=SalaryRecordDetailResponse)
def read_salary_record(
    record_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Any:
    """
    获取工资记录详情
    """
    record = db.query(SalaryRecord).filter(SalaryRecord.id == record_id).first()
    if not record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="工资记录不存在"
        )
    
    return record

@router.put("/records/{record_id}", response_model=SalaryRecordResponse)
def update_salary_record(
    *,
    db: Session = Depends(get_db),
    record_id: int,
    record_in: SalaryRecordUpdate,
    current_user: User = Depends(get_current_hr_user)
) -> Any:
    """
    更新工资记录
    """
    record = db.query(SalaryRecord).filter(SalaryRecord.id == record_id).first()
    if not record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="工资记录不存在"
        )
    
    # 如果已发放，不允许修改
    if record.status == "paid":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="已发放的工资记录不允许修改"
        )
    
    update_data = record_in.dict(exclude_unset=True)
    
    # 更新字段
    for key, value in update_data.items():
        if key != "details":  # 工资明细单独处理
            setattr(record, key, value)
    
    # 重新计算净工资
    record.net_salary = record.base_salary + record.overtime_pay + record.bonus - record.deduction - record.social_security - record.personal_tax
    
    db.add(record)
    db.commit()
    db.refresh(record)
    
    log_operation(
        db=db,
        user_id=current_user.id,
        operation_type="更新工资记录",
        operation_detail=f"更新了员工 ID: {record.employee_id} 的 {record.year}年{record.month}月 工资记录"
    )
    
    return record

@router.post("/pay", response_model=SalaryPaymentResponse)
def pay_salaries(
    *,
    db: Session = Depends(get_db),
    payment_in: SalaryPaymentRequest,
    current_user: User = Depends(get_current_hr_user)
) -> Any:
    """
    批量更新工资记录状态为已发放
    """
    if not payment_in.record_ids:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="未提供工资记录ID"
        )
    
    # 更新状态
    records = db.query(SalaryRecord).filter(
        SalaryRecord.id.in_(payment_in.record_ids),
        SalaryRecord.status == "pending"
    ).all()
    
    if not records:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="所选工资记录不存在或已发放"
        )
    
    # 批量更新
    for record in records:
        record.status = "paid"
        record.payment_date = payment_in.payment_date
        db.add(record)
    
    db.commit()
    
    log_operation(
        db=db,
        user_id=current_user.id,
        operation_type="批量发放工资",
        operation_detail=f"将 {len(records)} 条工资记录更新为已发放状态"
    )
    
    return {
        "success": True,
        "count": len(records),
        "message": f"成功更新{len(records)}条工资记录为已发放状态"
    }

@router.get("/export")
def export_salaries(
    year: int,
    month: int,
    department_id: Optional[int] = None,
    format: str = "excel",
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_hr_user)
) -> Any:
    """
    导出工资单（CSV或Excel格式）
    """
    # 这里应该实现导出功能，但由于需要使用第三方库如pandas/openpyxl等来生成文件
    # 这里只返回一个示例响应
    
    log_operation(
        db=db,
        user_id=current_user.id,
        operation_type="导出工资单",
        operation_detail=f"导出了 {year}年{month}月 的工资单"
    )
    
    return Response(
        content="导出功能待实现",
        media_type="text/plain"
    ) 