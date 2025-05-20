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
from sqlalchemy import text

# 添加项目根目录到 Python 路径
project_root = Path(__file__).parent
sys.path.append(str(project_root))

from app.db.session import engine, SessionLocal
from app.core.security import get_password_hash

def init_admin():
    """初始化管理员账号"""
    db = SessionLocal()
    try:
        # 检查是否已有用户
        user_count = db.execute(text("SELECT COUNT(*) FROM users")).scalar()
        if user_count > 0:
            print("管理员用户已存在，无需初始化")
            return
        
        # 创建管理员所在部门
        db.execute(
            text("INSERT INTO departments (name, description) VALUES (:name, :description)"),
            {"name": "管理部门", "description": "系统管理部门"}
        )
        result = db.execute(text("SELECT LAST_INSERT_ID()"))
        department_id = result.scalar()
        print(f"部门创建成功，ID: {department_id}")
        
        # 创建管理员职位
        db.execute(
            text("INSERT INTO positions (name, description) VALUES (:name, :description)"),
            {"name": "系统管理员", "description": "系统管理员职位"}
        )
        result = db.execute(text("SELECT LAST_INSERT_ID()"))
        position_id = result.scalar()
        print(f"职位创建成功，ID: {position_id}")
        
        # 创建管理员员工信息
        db.execute(
            text("""
                INSERT INTO employees (
                    name, department_id, position_id, base_salary, hire_date, 
                    phone, email, address, id_card, status
                ) VALUES (
                    :name, :department_id, :position_id, :base_salary, :hire_date,
                    :phone, :email, :address, :id_card, :status
                )
            """),
            {
                "name": "管理员",
                "department_id": department_id,
                "position_id": position_id,
                "base_salary": 8000.00,
                "hire_date": date(2020, 1, 1),
                "phone": "13800000000",
                "email": "admin@example.com",
                "address": "系统默认地址",
                "id_card": "000000000000000000",
                "status": True
            }
        )
        result = db.execute(text("SELECT LAST_INSERT_ID()"))
        employee_id = result.scalar()
        print(f"员工创建成功，ID: {employee_id}")
        
        # 创建管理员账号
        hashed_password = get_password_hash("admin123")
        db.execute(
            text("""
                INSERT INTO users (
                    username, password, employee_id, role, is_active
                ) VALUES (
                    :username, :password, :employee_id, :role, :is_active
                )
            """),
            {
                "username": "admin",
                "password": hashed_password,
                "employee_id": employee_id,
                "role": "admin",
                "is_active": True
            }
        )
        
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