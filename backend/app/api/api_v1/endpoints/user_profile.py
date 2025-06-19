from typing import Any, List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import text, func
from datetime import datetime, timedelta

from app.api.deps import get_current_user, get_db
from app.models.user import User
from app.models.employee import Employee
from app.crud.crud_user_registration import change_request, user_permission
from app.schemas.user_registration import (
    ChangeRequestCreate,
    ChangeRequestResponse,
    EmergencyContactCreate,
    EmergencyContactResponse,
    UserSettingCreate,
    UserSettingUpdate,
    UserSettingResponse
)
from app.schemas.employee import EmployeeResponse
from app.utils.permissions import (
    get_current_employee_user,
    require_permission,
    log_user_activity,
    mask_sensitive_data,
    PermissionChecker
)

router = APIRouter()

# 个人信息相关API

@router.get("/profile")
def get_my_profile(
    *,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_employee_user),
    request: Request
) -> Any:
    """
    获取当前用户的个人信息
    """
    # 记录访问日志
    log_user_activity(
        db=db,
        user=current_user,
        action_type="查看个人信息",
        description="用户查看个人资料",
        ip_address=request.client.host if request.client else None
    )
    
    # 获取员工信息（包含部门和职位）
    employee = db.query(Employee).options(
        joinedload(Employee.department),
        joinedload(Employee.position)
    ).filter(Employee.id == current_user.employee_id).first()
    
    if not employee:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="员工信息不存在"
        )
    
    # 脱敏处理敏感信息
    profile_data = {
        "user_info": {
            "id": current_user.id,
            "username": current_user.username,
            "role": current_user.role,
            "is_active": current_user.is_active,
            "last_login": current_user.last_login
        },
        "employee_info": {
            "id": employee.id,
            "name": employee.name,
            "department_name": employee.department.name if employee.department else "",
            "position_name": employee.position.name if employee.position else "",
            "hire_date": employee.hire_date,
            "status": employee.status,
            "phone": employee.phone,
            "email": employee.email,
            "address": employee.address,
            "id_card": mask_sensitive_data(employee.id_card, "id_card") if employee.id_card else None,
            "bank_name": employee.bank_name,
            "bank_account": mask_sensitive_data(employee.bank_account, "bank_account") if employee.bank_account else None,
            "base_salary": float(employee.base_salary),
            "emergency_contact_name": employee.emergency_contact_name,
            "emergency_contact_phone": employee.emergency_contact_phone,
            "emergency_contact_relationship": employee.emergency_contact_relationship
        }
    }
    
    return profile_data

@router.get("/dashboard")
def get_my_dashboard_stats(
    *,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_employee_user),
    request: Request
) -> Any:
    """
    获取当前用户的个人统计信息（用于首页仪表板）
    """
    # 记录访问日志
    log_user_activity(
        db=db,
        user=current_user,
        action_type="查看个人统计",
        description="用户查看个人仪表板",
        ip_address=request.client.host if request.client else None
    )
    
    # 获取当前月份和年份
    current_month = datetime.now().month
    current_year = datetime.now().year
    
    # 统计当前月薪资总额
    salary_sql = """
    SELECT COALESCE(SUM(net_salary), 0) as current_month_salary,
           COUNT(*) as salary_records_count
    FROM salary_records 
    WHERE employee_id = :employee_id 
    AND month = :current_month 
    AND year = :current_year
    """
    
    salary_result = db.execute(text(salary_sql), {
        "employee_id": current_user.employee_id,
        "current_month": current_month,
        "current_year": current_year
    }).fetchone()
    
    # 统计当前月考勤情况
    attendance_sql = """
    SELECT 
        COUNT(*) as total_days,
        SUM(CASE WHEN ast.name = 'present' THEN 1 ELSE 0 END) as present_days,
        SUM(CASE WHEN ast.name = 'absent' THEN 1 ELSE 0 END) as absent_days,
        SUM(CASE WHEN ast.name = 'late' THEN 1 ELSE 0 END) as late_days,
        SUM(CASE WHEN ast.name = 'leave' THEN 1 ELSE 0 END) as leave_days
    FROM attendance a
    LEFT JOIN attendance_status ast ON a.status_id = ast.id
    WHERE a.employee_id = :employee_id 
    AND MONTH(a.date) = :current_month 
    AND YEAR(a.date) = :current_year
    """
    
    attendance_result = db.execute(text(attendance_sql), {
        "employee_id": current_user.employee_id,
        "current_month": current_month,
        "current_year": current_year
    }).fetchone()
    
    # 统计本年度薪资趋势（近6个月）
    salary_trend_sql = """
    SELECT 
        year,
        month,
        SUM(net_salary) as total_salary,
        SUM(base_salary) as base_salary,
        SUM(performance_bonus) as performance_salary,
        SUM(bonus) as bonus,
        SUM(transportation_allowance + meal_allowance) as allowance
    FROM salary_records 
    WHERE employee_id = :employee_id 
    AND (year = :current_year OR (year = :last_year AND month >= :start_month))
    AND (year < :current_year OR (year = :current_year AND month <= :current_month))
    GROUP BY year, month
    ORDER BY year DESC, month DESC
    LIMIT 6
    """
    
    # 计算6个月前的年月
    start_date = datetime.now() - timedelta(days=180)  # 大约6个月
    last_year = current_year - 1 if current_month <= 6 else current_year
    start_month = current_month - 6 if current_month > 6 else current_month + 6
    
    salary_trend_result = db.execute(text(salary_trend_sql), {
        "employee_id": current_user.employee_id,
        "current_year": current_year,
        "current_month": current_month,
        "last_year": last_year,
        "start_month": start_month
    }).fetchall()
    
    # 统计待处理事项（变更申请等）
    pending_sql = """
    SELECT COUNT(*) as pending_change_requests
    FROM employee_change_requests 
    WHERE user_id = :user_id 
    AND status = 'pending'
    """
    
    pending_result = db.execute(text(pending_sql), {
        "user_id": current_user.id
    }).fetchone()
    
    # 构建响应数据
    stats = {
        "current_month_salary": float(salary_result.current_month_salary or 0),
        "salary_records_count": int(salary_result.salary_records_count or 0),
        "attendance": {
            "total_days": int(attendance_result.total_days or 0),
            "present_days": int(attendance_result.present_days or 0),
            "absent_days": int(attendance_result.absent_days or 0),
            "late_days": int(attendance_result.late_days or 0),
            "leave_days": int(attendance_result.leave_days or 0),
            "attendance_rate": round((attendance_result.present_days or 0) / max(attendance_result.total_days or 1, 1) * 100, 1)
        },
        "pending_requests": int(pending_result.pending_change_requests or 0),
        "salary_trend": []
    }
    
    # 处理薪资趋势数据
    months = ['1月', '2月', '3月', '4月', '5月', '6月', '7月', '8月', '9月', '10月', '11月', '12月']
    salary_data = {
        "months": [],
        "basic": [],
        "performance": [],
        "bonus": [],
        "allowance": []
    }
    
    for row in salary_trend_result:
        month_name = months[row.month - 1]
        salary_data["months"].append(month_name)
        salary_data["basic"].append(float(row.base_salary or 0))
        salary_data["performance"].append(float(row.performance_salary or 0))
        salary_data["bonus"].append(float(row.bonus or 0))
        salary_data["allowance"].append(float(row.allowance or 0))
    
    stats["salary_trend"] = salary_data
    
    return stats

@router.get("/permissions")
def get_my_permissions(
    *,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Any:
    """
    获取当前用户的权限列表
    """
    permissions = user_permission.get_user_permissions(db=db, user_id=current_user.id)
    
    return {
        "user_id": current_user.id,
        "role": current_user.role,
        "permissions": [
            {
                "permission_type": perm.permission_type,
                "is_granted": perm.is_granted,
                "granted_at": perm.granted_at,
                "expires_at": perm.expires_at
            }
            for perm in permissions
        ]
    }

# 信息变更申请相关API

@router.post("/change-requests", response_model=ChangeRequestResponse)
def create_change_request(
    *,
    db: Session = Depends(get_db),
    request_data: ChangeRequestCreate,
    current_user: User = Depends(require_permission("edit_profile")),
    request: Request
) -> Any:
    """
    提交信息变更申请
    """
    if not current_user.employee_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="当前用户未绑定员工信息"
        )
    
    # 创建变更申请
    change_req = change_request.create_change_request(
        db=db,
        user_id=current_user.id,
        employee_id=current_user.employee_id,
        obj_in=request_data
    )
    
    # 记录操作日志
    log_user_activity(
        db=db,
        user=current_user,
        action_type="提交信息变更申请",
        description=f"申请修改{request_data.field_name}: {request_data.old_value} -> {request_data.new_value}",
        resource_type="change_request",
        resource_id=change_req.id,
        ip_address=request.client.host if request.client else None
    )
    
    return change_req

@router.get("/change-requests", response_model=List[ChangeRequestResponse])
def get_my_change_requests(
    *,
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(get_current_employee_user)
) -> Any:
    """
    获取当前用户的信息变更申请列表
    """
    requests = change_request.get_user_change_requests(
        db=db,
        user_id=current_user.id,
        skip=skip,
        limit=limit
    )
    
    return requests

@router.get("/change-requests/{request_id}", response_model=ChangeRequestResponse)
def get_change_request_detail(
    *,
    db: Session = Depends(get_db),
    request_id: int,
    current_user: User = Depends(get_current_employee_user)
) -> Any:
    """
    获取信息变更申请详情
    """
    change_req = change_request.get(db=db, id=request_id)
    if not change_req:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="申请记录不存在"
        )
    
    # 检查权限：只能查看自己的申请
    if change_req.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="无权限访问此申请记录"
        )
    
    return change_req

# 个人设置相关API

@router.get("/settings", response_model=List[UserSettingResponse])
def get_my_settings(
    *,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Any:
    """
    获取用户个人设置
    """
    from app.models.user_registration import UserSetting
    
    settings = db.query(UserSetting).filter(
        UserSetting.user_id == current_user.id
    ).all()
    
    return settings

@router.post("/settings", response_model=UserSettingResponse)
def create_user_setting(
    *,
    db: Session = Depends(get_db),
    setting_data: UserSettingCreate,
    current_user: User = Depends(get_current_user)
) -> Any:
    """
    创建用户设置
    """
    from app.models.user_registration import UserSetting
    
    # 检查设置是否已存在
    existing = db.query(UserSetting).filter(
        UserSetting.user_id == current_user.id,
        UserSetting.setting_key == setting_data.setting_key
    ).first()
    
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="设置项已存在，请使用更新接口"
        )
    
    setting = UserSetting(
        user_id=current_user.id,
        setting_key=setting_data.setting_key,
        setting_value=setting_data.setting_value,
        description=setting_data.description
    )
    db.add(setting)
    db.commit()
    db.refresh(setting)
    
    return setting

@router.put("/settings/{setting_key}", response_model=UserSettingResponse)
def update_user_setting(
    *,
    db: Session = Depends(get_db),
    setting_key: str,
    setting_data: UserSettingUpdate,
    current_user: User = Depends(get_current_user)
) -> Any:
    """
    更新用户设置
    """
    from app.models.user_registration import UserSetting
    
    setting = db.query(UserSetting).filter(
        UserSetting.user_id == current_user.id,
        UserSetting.setting_key == setting_key
    ).first()
    
    if not setting:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="设置项不存在"
        )
    
    setting.setting_value = setting_data.setting_value
    if setting_data.description is not None:
        setting.description = setting_data.description
    
    db.commit()
    db.refresh(setting)
    
    return setting

@router.delete("/settings/{setting_key}")
def delete_user_setting(
    *,
    db: Session = Depends(get_db),
    setting_key: str,
    current_user: User = Depends(get_current_user)
) -> Any:
    """
    删除用户设置
    """
    from app.models.user_registration import UserSetting
    
    setting = db.query(UserSetting).filter(
        UserSetting.user_id == current_user.id,
        UserSetting.setting_key == setting_key
    ).first()
    
    if not setting:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="设置项不存在"
        )
    
    db.delete(setting)
    db.commit()
    
    return {"message": "设置已删除"}

# 活动日志API

@router.get("/activity-logs")
def get_my_activity_logs(
    *,
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 20,
    action_type: Optional[str] = None,
    current_user: User = Depends(get_current_user)
) -> Any:
    """
    获取用户活动日志
    """
    # 直接使用SQL查询，避免模型类导入问题
    sql_query = """
    SELECT id, action_type, resource_type, resource_id, description, ip_address, created_at
    FROM user_activity_logs
    WHERE user_id = :user_id
    """
    
    params = {"user_id": current_user.id}
    
    if action_type:
        sql_query += " AND action_type = :action_type"
        params["action_type"] = action_type
    
    # 获取总数
    count_sql = """
    SELECT COUNT(*) as total
    FROM user_activity_logs
    WHERE user_id = :user_id
    """
    
    if action_type:
        count_sql += " AND action_type = :action_type"
    
    count_result = db.execute(text(count_sql), params).fetchone()
    total = count_result.total if count_result else 0
    
    # 添加排序和分页
    sql_query += " ORDER BY created_at DESC LIMIT :limit OFFSET :skip"
    params["limit"] = limit
    params["skip"] = skip
    
    # 执行查询
    result = db.execute(text(sql_query), params).fetchall()
    
    # 构建响应
    logs = []
    for row in result:
        logs.append({
            "id": row.id,
            "action_type": row.action_type,
            "description": row.description,
            "resource_type": row.resource_type,
            "resource_id": row.resource_id,
            "ip_address": row.ip_address,
            "created_at": row.created_at
        })
    
    return {
        "logs": logs,
        "total": total
    } 