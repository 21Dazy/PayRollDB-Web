from typing import Any, List, Optional
from datetime import datetime, date, timedelta
from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import and_, desc, func, extract, between

from app.api.deps import get_db
from app.models.user import User
from app.models.attendance import Attendance
from app.models.attendance_status import AttendanceStatus
from app.models.employee import Employee
from app.utils.permissions import (
    require_permission,
    get_current_employee_user,
    log_user_activity,
    PermissionChecker
)

router = APIRouter()

@router.get("/records")
def get_my_attendance_records(
    *,
    db: Session = Depends(get_db),
    year: Optional[int] = None,
    month: Optional[int] = None,
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    status: Optional[str] = None,
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(require_permission("view_attendance")),
    request: Request
) -> Any:
    """
    获取当前用户的考勤记录列表
    """
    # 记录访问日志
    log_user_activity(
        db=db,
        user=current_user,
        action_type="查看考勤记录",
        description="用户查看考勤记录列表",
        ip_address=request.client.host if request.client else None
    )
    
    # 构建查询条件，预加载关联的status数据
    query = db.query(Attendance).options(
        joinedload(Attendance.status)
    ).filter(
        Attendance.employee_id == current_user.employee_id
    )
    
    # 按年份筛选
    if year:
        query = query.filter(extract('year', Attendance.date) == year)
    
    # 按月份筛选
    if month:
        query = query.filter(extract('month', Attendance.date) == month)
    
    # 按日期范围筛选
    if start_date and end_date:
        query = query.filter(between(Attendance.date, start_date, end_date))
    elif start_date:
        query = query.filter(Attendance.date >= start_date)
    elif end_date:
        query = query.filter(Attendance.date <= end_date)
    
    # 按状态筛选
    if status:
        query = query.join(AttendanceStatus).filter(AttendanceStatus.name == status)
    
    # 按日期倒序排列
    total = query.count()
    records = query.order_by(desc(Attendance.date)).offset(skip).limit(limit).all()
    
    # 格式化返回数据
    attendance_list = []
    for record in records:
        # 根据考勤状态获取状态信息
        status_name = record.status.name if record.status else "未知"
        
        attendance_list.append({
            "id": record.id,
            "date": record.date,
            "weekday": record.date.strftime("%A"),
            "status": status_name,
            "status_id": record.status_id,
            "overtime_hours": float(record.overtime_hours) if record.overtime_hours else 0,
            "remarks": record.remarks,
            "created_at": record.created_at,
            "updated_at": record.updated_at
        })
    
    return {
        "records": attendance_list,
        "total": total,
        "page": skip // limit + 1,
        "size": limit
    }

@router.get("/statistics")
def get_attendance_statistics(
    *,
    db: Session = Depends(get_db),
    year: Optional[int] = None,
    month: Optional[int] = None,
    current_user: User = Depends(require_permission("view_attendance"))
) -> Any:
    """
    获取考勤统计信息
    """
    current_year = year or datetime.now().year
    current_month = month or datetime.now().month
    
    # 构建查询条件，预加载关联的status数据
    query = db.query(Attendance).options(
        joinedload(Attendance.status)
    ).filter(
        Attendance.employee_id == current_user.employee_id
    )
    
    if year:
        query = query.filter(extract('year', Attendance.date) == year)
        if month:
            query = query.filter(extract('month', Attendance.date) == month)
    else:
        # 默认查询当前年度
        query = query.filter(extract('year', Attendance.date) == current_year)
    
    records = query.all()
    
    if not records:
        return {
            "period": {
                "year": current_year,
                "month": current_month if month else None
            },
            "summary": {
                "total_days": 0,
                "work_days": 0,
                "normal_days": 0,
                "late_days": 0,
                "early_leave_days": 0,
                "absent_days": 0,
                "overtime_days": 0,
                "total_work_hours": 0,
                "total_overtime_hours": 0,
                "total_late_minutes": 0,
                "total_early_leave_minutes": 0
            },
            "monthly_summary": [],
            "status_breakdown": {}
        }
    
    # 基本统计
    total_days = len(records)
    # 根据实际的考勤状态名称进行统计
    work_days = len([r for r in records if r.status.name in ['正常', '迟到', '早退', '迟到早退']])
    normal_days = len([r for r in records if r.status.name == '正常'])
    late_days = len([r for r in records if r.status.name in ['迟到', '迟到早退']])
    early_leave_days = len([r for r in records if r.status.name in ['早退', '迟到早退']])
    absent_days = len([r for r in records if r.status.name == '缺勤'])
    overtime_days = len([r for r in records if r.overtime_hours and r.overtime_hours > 0])
    
    # 时间统计 - 由于没有clock_in/clock_out字段，暂时只统计加班时间
    total_overtime_hours = 0
    
    for record in records:
        if record.overtime_hours:
            total_overtime_hours += float(record.overtime_hours)
    
    # 状态分布
    status_breakdown = {}
    for record in records:
        status = record.status.name if record.status else "未知"
        if status not in status_breakdown:
            status_breakdown[status] = 0
        status_breakdown[status] += 1
    
    # 月度汇总（如果查询的是年度数据）
    monthly_summary = []
    if not month:
        # 按月分组统计
        monthly_data = {}
        for record in records:
            month_key = record.date.month
            if month_key not in monthly_data:
                monthly_data[month_key] = []
            monthly_data[month_key].append(record)
        
        for month_num in range(1, 13):
            if month_num in monthly_data:
                month_records = monthly_data[month_num]
                month_work_days = len([r for r in month_records if r.status.name in ['正常', '迟到', '早退', '迟到早退']])
                month_normal_days = len([r for r in month_records if r.status.name == '正常'])
                month_late_days = len([r for r in month_records if r.status.name in ['迟到', '迟到早退']])
                month_absent_days = len([r for r in month_records if r.status.name == '缺勤'])
                
                monthly_summary.append({
                    "month": month_num,
                    "total_days": len(month_records),
                    "work_days": month_work_days,
                    "normal_days": month_normal_days,
                    "late_days": month_late_days,
                    "absent_days": month_absent_days,
                    "attendance_rate": round(month_work_days / len(month_records) * 100, 2) if month_records else 0
                })
            else:
                monthly_summary.append({
                    "month": month_num,
                    "total_days": 0,
                    "work_days": 0,
                    "normal_days": 0,
                    "late_days": 0,
                    "absent_days": 0,
                    "attendance_rate": 0
                })
    
    return {
        "period": {
            "year": current_year,
            "month": current_month if month else None
        },
        "summary": {
            "total_days": total_days,
            "work_days": work_days,
            "normal_days": normal_days,
            "late_days": late_days,
            "early_leave_days": early_leave_days,
            "absent_days": absent_days,
            "overtime_days": overtime_days,
            "total_work_hours": 0,  # 由于没有打卡时间，设为0
            "total_overtime_hours": round(total_overtime_hours, 2),
            "total_late_minutes": 0,  # 由于没有具体迟到时间，设为0
            "total_early_leave_minutes": 0,  # 由于没有具体早退时间，设为0
            "attendance_rate": round(work_days / total_days * 100, 2) if total_days > 0 else 0,
            "punctuality_rate": round(normal_days / work_days * 100, 2) if work_days > 0 else 0
        },
        "monthly_summary": monthly_summary,
        "status_breakdown": status_breakdown
    }

@router.get("/calendar")
def get_attendance_calendar(
    *,
    db: Session = Depends(get_db),
    year: int,
    month: int,
    current_user: User = Depends(require_permission("view_attendance"))
) -> Any:
    """
    获取指定月份的考勤日历数据
    """
    # 构建查询条件，预加载关联的status数据
    query = db.query(Attendance).options(
        joinedload(Attendance.status)
    ).filter(
        and_(
            Attendance.employee_id == current_user.employee_id,
            extract('year', Attendance.date) == year,
            extract('month', Attendance.date) == month
        )
    )
    
    # 构建日历数据
    calendar_data = {}
    records_list = query.all()
    for record in records_list:
        day = record.date.day
        
        calendar_data[day] = {
            "date": record.date,
            "status": record.status.name if record.status else "未知",
            "status_id": record.status_id,
            "overtime_hours": float(record.overtime_hours) if record.overtime_hours else 0,
            "remarks": record.remarks
        }
    
    return {
        "year": year,
        "month": month,
        "calendar_data": calendar_data,
        "total_records": len(records_list)
    }

@router.get("/recent")
def get_recent_attendance(
    *,
    db: Session = Depends(get_db),
    days: int = 7,
    current_user: User = Depends(require_permission("view_attendance"))
) -> Any:
    """
    获取最近几天的考勤记录
    """
    end_date = date.today()
    start_date = end_date - timedelta(days=days-1)
    
    # 构建查询条件，预加载关联的status数据
    query = db.query(Attendance).options(
        joinedload(Attendance.status)
    ).filter(
        and_(
            Attendance.employee_id == current_user.employee_id,
            between(Attendance.date, start_date, end_date)
        )
    )
    
    records = query.order_by(desc(Attendance.date)).all()
    
    # 格式化返回数据
    recent_records = []
    for record in records:
        recent_records.append({
            "date": record.date,
            "weekday": record.date.strftime("%A"),
            "status": record.status.name if record.status else "未知",
            "status_id": record.status_id,
            "overtime_hours": float(record.overtime_hours) if record.overtime_hours else 0,
            "remarks": record.remarks
        })
    
    return {
        "period": {
            "start_date": start_date,
            "end_date": end_date,
            "days": days
        },
        "records": recent_records,
        "total": len(recent_records)
    }

@router.get("/summary")
def get_attendance_summary(
    *,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission("view_attendance"))
) -> Any:
    """
    获取考勤概览信息
    """
    today = date.today()
    current_year = today.year
    current_month = today.month
    
    # 今日考勤
    today_record = db.query(Attendance).options(
        joinedload(Attendance.status)
    ).filter(
        and_(
            Attendance.employee_id == current_user.employee_id,
            Attendance.date == today
        )
    ).first()
    
    # 本月考勤统计
    month_records = db.query(Attendance).options(
        joinedload(Attendance.status)
    ).filter(
        and_(
            Attendance.employee_id == current_user.employee_id,
            extract('year', Attendance.date) == current_year,
            extract('month', Attendance.date) == current_month
        )
    ).all()
    
    # 计算本月统计
    month_work_days = len([r for r in month_records if r.status.name in ['正常', '迟到', '早退', '迟到早退']])
    month_late_days = len([r for r in month_records if r.status.name in ['迟到', '迟到早退']])
    month_absent_days = len([r for r in month_records if r.status.name == '缺勤'])
    
    return {
        "today": {
            "date": today,
            "has_record": today_record is not None,
            "status": today_record.status.name if today_record and today_record.status else None,
            "status_id": today_record.status_id if today_record else None,
            "overtime_hours": float(today_record.overtime_hours) if today_record and today_record.overtime_hours else 0,
            "remarks": today_record.remarks if today_record else None
        },
        "current_month": {
            "year": current_year,
            "month": current_month,
            "total_days": len(month_records),
            "work_days": month_work_days,
            "late_days": month_late_days,
            "absent_days": month_absent_days,
            "attendance_rate": round(month_work_days / len(month_records) * 100, 2) if month_records else 0
        }
    } 