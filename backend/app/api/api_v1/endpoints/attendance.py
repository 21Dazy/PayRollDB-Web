from typing import Any, List, Optional
from datetime import date

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from sqlalchemy import and_, func

from app.api.deps import get_current_hr_user, get_current_user, get_db
from app.models.user import User
from app.models.attendance import Attendance
from app.models.attendance_status import AttendanceStatus
from app.models.employee import Employee
from app.schemas.attendance import (
    AttendanceCreate, AttendanceUpdate, AttendanceResponse, 
    AttendanceDetailResponse, AttendanceStatusResponse,
    AttendanceBatchCreate, AttendanceStatResponse
)
from app.utils.log import log_operation

router = APIRouter()

# 考勤状态相关接口
@router.get("/status", response_model=List[AttendanceStatusResponse])
def read_attendance_status(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Any:
    """
    获取考勤状态列表
    """
    return db.query(AttendanceStatus).all()

# 考勤记录相关接口
@router.get("/", response_model=List[AttendanceDetailResponse])
def read_attendance(
    skip: int = 0,
    limit: int = 100,
    department_id: Optional[int] = None,
    employee_id: Optional[int] = None,
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    status_id: Optional[int] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Any:
    """
    获取考勤记录列表，支持筛选
    """
    query = db.query(Attendance).join(Employee)
    
    # 应用筛选条件
    if department_id is not None:
        query = query.filter(Employee.department_id == department_id)
    
    if employee_id is not None:
        query = query.filter(Attendance.employee_id == employee_id)
    
    if start_date is not None:
        query = query.filter(Attendance.date >= start_date)
    
    if end_date is not None:
        query = query.filter(Attendance.date <= end_date)
    
    if status_id is not None:
        query = query.filter(Attendance.status_id == status_id)
    
    return query.offset(skip).limit(limit).all()

@router.post("/", response_model=AttendanceResponse, status_code=status.HTTP_201_CREATED)
def create_attendance(
    *,
    db: Session = Depends(get_db),
    attendance_in: AttendanceCreate,
    current_user: User = Depends(get_current_hr_user)
) -> Any:
    """
    创建考勤记录
    """
    # 检查员工是否存在
    employee = db.query(Employee).filter(Employee.id == attendance_in.employee_id).first()
    if not employee:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="员工不存在"
        )
    
    # 检查考勤状态是否存在
    status = db.query(AttendanceStatus).filter(AttendanceStatus.id == attendance_in.status_id).first()
    if not status:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="考勤状态不存在"
        )
    
    # 检查该员工当天是否已有考勤记录
    existing = db.query(Attendance).filter(
        and_(
            Attendance.employee_id == attendance_in.employee_id,
            Attendance.date == attendance_in.date
        )
    ).first()
    
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="该员工在当天已有考勤记录"
        )
    
    # 创建考勤记录
    attendance = Attendance(**attendance_in.dict())
    db.add(attendance)
    db.commit()
    db.refresh(attendance)
    
    log_operation(
        db=db,
        user_id=current_user.id,
        operation_type="创建考勤记录",
        operation_detail=f"为员工 ID: {attendance.employee_id} 创建了 {attendance.date} 的考勤记录"
    )
    
    return attendance

@router.post("/batch", response_model=List[AttendanceResponse], status_code=status.HTTP_201_CREATED)
def create_batch_attendance(
    *,
    db: Session = Depends(get_db),
    batch_in: AttendanceBatchCreate,
    current_user: User = Depends(get_current_hr_user)
) -> Any:
    """
    批量创建考勤记录
    """
    # 检查考勤状态是否存在
    status = db.query(AttendanceStatus).filter(AttendanceStatus.id == batch_in.status_id).first()
    if not status:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="考勤状态不存在"
        )
    
    # 批量创建考勤记录
    result = []
    for employee_id in batch_in.employee_ids:
        # 检查员工是否存在
        employee = db.query(Employee).filter(Employee.id == employee_id).first()
        if not employee:
            continue
        
        # 检查该员工当天是否已有考勤记录
        existing = db.query(Attendance).filter(
            and_(
                Attendance.employee_id == employee_id,
                Attendance.date == batch_in.date
            )
        ).first()
        
        if existing:
            continue
        
        # 创建考勤记录
        attendance = Attendance(
            employee_id=employee_id,
            date=batch_in.date,
            status_id=batch_in.status_id,
            overtime_hours=batch_in.overtime_hours,
            remarks=batch_in.remarks
        )
        db.add(attendance)
        result.append(attendance)
    
    db.commit()
    for item in result:
        db.refresh(item)
    
    log_operation(
        db=db,
        user_id=current_user.id,
        operation_type="批量创建考勤记录",
        operation_detail=f"为 {len(result)} 名员工批量创建了 {batch_in.date} 的考勤记录"
    )
    
    return result

@router.get("/{attendance_id}", response_model=AttendanceDetailResponse)
def read_attendance_detail(
    attendance_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Any:
    """
    获取考勤记录详情
    """
    attendance = db.query(Attendance).filter(Attendance.id == attendance_id).first()
    if not attendance:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="考勤记录不存在"
        )
    
    return attendance

@router.put("/{attendance_id}", response_model=AttendanceResponse)
def update_attendance(
    *,
    db: Session = Depends(get_db),
    attendance_id: int,
    attendance_in: AttendanceUpdate,
    current_user: User = Depends(get_current_hr_user)
) -> Any:
    """
    更新考勤记录
    """
    attendance = db.query(Attendance).filter(Attendance.id == attendance_id).first()
    if not attendance:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="考勤记录不存在"
        )
    
    update_data = attendance_in.dict(exclude_unset=True)
    
    # 如果更新了考勤状态，检查状态是否存在
    if "status_id" in update_data:
        status = db.query(AttendanceStatus).filter(AttendanceStatus.id == update_data["status_id"]).first()
        if not status:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="考勤状态不存在"
            )
    
    for key, value in update_data.items():
        setattr(attendance, key, value)
    
    db.add(attendance)
    db.commit()
    db.refresh(attendance)
    
    log_operation(
        db=db,
        user_id=current_user.id,
        operation_type="更新考勤记录",
        operation_detail=f"更新了员工 ID: {attendance.employee_id} 在 {attendance.date} 的考勤记录"
    )
    
    return attendance

@router.delete("/{attendance_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_attendance(
    *,
    db: Session = Depends(get_db),
    attendance_id: int,
    current_user: User = Depends(get_current_hr_user)
) -> None:
    """
    删除考勤记录
    """
    attendance = db.query(Attendance).filter(Attendance.id == attendance_id).first()
    if not attendance:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="考勤记录不存在"
        )
    
    employee_id = attendance.employee_id
    attendance_date = attendance.date
    
    db.delete(attendance)
    db.commit()
    
    log_operation(
        db=db,
        user_id=current_user.id,
        operation_type="删除考勤记录",
        operation_detail=f"删除了员工 ID: {employee_id} 在 {attendance_date} 的考勤记录"
    )
    
    return None

@router.get("/employees/{employee_id}/stats", response_model=AttendanceStatResponse)
def get_employee_attendance_stats(
    employee_id: int,
    year: int,
    month: Optional[int] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Any:
    """
    获取员工考勤统计
    """
    # 检查员工是否存在
    employee = db.query(Employee).filter(Employee.id == employee_id).first()
    if not employee:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="员工不存在"
        )
    
    # 构建查询条件
    query = db.query(
        Attendance, AttendanceStatus
    ).join(
        AttendanceStatus, Attendance.status_id == AttendanceStatus.id
    ).filter(
        Attendance.employee_id == employee_id,
        func.extract('year', Attendance.date) == year
    )
    
    if month:
        query = query.filter(func.extract('month', Attendance.date) == month)
    
    # 执行查询
    results = query.all()
    
    # 统计不同考勤状态的天数
    normal_days = sum(1 for r in results if r[1].name == '正常')
    late_days = sum(1 for r in results if r[1].name == '迟到')
    early_leave_days = sum(1 for r in results if r[1].name == '早退')
    absent_days = sum(1 for r in results if r[1].name == '缺勤')
    sick_leave_days = sum(1 for r in results if r[1].name == '病假')
    personal_leave_days = sum(1 for r in results if r[1].name == '事假')
    annual_leave_days = sum(1 for r in results if r[1].name == '年假')
    
    # 计算加班总时长
    overtime_hours = sum(r[0].overtime_hours for r in results)
    
    return {
        "normal_days": normal_days,
        "late_days": late_days,
        "early_leave_days": early_leave_days,
        "absent_days": absent_days,
        "sick_leave_days": sick_leave_days,
        "personal_leave_days": personal_leave_days,
        "annual_leave_days": annual_leave_days,
        "overtime_hours": overtime_hours
    } 