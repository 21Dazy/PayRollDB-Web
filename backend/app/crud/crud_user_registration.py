from typing import List, Optional
from datetime import datetime, timedelta
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import and_, or_

from app.crud.base import CRUDBase
from app.models.user_registration import UserRegistration, UserPermission, EmployeeChangeRequest
from app.models.user import User
from app.models.employee import Employee
from app.models.department import Department
from app.models.position import Position
from app.schemas.user_registration import (
    UserRegistrationRequest, 
    RegistrationApprovalRequest,
    ChangeRequestCreate,
    EmployeeVerifyRequest
)
from app.core.security import get_password_hash, verify_password

class CRUDUserRegistration(CRUDBase[UserRegistration, UserRegistrationRequest, None]):
    
    def create_registration(self, db: Session, *, obj_in: UserRegistrationRequest, status: str = "pending") -> UserRegistration:
        """创建用户注册申请"""
        db_obj = UserRegistration(
            username=obj_in.username,
            password=get_password_hash(obj_in.password),
            real_name=obj_in.real_name,
            id_card=obj_in.id_card or "",  # 确保id_card不为None
            phone=obj_in.phone,
            email=obj_in.email,
            employee_id=obj_in.employee_id,
            verification_code=obj_in.verification_code,
            verification_expires=datetime.now() + timedelta(minutes=30) if obj_in.verification_code else None,
            status=status
        )
        
        # 不再添加紧急联系人信息，因为UserRegistration模型中没有这个字段
        
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj
    
    def verify_employee(self, db: Session, *, verify_data: EmployeeVerifyRequest) -> Optional[Employee]:
        """验证员工信息"""
        query = db.query(Employee).filter(Employee.status == True)
        
        # 如果提供了员工ID，按ID和姓名匹配
        if verify_data.employee_id:
            employee = query.filter(
                and_(
                    Employee.id == verify_data.employee_id,
                    Employee.name == verify_data.real_name
                )
            ).first()
        # 如果提供了身份证，按身份证和姓名匹配
        elif verify_data.id_card:
            employee = query.filter(
                and_(
                    Employee.id_card == verify_data.id_card,
                    Employee.name == verify_data.real_name
                )
            ).first()
        else:
            return None
            
        return employee
    
    def check_username_exists(self, db: Session, *, username: str) -> bool:
        """检查用户名是否已存在"""
        # 检查已注册的用户
        existing_user = db.query(User).filter(User.username == username).first()
        if existing_user:
            return True
            
        # 检查待审核的注册申请
        pending_registration = db.query(UserRegistration).filter(
            and_(
                UserRegistration.username == username,
                UserRegistration.status == "pending"
            )
        ).first()
        return pending_registration is not None
    
    def check_employee_bound(self, db: Session, *, employee_id: int) -> bool:
        """检查员工是否已绑定用户"""
        # 检查已有用户绑定
        existing_user = db.query(User).filter(User.employee_id == employee_id).first()
        if existing_user:
            return True
            
        # 检查待审核的绑定申请
        pending_registration = db.query(UserRegistration).filter(
            and_(
                UserRegistration.employee_id == employee_id,
                UserRegistration.status == "pending"
            )
        ).first()
        return pending_registration is not None
    
    def get_registrations_with_employee_info(
        self, 
        db: Session, 
        *, 
        skip: int = 0, 
        limit: int = 100,
        status: Optional[str] = None
    ) -> List[UserRegistration]:
        """获取带员工信息的注册申请列表"""
        query = db.query(UserRegistration).options(
            joinedload(UserRegistration.employee).joinedload(Employee.department),
            joinedload(UserRegistration.employee).joinedload(Employee.position)
        )
        
        if status:
            query = query.filter(UserRegistration.status == status)
            
        return query.offset(skip).limit(limit).all()
    
    def approve_registration(
        self, 
        db: Session, 
        *, 
        registration_id: int,
        admin_id: int,
        approval_data: RegistrationApprovalRequest
    ) -> Optional[UserRegistration]:
        """审核注册申请"""
        registration = db.query(UserRegistration).filter(UserRegistration.id == registration_id).first()
        if not registration:
            return None
            
        registration.admin_id = admin_id
        registration.admin_remarks = approval_data.remarks
        
        if approval_data.action == "approve":
            registration.status = "approved"
            
            # 创建用户账号
            user = User(
                username=registration.username,
                password=registration.password,  # 已经是加密的
                employee_id=registration.employee_id,
                role="employee",
                is_active=True
            )
            db.add(user)
            db.flush()  # 获取用户ID
            
            # 分配默认权限
            self._assign_default_permissions(db, user.id, admin_id)
            
        elif approval_data.action == "reject":
            registration.status = "rejected"
            
        db.commit()
        db.refresh(registration)
        return registration
    
    def _assign_default_permissions(self, db: Session, user_id: int, approver_id: int) -> None:
        """
        为新创建的用户分配默认权限
        """
        from app.models.user_registration import UserPermission
        from sqlalchemy import and_
        
        # 默认权限列表 - 普通员工权限
        default_permissions = [
            "view_salary",
            "view_attendance",
            "edit_profile",
            "view_payslip"
        ]
        
        # 添加默认权限
        for permission in default_permissions:
            # 检查权限是否已存在
            existing_permission = db.query(UserPermission).filter(
                and_(
                    UserPermission.user_id == user_id,
                    UserPermission.permission_type == permission
                )
            ).first()
            
            if not existing_permission:
                db_permission = UserPermission(
                    user_id=user_id,
                    permission_type=permission,
                    is_granted=True,
                    granted_by=approver_id,
                    granted_at=datetime.now()
                )
                db.add(db_permission)
        
        # 不需要commit，因为调用方会处理
    
    def get_by_username(self, db: Session, *, username: str) -> Optional[UserRegistration]:
        """根据用户名获取注册申请"""
        return db.query(UserRegistration).filter(UserRegistration.username == username).first()

class CRUDUserPermission(CRUDBase[UserPermission, None, None]):
    
    def get_user_permissions(self, db: Session, *, user_id: int) -> List[UserPermission]:
        """获取用户权限列表"""
        return db.query(UserPermission).filter(UserPermission.user_id == user_id).all()
    
    def check_permission(self, db: Session, *, user_id: int, permission_type: str) -> bool:
        """检查用户是否有指定权限"""
        permission = db.query(UserPermission).filter(
            and_(
                UserPermission.user_id == user_id,
                UserPermission.permission_type == permission_type,
                UserPermission.is_granted == True,
                or_(
                    UserPermission.expires_at.is_(None),
                    UserPermission.expires_at > datetime.now()
                )
            )
        ).first()
        return permission is not None

class CRUDChangeRequest(CRUDBase[EmployeeChangeRequest, ChangeRequestCreate, None]):
    
    def create_change_request(
        self, 
        db: Session, 
        *, 
        user_id: int,
        employee_id: int,
        obj_in: ChangeRequestCreate
    ) -> EmployeeChangeRequest:
        """创建信息变更申请"""
        # 获取当前值
        old_value = self._get_current_value(db, employee_id, obj_in.field_name)
        
        db_obj = EmployeeChangeRequest(
            employee_id=employee_id,
            user_id=user_id,
            change_type=obj_in.change_type,
            field_name=obj_in.field_name,
            old_value=old_value,
            new_value=obj_in.new_value,
            reason=obj_in.reason,
            status="pending"
        )
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj
    
    def _get_current_value(self, db: Session, employee_id: int, field_name: str) -> Optional[str]:
        """获取员工字段的当前值"""
        employee = db.query(Employee).filter(Employee.id == employee_id).first()
        if not employee:
            return None
            
        return str(getattr(employee, field_name, "")) if hasattr(employee, field_name) else None
    
    def get_user_change_requests(
        self, 
        db: Session, 
        *, 
        user_id: int,
        skip: int = 0,
        limit: int = 100
    ) -> List[EmployeeChangeRequest]:
        """获取用户的变更申请列表"""
        return db.query(EmployeeChangeRequest).filter(
            EmployeeChangeRequest.user_id == user_id
        ).offset(skip).limit(limit).all()

# 创建实例
user_registration = CRUDUserRegistration(UserRegistration)
user_permission = CRUDUserPermission(UserPermission)
change_request = CRUDChangeRequest(EmployeeChangeRequest) 