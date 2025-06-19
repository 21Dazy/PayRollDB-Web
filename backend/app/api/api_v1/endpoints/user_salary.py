from typing import Any, List, Optional
from datetime import datetime, date
from fastapi import APIRouter, Depends, HTTPException, status, Request, Response
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import and_, desc, func, extract

from app.api.deps import get_db
from app.models.user import User
from app.models.salary_record import SalaryRecord
from app.models.employee import Employee
from app.utils.permissions import (
    require_permission,
    get_current_employee_user,
    log_user_activity,
    PermissionChecker
)

router = APIRouter()

@router.get("/records")
def get_my_salary_records(
    *,
    db: Session = Depends(get_db),
    year: Optional[int] = None,
    month: Optional[int] = None,
    start_year: Optional[int] = None,
    end_year: Optional[int] = None,
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(require_permission("view_salary")),
    request: Request
) -> Any:
    """
    获取当前用户的薪资记录列表
    """
    # 记录访问日志
    log_user_activity(
        db=db,
        user=current_user,
        action_type="查看薪资记录",
        description="用户查看薪资记录列表",
        ip_address=request.client.host if request.client else None
    )
    
    # 构建查询条件
    query = db.query(SalaryRecord).filter(
        SalaryRecord.employee_id == current_user.employee_id
    )
    
    # 按年份筛选
    if year:
        query = query.filter(SalaryRecord.year == year)
    elif start_year and end_year:
        query = query.filter(
            and_(
                SalaryRecord.year >= start_year,
                SalaryRecord.year <= end_year
            )
        )
    
    # 按月份筛选
    if month:
        query = query.filter(SalaryRecord.month == month)
    
    # 按时间倒序排列
    total = query.count()
    records = query.order_by(
        desc(SalaryRecord.year),
        desc(SalaryRecord.month)
    ).offset(skip).limit(limit).all()
    
    # 格式化返回数据
    salary_list = []
    for record in records:
        salary_list.append({
            "id": record.id,
            "year": record.year,
            "month": record.month,
            "period": f"{record.year}年{record.month:02d}月",
            "base_salary": float(record.base_salary),
            "overtime_pay": float(record.overtime_pay),
            "bonus": float(record.bonus),
            "performance_bonus": float(record.performance_bonus),
            "attendance_bonus": float(record.attendance_bonus),
            "transportation_allowance": float(record.transportation_allowance),
            "meal_allowance": float(record.meal_allowance),
            "gross_salary": float(
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
            "payment_date": record.payment_date,
            "created_at": record.created_at
        })
    
    return {
        "records": salary_list,
        "total": total,
        "page": skip // limit + 1,
        "size": limit,
        "summary": {
            "total_records": total,
            "years_covered": len(set(r.year for r in records)) if records else 0
        }
    }

@router.get("/records/{record_id}")
def get_salary_record_detail(
    *,
    db: Session = Depends(get_db),
    record_id: int,
    current_user: User = Depends(require_permission("view_salary")),
    request: Request
) -> Any:
    """
    获取薪资记录详情
    """
    # 查询薪资记录
    record = db.query(SalaryRecord).options(
        joinedload(SalaryRecord.employee).joinedload(Employee.department),
        joinedload(SalaryRecord.employee).joinedload(Employee.position)
    ).filter(
        and_(
            SalaryRecord.id == record_id,
            SalaryRecord.employee_id == current_user.employee_id
        )
    ).first()
    
    if not record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="薪资记录不存在或无权限访问"
        )
    
    # 记录访问日志
    log_user_activity(
        db=db,
        user=current_user,
        action_type="查看薪资详情",
        description=f"查看{record.year}年{record.month:02d}月薪资详情",
        resource_type="salary_record",
        resource_id=record_id,
        ip_address=request.client.host if request.client else None
    )
    
    # 计算薪资组成
    income_items = [
        {"name": "基本工资", "amount": float(record.base_salary)},
        {"name": "加班费", "amount": float(record.overtime_pay)},
        {"name": "奖金", "amount": float(record.bonus)},
        {"name": "绩效奖金", "amount": float(record.performance_bonus)},
        {"name": "全勤奖", "amount": float(record.attendance_bonus)},
        {"name": "交通补贴", "amount": float(record.transportation_allowance)},
        {"name": "餐补", "amount": float(record.meal_allowance)}
    ]
    
    deduction_items = [
        {"name": "其他扣款", "amount": float(record.deduction)},
        {"name": "社保公积金", "amount": float(record.social_security)},
        {"name": "迟到扣款", "amount": float(record.late_deduction)},
        {"name": "缺勤扣款", "amount": float(record.absence_deduction)},
        {"name": "个人所得税", "amount": float(record.personal_tax)}
    ]
    
    # 计算统计数据
    gross_salary = sum(item["amount"] for item in income_items)
    total_deduction = sum(item["amount"] for item in deduction_items)
    
    return {
        "id": record.id,
        "employee_info": {
            "name": record.employee.name,
            "department": record.employee.department.name if record.employee.department else "",
            "position": record.employee.position.name if record.employee.position else ""
        },
        "period": {
            "year": record.year,
            "month": record.month,
            "display": f"{record.year}年{record.month:02d}月"
        },
        "income_items": income_items,
        "deduction_items": deduction_items,
        "summary": {
            "gross_salary": gross_salary,
            "total_deduction": total_deduction,
            "net_salary": float(record.net_salary)
        },
        "status": record.status,
        "payment_date": record.payment_date,
        "remark": record.remark,
        "created_at": record.created_at
    }

@router.get("/statistics")
def get_salary_statistics(
    *,
    db: Session = Depends(get_db),
    year: Optional[int] = None,
    current_user: User = Depends(require_permission("view_salary"))
) -> Any:
    """
    获取薪资统计信息
    """
    current_year = year or datetime.now().year
    
    # 查询指定年份的薪资记录
    query = db.query(SalaryRecord).filter(
        and_(
            SalaryRecord.employee_id == current_user.employee_id,
            SalaryRecord.year == current_year
        )
    )
    
    records = query.all()
    
    if not records:
        return {
            "year": current_year,
            "total_records": 0,
            "annual_summary": {
                "total_gross": 0,
                "total_deduction": 0,
                "total_net": 0,
                "average_monthly": 0
            },
            "monthly_data": [],
            "income_breakdown": {},
            "deduction_breakdown": {}
        }
    
    # 计算年度统计
    total_gross = sum(
        float(r.base_salary + r.overtime_pay + r.bonus + r.performance_bonus + 
              r.attendance_bonus + r.transportation_allowance + r.meal_allowance)
        for r in records
    )
    total_deduction = sum(
        float(r.deduction + r.social_security + r.late_deduction + 
              r.absence_deduction + r.personal_tax)
        for r in records
    )
    total_net = sum(float(r.net_salary) for r in records)
    
    # 月度数据
    monthly_data = []
    for record in sorted(records, key=lambda x: x.month):
        gross = float(
            record.base_salary + record.overtime_pay + record.bonus + 
            record.performance_bonus + record.attendance_bonus + 
            record.transportation_allowance + record.meal_allowance
        )
        deduction = float(
            record.deduction + record.social_security + record.late_deduction + 
            record.absence_deduction + record.personal_tax
        )
        
        monthly_data.append({
            "month": record.month,
            "gross_salary": gross,
            "total_deduction": deduction,
            "net_salary": float(record.net_salary),
            "status": record.status
        })
    
    # 收入项目汇总
    income_breakdown = {
        "base_salary": sum(float(r.base_salary) for r in records),
        "overtime_pay": sum(float(r.overtime_pay) for r in records),
        "bonus": sum(float(r.bonus) for r in records),
        "performance_bonus": sum(float(r.performance_bonus) for r in records),
        "attendance_bonus": sum(float(r.attendance_bonus) for r in records),
        "transportation_allowance": sum(float(r.transportation_allowance) for r in records),
        "meal_allowance": sum(float(r.meal_allowance) for r in records)
    }
    
    # 扣除项目汇总
    deduction_breakdown = {
        "deduction": sum(float(r.deduction) for r in records),
        "social_security": sum(float(r.social_security) for r in records),
        "late_deduction": sum(float(r.late_deduction) for r in records),
        "absence_deduction": sum(float(r.absence_deduction) for r in records),
        "personal_tax": sum(float(r.personal_tax) for r in records)
    }
    
    return {
        "year": current_year,
        "total_records": len(records),
        "annual_summary": {
            "total_gross": total_gross,
            "total_deduction": total_deduction,
            "total_net": total_net,
            "average_monthly": total_net / len(records) if records else 0
        },
        "monthly_data": monthly_data,
        "income_breakdown": income_breakdown,
        "deduction_breakdown": deduction_breakdown
    }

@router.get("/years")
def get_salary_years(
    *,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission("view_salary"))
) -> Any:
    """
    获取有薪资记录的年份列表
    """
    years = db.query(SalaryRecord.year).filter(
        SalaryRecord.employee_id == current_user.employee_id
    ).distinct().order_by(desc(SalaryRecord.year)).all()
    
    return {
        "years": [year[0] for year in years],
        "current_year": datetime.now().year
    }

@router.post("/records/{record_id}/download-payslip")
def download_payslip(
    *,
    db: Session = Depends(get_db),
    record_id: int,
    current_user: User = Depends(require_permission("view_payslip")),
    request: Request
) -> Any:
    """
    下载工资条PDF（模拟实现）
    """
    # 查询薪资记录
    record = db.query(SalaryRecord).options(
        joinedload(SalaryRecord.employee).joinedload(Employee.department),
        joinedload(SalaryRecord.employee).joinedload(Employee.position)
    ).filter(
        and_(
            SalaryRecord.id == record_id,
            SalaryRecord.employee_id == current_user.employee_id
        )
    ).first()
    
    if not record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="薪资记录不存在或无权限访问"
        )
    
    # 记录下载日志
    log_user_activity(
        db=db,
        user=current_user,
        action_type="下载工资条",
        description=f"下载{record.year}年{record.month:02d}月工资条",
        resource_type="salary_record",
        resource_id=record_id,
        ip_address=request.client.host if request.client else None
    )
    
    # TODO: 实际实现PDF生成
    # 这里返回模拟的下载链接
    return {
        "download_url": f"/api/v1/user/salary/records/{record_id}/payslip.pdf",
        "filename": f"工资条_{record.year}年{record.month:02d}月_{record.employee.name}.pdf",
        "generated_at": datetime.now(),
        "message": "工资条已生成，请点击链接下载"
    } 