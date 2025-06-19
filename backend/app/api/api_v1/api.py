from fastapi import APIRouter

from app.api.api_v1.endpoints import (
    auth, users, departments, positions, employees, 
    attendance, salaries, social_security, system, user_registration,
    user_profile, user_salary, user_attendance
)

api_router = APIRouter()

# 身份验证
api_router.include_router(auth.router, prefix="/auth", tags=["身份验证"])

# 用户注册
api_router.include_router(user_registration.router, prefix="/registration", tags=["用户注册"])

# 用户管理
api_router.include_router(users.router, prefix="/users", tags=["用户管理"])

# 部门管理
api_router.include_router(departments.router, prefix="/departments", tags=["部门管理"])

# 职位管理
api_router.include_router(positions.router, prefix="/positions", tags=["职位管理"])

# 员工管理
api_router.include_router(employees.router, prefix="/employees", tags=["员工管理"])

# 考勤管理
api_router.include_router(attendance.router, prefix="/attendance", tags=["考勤管理"])

# 工资管理
api_router.include_router(salaries.router, prefix="/salaries", tags=["工资管理"])

# 社保管理
api_router.include_router(social_security.router, prefix="/social-security", tags=["社保管理"])

# 系统管理
api_router.include_router(system.router, prefix="/system", tags=["系统管理"])

# 用户个人功能
api_router.include_router(user_profile.router, prefix="/user/profile", tags=["个人信息"])
api_router.include_router(user_salary.router, prefix="/user/salary", tags=["个人薪资"])
api_router.include_router(user_attendance.router, prefix="/user/attendance", tags=["个人考勤"]) 