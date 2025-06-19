from typing import List, Optional
from datetime import datetime
from fastapi import Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import text

from app.api.deps import get_current_user, get_db
from app.models.user import User
from app.crud.crud_user_registration import user_permission
from app.utils.log import log_operation

def require_permission(permission_type: str):
    """权限检查装饰器"""
    def permission_checker(
        current_user: User = Depends(get_current_user),
        db: Session = Depends(get_db)
    ) -> User:
        # 管理员和HR默认有所有权限
        if current_user.role in ["admin", "hr"]:
            return current_user
            
        # 检查普通用户权限
        if not user_permission.check_permission(
            db=db, 
            user_id=current_user.id, 
            permission_type=permission_type
        ):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"没有权限访问此资源，需要权限: {permission_type}"
            )
        return current_user
    return permission_checker

def get_current_employee_user(
    current_user: User = Depends(get_current_user),
) -> User:
    """获取当前员工用户（必须绑定了员工信息）"""
    if not current_user.employee_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="当前用户未绑定员工信息"
        )
    return current_user

def log_user_activity(
    db: Session,
    user: User,
    action_type: str,
    description: str,
    resource_type: Optional[str] = None,
    resource_id: Optional[int] = None,
    ip_address: Optional[str] = None,
    user_agent: Optional[str] = None
):
    """记录用户活动日志"""
    # 使用原生SQL插入数据，避免模型类导入问题
    sql = """
    INSERT INTO user_activity_logs 
    (user_id, action_type, resource_type, resource_id, description, ip_address, user_agent, created_at)
    VALUES (:user_id, :action_type, :resource_type, :resource_id, :description, :ip_address, :user_agent, :created_at)
    """
    
    try:
        db.execute(
            text(sql),
            {
                "user_id": user.id,
                "action_type": action_type,
                "resource_type": resource_type,
                "resource_id": resource_id,
                "description": description,
                "ip_address": ip_address,
                "user_agent": user_agent,
                "created_at": datetime.now()
            }
        )
        db.commit()
    except Exception as e:
        db.rollback()
        print(f"记录用户活动日志失败: {str(e)}")
        # 不抛出异常，避免影响主流程

def mask_sensitive_data(data: str, mask_type: str = "default") -> str:
    """数据脱敏处理"""
    if not data:
        return data
        
    if mask_type == "bank_account":
        if len(data) <= 8:
            return data
        return data[:4] + '*' * (len(data) - 8) + data[-4:]
    elif mask_type == "id_card":
        if len(data) != 18:
            return data
        return data[:6] + '*' * 8 + data[-4:]
    elif mask_type == "phone":
        if len(data) != 11:
            return data
        return data[:3] + '*' * 4 + data[-4:]
    else:
        # 默认脱敏：保留前2位和后2位
        if len(data) <= 4:
            return data
        return data[:2] + '*' * (len(data) - 4) + data[-2:]

def generate_verification_code() -> str:
    """生成6位数字验证码"""
    import random
    return ''.join([str(random.randint(0, 9)) for _ in range(6)])

def is_verification_code_valid(
    code: str, 
    stored_code: str, 
    expires_at: Optional[datetime]
) -> bool:
    """验证验证码是否有效"""
    if not code or not stored_code:
        return False
        
    if code != stored_code:
        return False
        
    if expires_at and datetime.now() > expires_at:
        return False
        
    return True

def check_rate_limit(
    db: Session,
    user_id: int,
    action_type: str,
    max_attempts: int = 5,
    time_window_minutes: int = 60
) -> bool:
    """检查操作频率限制"""
    from sqlalchemy import text
    from datetime import datetime, timedelta
    
    # 使用原生SQL查询，避免模型类导入问题
    sql = """
    SELECT COUNT(*) as count
    FROM user_activity_logs
    WHERE user_id = :user_id
    AND action_type = :action_type
    AND created_at >= :time_threshold
    """
    
    try:
        time_threshold = datetime.now() - timedelta(minutes=time_window_minutes)
        result = db.execute(
            text(sql),
            {
                "user_id": user_id,
                "action_type": action_type,
                "time_threshold": time_threshold
            }
        ).fetchone()
        
        count = result.count if result else 0
        return count < max_attempts
    except Exception as e:
        print(f"检查操作频率限制失败: {str(e)}")
        # 出错时默认通过检查
        return True

def validate_phone_number(phone: str) -> bool:
    """验证手机号格式"""
    import re
    pattern = r"^1[3-9]\d{9}$"
    return bool(re.match(pattern, phone))

def validate_id_card(id_card: str) -> bool:
    """验证身份证号格式"""
    import re
    pattern = r"^\d{17}[\dXx]$"
    if not re.match(pattern, id_card):
        return False
        
    # 简单的校验位验证
    weights = [7, 9, 10, 5, 8, 4, 2, 1, 6, 3, 7, 9, 10, 5, 8, 4, 2]
    check_codes = ['1', '0', 'X', '9', '8', '7', '6', '5', '4', '3', '2']
    
    try:
        sum_val = sum(int(id_card[i]) * weights[i] for i in range(17))
        check_code = check_codes[sum_val % 11]
        return id_card[-1].upper() == check_code
    except (ValueError, IndexError):
        return False

class PermissionChecker:
    """权限检查器类"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def has_salary_permission(self, user: User) -> bool:
        """检查薪资查看权限"""
        return user.role in ["admin", "hr"] or user_permission.check_permission(
            db=self.db, user_id=user.id, permission_type="view_salary"
        )
    
    def has_attendance_permission(self, user: User) -> bool:
        """检查考勤查看权限"""
        return user.role in ["admin", "hr"] or user_permission.check_permission(
            db=self.db, user_id=user.id, permission_type="view_attendance"
        )
    
    def has_profile_edit_permission(self, user: User) -> bool:
        """检查个人信息编辑权限"""
        return user.role in ["admin", "hr"] or user_permission.check_permission(
            db=self.db, user_id=user.id, permission_type="edit_profile"
        )
    
    def has_payslip_permission(self, user: User) -> bool:
        """检查工资条下载权限"""
        return user.role in ["admin", "hr"] or user_permission.check_permission(
            db=self.db, user_id=user.id, permission_type="view_payslip"
        )
    
    def can_access_employee_data(self, user: User, employee_id: int) -> bool:
        """检查是否可以访问指定员工的数据"""
        # 管理员和HR可以访问所有员工数据
        if user.role in ["admin", "hr"]:
            return True
            
        # 普通用户只能访问自己的数据
        return user.employee_id == employee_id 