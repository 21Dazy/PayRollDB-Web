#!/usr/bin/env python
"""
初始化管理员用户脚本
用于在系统初始化时创建一个管理员用户，以便能够登录系统测试API
"""
import os
import sys
import traceback
from datetime import date
from pathlib import Path

# 添加项目根目录到 Python 路径
project_root = Path(__file__).parent
sys.path.append(str(project_root))

from sqlalchemy.orm import Session
from passlib.context import CryptContext

from app.db.session import engine, SessionLocal
from app.models.user import User
from app.models.department import Department
from app.models.position import Position
from app.models.employee import Employee

# 密码上下文
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def init_admin():
    """初始化管理员账号"""
    db = SessionLocal()
    try:
        # 检查是否已有用户
        user = db.query(User).first()
        if user:
            print("管理员用户已存在，无需初始化")
            return
        
        # 创建管理员所在部门
        department = Department(name="管理部门", description="系统管理部门")
        db.add(department)
        db.flush()
        print(f"部门创建成功: {department.name}")
        
        # 创建管理员职位
        position = Position(name="系统管理员", description="系统管理员职位", department_id=department.id)
        db.add(position)
        db.flush()
        
        # 创建管理员员工信息
        employee = Employee(
            name="管理员",
            gender="男",
            id_card="000000000000000000",
            date_of_birth=date(1990, 1, 1),
            phone="13800000000",
            email="admin@example.com",
            address="系统默认地址",
            hire_date=date(2020, 1, 1),
            department_id=department.id,
            position_id=position.id
        )
        db.add(employee)
        db.flush()
        
        # 创建管理员账号
        admin_user = User(
            username="admin",
            hashed_password=pwd_context.hash("admin123"),
            is_active=True,
            is_superuser=True,
            employee_id=employee.id
        )
        db.add(admin_user)
        db.commit()
        
        print("管理员用户初始化成功，用户名：admin，密码：admin123")
    except Exception as e:
        db.rollback()
        print(f"初始化管理员账号失败: {e}")
        traceback.print_exc()  # 打印完整错误堆栈
    finally:
        db.close()

if __name__ == "__main__":
    init_admin() 