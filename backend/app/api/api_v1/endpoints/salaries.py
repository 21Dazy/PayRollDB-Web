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
from app.models.salary_config import EmployeeSalaryConfig as DBEmployeeSalaryConfig
from app.schemas.salary import (
    SalaryItemCreate, SalaryItemUpdate, SalaryItemResponse,
    SalaryRecordCreate, SalaryRecordUpdate, SalaryRecordResponse,
    SalaryRecordDetailResponse, SalaryDetailResponse,
    SalaryPaymentRequest, SalaryPaymentResponse, PaginatedResponse
)
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
@router.get("/records", response_model=PaginatedResponse)
def read_salary_records(
    skip: int = 0,
    limit: int = 100,
    department_id: Optional[int] = None,
    employee_id: Optional[int] = None,
    year: Optional[int] = None,
    month: Optional[int] = None,
    status: Optional[str] = None,
    keyword: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Any:
    # 打印接收到的参数，用于调试
    print(f"接收到的参数: skip={skip}, limit={limit}, year={year}, month={month}, department_id={department_id}, status={status}, keyword={keyword}")
    """
    获取工资记录列表
    """
    query = db.query(SalaryRecord).join(Employee).join(Employee.department)
    
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
        
    if keyword:
        query = query.filter(Employee.name.ilike(f"%{keyword}%"))
    
    # 计算总数
    total = query.count()
    
    # 获取分页数据
    records = query.offset(skip).limit(limit).all()
    
    # 转换为响应格式，添加员工和部门信息
    result = []
    for record in records:
        employee = record.employee
        # 创建一个新的字典，只包含需要的属性，避免包含SQLAlchemy对象
        record_dict = {
            "id": record.id,
            "employeeId": record.employee_id,
            "year": record.year,
            "month": record.month,
            "baseSalary": record.base_salary,
            "overtimePay": record.overtime_pay,
            "bonus": record.bonus,
            "performanceBonus": record.performance_bonus,
            "attendanceBonus": record.attendance_bonus,
            "transportationAllowance": record.transportation_allowance,
            "mealAllowance": record.meal_allowance,
            "deduction": record.deduction,
            "lateDeduction": record.late_deduction,
            "absenceDeduction": record.absence_deduction,
            "socialSecurity": record.social_security,
            "personalTax": record.personal_tax,
            "netSalary": record.net_salary,
            "status": record.status,
            "paymentDate": record.payment_date,
            "remark": record.remark,
            "createdAt": record.created_at,
            "updatedAt": record.updated_at,
            "employeeName": employee.name if employee else None,
            "departmentName": employee.department.name if employee and employee.department else None,
            "positionName": employee.position.name if employee and employee.position else None,
            "bankName": employee.bank_name if employee else None,
            "bankAccount": employee.bank_account if employee else None
        }
        result.append(record_dict)
    
    # 返回带有总数的响应
    return {
        "items": result,
        "total": total
    }

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
    
    # 确保加载所有关联数据
    details = []
    for detail in record.details:
        if detail.item:
            details.append({
                "id": detail.id,
                "item": {
                    "id": detail.item.id,
                    "name": detail.item.name,
                    "type": detail.item.type,
                    "is_percentage": detail.item.is_percentage,
                    "is_system": detail.item.is_system,
                    "created_at": detail.item.created_at,
                    "updated_at": detail.item.updated_at
                },
                "amount": detail.amount,
                "created_at": detail.created_at,
                "updated_at": detail.updated_at
            })
    
    # 构建详细响应
    response_data = {
        "id": record.id,
        "employee": record.employee,
        "year": record.year,
        "month": record.month,
        "base_salary": record.base_salary,
        "overtime_pay": record.overtime_pay,
        "bonus": record.bonus,
        "performance_bonus": record.performance_bonus,
        "attendance_bonus": record.attendance_bonus,
        "transportation_allowance": record.transportation_allowance,
        "meal_allowance": record.meal_allowance,
        "deduction": record.deduction,
        "social_security": record.social_security,
        "late_deduction": record.late_deduction,
        "absence_deduction": record.absence_deduction,
        "personal_tax": record.personal_tax,
        "net_salary": record.net_salary,
        "status": record.status,
        "payment_date": record.payment_date,
        "remark": record.remark,
        "created_at": record.created_at,
        "updated_at": record.updated_at,
        "details": details
    }
    
    return response_data

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

@router.delete("/records/{record_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_salary_record(
    *,
    db: Session = Depends(get_db),
    record_id: int,
    current_user: User = Depends(get_current_hr_user)
) -> None:
    """
    删除工资记录
    """
    record = db.query(SalaryRecord).filter(SalaryRecord.id == record_id).first()
    if not record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="工资记录不存在"
        )
    
    # 如果已发放，不允许删除
    if record.status == "paid":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="已发放的工资记录不允许删除"
        )
    
    employee_id = record.employee_id
    year = record.year
    month = record.month
    
    db.delete(record)
    db.commit()
    
    log_operation(
        db=db,
        user_id=current_user.id,
        operation_type="删除工资记录",
        operation_detail=f"删除了员工 ID: {employee_id} 的 {year}年{month}月 工资记录"
    )
    
    return None

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

# 薪资配置相关接口
@router.get("/config/{employee_id}", response_model=EmployeeSalaryConfig)
def get_employee_salary_config(
    *,
    db: Session = Depends(get_db),
    employee_id: int,
    effective_date: date = None,
    current_user: User = Depends(get_current_user),
) -> Any:
    """
    获取员工薪资配置
    """
    # 检查员工是否存在
    employee = db.query(Employee).filter(Employee.id == employee_id).first()
    if not employee:
        raise HTTPException(status_code=404, detail="员工不存在")
    
    # 获取配置
    print(f"获取员工 {employee_id} ({employee.name}) 的薪资配置")
    configs = crud_salary_config.get_employee_config(
        db=db, 
        employee_id=employee_id,
        effective_date=effective_date or date.today()
    )
    
    print(f"获取到 {len(configs)} 条薪资配置")
    
    # 转换为响应格式
    items = []
    for config in configs:
        # 确保薪资项目存在
        salary_item = db.query(SalaryItem).filter(SalaryItem.id == config.item_id).first()
        if not salary_item:
            print(f"警告: 薪资配置 {config.id} 引用了不存在的薪资项目 {config.item_id}")
            continue
            
        print(f"处理薪资配置: item_id={config.item_id}, item_name={salary_item.name}, value={config.value}")
        
        item = SalaryConfigItemInDB(
            id=config.id,
            employee_id=config.employee_id,
            item_id=config.item_id,
            value=config.value,
            base_item=config.base_item,
            is_active=config.is_active,
            effective_date=config.effective_date,
            item_name=salary_item.name,
            type=salary_item.type,
            is_percentage=salary_item.is_percentage,
            is_system=salary_item.is_system
        )
        items.append(item)
    
    # 如果没有配置，添加默认的基本工资配置
    if not items:
        print(f"员工 {employee_id} 没有薪资配置，尝试添加默认基本工资配置")
        base_salary_item = db.query(SalaryItem).filter(SalaryItem.name == '基本工资').first()
        if base_salary_item and employee.base_salary:
            print(f"添加默认基本工资配置: {employee.base_salary}")
            # 创建默认配置
            default_config = DBEmployeeSalaryConfig(
                employee_id=employee_id,
                item_id=base_salary_item.id,
                value=employee.base_salary,
                is_active=True,
                effective_date=date.today()
            )
            db.add(default_config)
            db.commit()
            db.refresh(default_config)
            
            # 添加到响应中
            items.append(SalaryConfigItemInDB(
                id=default_config.id,
                employee_id=default_config.employee_id,
                item_id=base_salary_item.id,
                value=employee.base_salary,
                base_item=None,
                is_active=True,
                effective_date=date.today(),
                item_name=base_salary_item.name,
                type=base_salary_item.type,
                is_percentage=base_salary_item.is_percentage,
                is_system=base_salary_item.is_system
            ))
        else:
            # 即使没有基本工资配置，也要返回空的items列表
            print(f"无法添加默认基本工资配置: 基本工资项目不存在或员工没有设置基本工资")
    
    return EmployeeSalaryConfig(employee_id=employee_id, items=items)

@router.put("/config/{employee_id}", response_model=EmployeeSalaryConfig)
def update_employee_salary_config(
    *,
    db: Session = Depends(get_db),
    employee_id: int,
    config_in: EmployeeSalaryConfigUpdate,
    current_user: User = Depends(get_current_hr_user),
) -> Any:
    """
    更新员工薪资配置
    """
    # 检查员工是否存在
    employee = db.query(Employee).filter(Employee.id == employee_id).first()
    if not employee:
        raise HTTPException(status_code=404, detail="员工不存在")
    
    # 检查薪资项目是否存在
    print(f"更新员工 {employee_id} ({employee.name}) 的薪资配置")
    print(f"收到 {len(config_in.items)} 条薪资配置项")
    
    for item in config_in.items:
        salary_item = db.query(SalaryItem).filter(SalaryItem.id == item.item_id).first()
        if not salary_item:
            raise HTTPException(status_code=400, detail=f"薪资项目 ID {item.item_id} 不存在")
        print(f"薪资项目: {item.item_id} - {salary_item.name}, 值: {item.value}")
    
    # 更新配置
    configs = crud_salary_config.update_employee_config(
        db=db,
        employee_id=employee_id,
        config_items=config_in.items
    )
    
    print(f"更新了 {len(configs)} 条薪资配置")
    
    # 转换为响应格式
    items = []
    for config in configs:
        # 确保薪资项目存在
        salary_item = db.query(SalaryItem).filter(SalaryItem.id == config.item_id).first()
        if not salary_item:
            print(f"警告: 薪资配置 {config.id} 引用了不存在的薪资项目 {config.item_id}")
            continue
            
        print(f"处理薪资配置: item_id={config.item_id}, item_name={salary_item.name}, value={config.value}")
        
        item = SalaryConfigItemInDB(
            id=config.id,
            employee_id=config.employee_id,
            item_id=config.item_id,
            value=config.value,
            base_item=config.base_item,
            is_active=config.is_active,
            effective_date=config.effective_date,
            item_name=salary_item.name,
            type=salary_item.type,
            is_percentage=salary_item.is_percentage,
            is_system=salary_item.is_system
        )
        items.append(item)
    
    log_operation(
        db=db,
        user_id=current_user.id,
        operation_type="更新员工薪资配置",
        operation_detail=f"更新了员工 {employee.name} (ID: {employee_id}) 的薪资配置"
    )
    
    return EmployeeSalaryConfig(employee_id=employee_id, items=items)

@router.post("/generate", response_model=SalaryGenerateResponse)
def generate_salary_records(
    *,
    db: Session = Depends(get_db),
    request: SalaryGenerateRequest,
    current_user: User = Depends(get_current_hr_user),
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
        
        log_operation(
            db=db,
            user_id=current_user.id,
            operation_type="批量生成薪资记录",
            operation_detail=f"生成了 {request.year}年{request.month}月 的薪资记录，成功{result['generated_count']}条，失败{result.get('failed_count', 0)}条"
        )
        
        return SalaryGenerateResponse(
            success=True,
            message=f"成功生成{result['generated_count']}条薪资记录",
            generated_count=result['generated_count'],
            failed_count=result.get('failed_count', 0),
            errors=result.get('errors', []),
            total_generated=result['generated_count'],
            total_updated=result['updated_count'],
            department_id=request.department_id,
            year=request.year,
            month=request.month
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/statistics")
def get_salary_statistics(
    year: Optional[int] = Query(None, description="年份"),
    month: Optional[int] = Query(None, description="月份"),
    department_id: Optional[int] = Query(None, description="部门ID"),
    position_id: Optional[int] = Query(None, description="职位ID"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)  # 改为普通用户权限
) -> Any:
    """
    获取薪资统计数据，支持按部门、职位筛选
    管理员可以查看全局统计，普通员工只能查看自己的数据
    """
    from app.models.department import Department
    from app.models.position import Position
    from sqlalchemy import func, desc
    
    # 如果没有指定年月，默认使用当前年月
    if not year:
        year = datetime.now().year
    if not month:
        month = datetime.now().month
    
    # 构建基础查询
    query = db.query(SalaryRecord).join(Employee).filter(
        SalaryRecord.year == year,
        SalaryRecord.month == month,
        Employee.status == 1  # 只查询在职员工
    )
    
    # 权限控制：普通员工只能查看自己的数据
    if current_user.role not in ["admin", "hr", "manager"]:
        if not current_user.employee_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="普通用户需要关联员工信息才能查看薪资统计"
            )
        query = query.filter(Employee.id == current_user.employee_id)
        # 普通员工不能使用部门和职位筛选
        department_id = None
        position_id = None
    else:
        # 管理员可以按部门和职位筛选
        if department_id:
            query = query.filter(Employee.department_id == department_id)
        
        if position_id:
            query = query.filter(Employee.position_id == position_id)
    
    # 获取薪资记录
    salary_records = query.all()
    
    if not salary_records:
        return {
            "year": year,
            "month": month,
            "employee_count": 0,
            "average_salary": 0,
            "max_salary": 0,
            "min_salary": 0,
            "total_salary": 0,
            "salary_records": [],
            "department_salary_distribution": []
        }
    
    # 计算统计数据
    net_salaries = [float(record.net_salary) for record in salary_records]
    employee_count = len(salary_records)
    average_salary = sum(net_salaries) / employee_count if employee_count > 0 else 0
    max_salary = max(net_salaries) if net_salaries else 0
    min_salary = min(net_salaries) if net_salaries else 0
    total_salary = sum(net_salaries)
    
    # 构建薪资记录详情
    salary_records_data = []
    for record in salary_records:
        salary_records_data.append({
            "id": record.id,
            "employee_id": record.employee_id,
            "employee_name": record.employee.name,
            "department_name": record.employee.department.name if record.employee.department else "",
            "position_name": record.employee.position.name if record.employee.position else "",
            "base_salary": float(record.base_salary),
            "overtime_pay": float(record.overtime_pay),
            "bonus": float(record.bonus),
            "performance_bonus": float(record.performance_bonus),
            "attendance_bonus": float(record.attendance_bonus),
            "transportation_allowance": float(record.transportation_allowance),
            "meal_allowance": float(record.meal_allowance),
            "total_income": float(
                record.base_salary + record.overtime_pay + record.bonus + 
                record.performance_bonus + record.attendance_bonus + 
                record.transportation_allowance + record.meal_allowance
            ),
            "deduction": float(record.deduction),
            "social_security": float(record.social_security),
            "late_deduction": float(record.late_deduction),
            "absence_deduction": float(record.absence_deduction),
            "personal_tax": float(record.personal_tax),
            "total_deduction": float(
                record.deduction + record.social_security + record.late_deduction + 
                record.absence_deduction + record.personal_tax
            ),
            "net_salary": float(record.net_salary),
            "status": record.status,
            "payment_date": record.payment_date
        })
    
    # 计算部门薪资分布（只有管理员且没有按部门筛选时才显示）
    department_salary_distribution = []
    if current_user.role in ["admin", "hr", "manager"] and not department_id:
        dept_query = (
            db.query(
                Department.name.label('department_name'),
                func.sum(SalaryRecord.net_salary).label('total_salary'),
                func.count(SalaryRecord.id).label('employee_count'),
                func.avg(SalaryRecord.net_salary).label('average_salary')
            )
            .join(Employee, Employee.department_id == Department.id)
            .join(SalaryRecord, SalaryRecord.employee_id == Employee.id)
            .filter(
                SalaryRecord.year == year,
                SalaryRecord.month == month,
                Employee.status == 1
            )
            .group_by(Department.id, Department.name)
            .all()
        )
        
        for dept_data in dept_query:
            department_salary_distribution.append({
                "name": dept_data.department_name,
                "value": float(dept_data.total_salary),
                "employee_count": dept_data.employee_count,
                "average_salary": float(dept_data.average_salary)
            })
    
    return {
        "year": year,
        "month": month,
        "filter": {
            "department_id": department_id,
            "position_id": position_id
        },
        "employee_count": employee_count,
        "average_salary": round(average_salary, 2),
        "max_salary": max_salary,
        "min_salary": min_salary,
        "total_salary": total_salary,
        "salary_records": salary_records_data,
        "department_salary_distribution": department_salary_distribution,
        "user_role": current_user.role,  # 返回用户角色，前端可据此调整显示
        "is_personal_view": current_user.role not in ["admin", "hr", "manager"]  # 是否为个人视图
    } 