from typing import Any, List
from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session

from app.api.deps import get_current_admin, get_current_user, get_db
from app.models.user import User
from app.crud.crud_user_registration import user_registration, user_permission, change_request
from app.schemas.user_registration import (
    EmployeeVerifyRequest,
    EmployeeVerifyResponse,
    UserRegistrationRequest,
    UserRegistrationResponse,
    RegistrationListResponse,
    RegistrationApprovalRequest,
    SendVerificationCodeRequest,
    VerifyCodeRequest
)
from app.utils.permissions import (
    log_user_activity,
    generate_verification_code,
    is_verification_code_valid,
    check_rate_limit,
    validate_phone_number,
    validate_id_card
)
from app.utils.log import log_operation

router = APIRouter()

@router.post("/verify-employee", response_model=EmployeeVerifyResponse)
def verify_employee_info(
    *,
    db: Session = Depends(get_db),
    verify_data: EmployeeVerifyRequest,
    request: Request
) -> Any:
    """
    验证员工信息是否存在且可绑定
    """
    # 验证输入数据
    if verify_data.id_card and not validate_id_card(verify_data.id_card):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="身份证号格式不正确"
        )
    
    # 查找员工
    employee = user_registration.verify_employee(db=db, verify_data=verify_data)
    
    if not employee:
        return EmployeeVerifyResponse(
            found=False,
            message="未找到匹配的员工信息，请检查姓名和身份证号/工号是否正确"
        )
    
    # 检查是否已绑定用户
    if user_registration.check_employee_bound(db=db, employee_id=employee.id):
        return EmployeeVerifyResponse(
            found=False,
            message="该员工已绑定用户账号或有待审核的绑定申请"
        )
    
    return EmployeeVerifyResponse(
        found=True,
        employee_id=employee.id,
        employee_name=employee.name,
        department_name=employee.department.name if employee.department else "",
        position_name=employee.position.name if employee.position else "",
        message="员工信息验证成功，可以进行注册"
    )

@router.post("/send-verification-code")
def send_verification_code(
    *,
    db: Session = Depends(get_db),
    request_data: SendVerificationCodeRequest,
    request: Request
) -> Any:
    """
    发送手机验证码
    """
    # 验证手机号格式
    if not validate_phone_number(request_data.phone):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="手机号格式不正确"
        )
    
    # 生成验证码
    code = generate_verification_code()
    
    # 在实际应用中，这里应该发送短信验证码
    # 这里为了测试方便，直接返回验证码
    print(f"发送验证码到 {request_data.phone}: {code}")
    
    return {
        "message": "验证码已发送",
        "debug_code": code  # 直接返回验证码，方便测试
    }

@router.post("/register", response_model=UserRegistrationResponse)
def register_user(
    *,
    db: Session = Depends(get_db),
    registration_data: UserRegistrationRequest,
    request: Request
) -> Any:
    """
    用户注册申请
    """
    # 验证输入数据
    if registration_data.id_card and not validate_id_card(registration_data.id_card):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="身份证号格式不正确"
        )
    
    if not validate_phone_number(registration_data.phone):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="手机号格式不正确"
        )
    
    # 检查用户名是否已存在
    if user_registration.check_username_exists(db=db, username=registration_data.username):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="用户名已存在或有待审核的注册申请"
        )
    
    # 如果指定了员工ID，检查是否已绑定
    if registration_data.employee_id:
        if user_registration.check_employee_bound(db=db, employee_id=registration_data.employee_id):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="该员工已绑定用户账号或有待审核的绑定申请"
            )
    
    # TODO: 验证验证码
    # if registration_data.verification_code:
    #     if not verify_verification_code(registration_data.phone, registration_data.verification_code):
    #         raise HTTPException(
    #             status_code=status.HTTP_400_BAD_REQUEST,
    #             detail="验证码错误或已过期"
    #         )
    
    # 创建注册申请
    registration = user_registration.create_registration(db=db, obj_in=registration_data)
    
    return UserRegistrationResponse(
        id=registration.id,
        username=registration.username,
        real_name=registration.real_name,
        phone=registration.phone,
        email=registration.email,
        status=registration.status,
        employee_id=registration.employee_id,
        created_at=registration.created_at,
        message="注册申请已提交，请等待管理员审核"
    )

@router.post("/register-direct", response_model=UserRegistrationResponse)
def register_user_direct(
    *,
    db: Session = Depends(get_db),
    registration_data: UserRegistrationRequest,
    request: Request
) -> Any:
    """
    用户注册申请 - 直接创建用户，不需要审核
    """
    # 导入User类
    from app.models.user import User
    
    # 记录请求数据(仅开发环境)
    print(f"注册请求数据: {registration_data.dict(exclude={'password'})}")
    
    # 验证输入数据
    if registration_data.id_card and not validate_id_card(registration_data.id_card):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="身份证号格式不正确"
        )
    
    if not validate_phone_number(registration_data.phone):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="手机号格式不正确"
        )
    
    # 检查用户名是否已存在于users表中
    existing_user = db.query(User).filter(User.username == registration_data.username).first()
    if existing_user:
        # 如果用户已存在，直接返回成功响应
        print(f"用户名 {registration_data.username} 已存在，返回已有用户ID: {existing_user.id}")
        return UserRegistrationResponse(
            id=existing_user.id,
            username=existing_user.username,
            real_name=registration_data.real_name,
            phone=registration_data.phone,
            email=registration_data.email,
            status="approved",
            employee_id=registration_data.employee_id,
            created_at=existing_user.created_at,
            message="用户已存在，可以直接登录"
        )
    
    # 检查用户名是否已存在于注册申请中
    if user_registration.check_username_exists(db=db, username=registration_data.username):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="用户名已存在或有待审核的注册申请"
        )
    
    # 如果指定了员工ID，检查是否已绑定
    if registration_data.employee_id:
        if user_registration.check_employee_bound(db=db, employee_id=registration_data.employee_id):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="该员工已绑定用户账号或有待审核的绑定申请"
            )
    
    # 注意：为了简化流程，我们不检查验证码
    
    try:
        # 创建注册申请，但状态为已批准
        registration = user_registration.create_registration(
            db=db, 
            obj_in=registration_data,
            status="approved"  # 直接设置为已批准状态
        )
        
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
        try:
            user_registration._assign_default_permissions(db, user.id, user.id)  # 使用用户自己的ID作为授权人
        except Exception as perm_error:
            print(f"分配权限时出错，但继续创建用户: {str(perm_error)}")
            # 权限分配错误不影响用户创建
        
        # 提交事务
        db.commit()
        
        # 记录操作日志
        try:
            log_operation(
                db=db,
                user_id=user.id,
                operation_type="user_register",
                operation_detail=f"用户 {user.username} 完成注册",
                ip_address=request.client.host if request.client else None
            )
        except Exception as log_error:
            print(f"记录操作日志时出错: {str(log_error)}")
            # 日志记录错误不影响用户创建
        
        return UserRegistrationResponse(
            id=user.id,  # 返回用户ID而不是注册申请ID
            username=registration.username,
            real_name=registration.real_name,
            phone=registration.phone,
            email=registration.email,
            status="approved",
            employee_id=registration.employee_id,
            created_at=registration.created_at,
            message="注册成功，账号已创建"
        )
    except Exception as e:
        db.rollback()
        print(f"注册失败: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"注册失败: {str(e)}"
        )

@router.get("/registrations", response_model=List[RegistrationListResponse])
def get_registration_list(
    *,
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 100,
    status: str = None,
    current_user: User = Depends(get_current_admin)
) -> Any:
    """
    获取注册申请列表（管理员）
    """
    registrations = user_registration.get_registrations_with_employee_info(
        db=db, skip=skip, limit=limit, status=status
    )
    
    result = []
    for reg in registrations:
        result.append(RegistrationListResponse(
            id=reg.id,
            username=reg.username,
            real_name=reg.real_name,
            phone=reg.phone,
            email=reg.email,
            status=reg.status,
            employee_name=reg.employee.name if reg.employee else None,
            department_name=reg.employee.department.name if reg.employee and reg.employee.department else None,
            position_name=reg.employee.position.name if reg.employee and reg.employee.position else None,
            created_at=reg.created_at,
            admin_remarks=reg.admin_remarks
        ))
    
    return result

@router.get("/registrations/{registration_id}", response_model=RegistrationListResponse)
def get_registration_detail(
    *,
    db: Session = Depends(get_db),
    registration_id: int,
    current_user: User = Depends(get_current_admin)
) -> Any:
    """
    获取注册申请详情（管理员）
    """
    registration = user_registration.get(db=db, id=registration_id)
    if not registration:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="注册申请不存在"
        )
    
    return RegistrationListResponse(
        id=registration.id,
        username=registration.username,
        real_name=registration.real_name,
        phone=registration.phone,
        email=registration.email,
        status=registration.status,
        employee_name=registration.employee.name if registration.employee else None,
        department_name=registration.employee.department.name if registration.employee and registration.employee.department else None,
        position_name=registration.employee.position.name if registration.employee and registration.employee.position else None,
        created_at=registration.created_at,
        admin_remarks=registration.admin_remarks
    )

@router.post("/registrations/{registration_id}/approve")
def approve_registration(
    *,
    db: Session = Depends(get_db),
    registration_id: int,
    approval_data: RegistrationApprovalRequest,
    current_user: User = Depends(get_current_admin)
) -> Any:
    """
    审核注册申请（管理员）
    """
    registration = user_registration.approve_registration(
        db=db,
        registration_id=registration_id,
        admin_id=current_user.id,
        approval_data=approval_data
    )
    
    if not registration:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="注册申请不存在"
        )
    
    # 记录操作日志
    log_operation(
        db=db,
        user_id=current_user.id,
        operation_type="审核用户注册",
        operation_detail=f"{'通过' if approval_data.action == 'approve' else '拒绝'}了用户 {registration.username} 的注册申请"
    )
    
    action_text = "通过" if approval_data.action == "approve" else "拒绝"
    return {
        "message": f"注册申请已{action_text}",
        "status": registration.status
    }

@router.get("/my-registration")
def get_my_registration(
    *,
    db: Session = Depends(get_db),
    username: str,
    request: Request
) -> Any:
    """
    查询注册申请状态（公开接口）
    """
    registration = user_registration.get_by_username(db=db, username=username)
    if not registration:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="未找到注册申请"
        )
    
    return {
        "status": registration.status,
        "message": {
            "pending": "注册申请审核中，请耐心等待",
            "approved": "注册申请已通过，请使用用户名和密码登录",
            "rejected": f"注册申请被拒绝：{registration.admin_remarks or '未提供拒绝原因'}"
        }.get(registration.status, "未知状态"),
        "created_at": registration.created_at,
        "admin_remarks": registration.admin_remarks if registration.status == "rejected" else None
    } 