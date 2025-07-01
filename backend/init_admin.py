#!/usr/bin/env python
"""
初始化管理员用户脚本
用于在系统初始化时创建一个管理员用户，以便能够登录系统测试API
同时初始化系统必需的基础数据
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

def init_basic_data(db):
    """初始化基础数据"""
    
    # 1. 初始化考勤状态
    attendance_statuses = [
        {"name": "正常", "description": "正常出勤", "is_deduction": 0, "deduction_value": 0.00},
        {"name": "迟到", "description": "迟到", "is_deduction": 1, "deduction_value": 50.00},
        {"name": "早退", "description": "早退", "is_deduction": 1, "deduction_value": 50.00},
        {"name": "缺勤", "description": "缺勤", "is_deduction": 1, "deduction_value": 200.00},
        {"name": "病假", "description": "病假", "is_deduction": 1, "deduction_value": 0.50},
        {"name": "事假", "description": "事假", "is_deduction": 1, "deduction_value": 1.00},
        {"name": "调休", "description": "调休", "is_deduction": 0, "deduction_value": 0.00}
    ]
    
    # 检查是否已存在考勤状态数据
    status_count = db.execute(text("SELECT COUNT(*) FROM attendance_status")).scalar()
    if status_count == 0:
        for status in attendance_statuses:
            db.execute(
                text("""
                    INSERT INTO attendance_status (name, description, is_deduction, deduction_value) 
                    VALUES (:name, :description, :is_deduction, :deduction_value)
                """),
                status
            )
        print("考勤状态基础数据初始化完成")
    
    # 2. 初始化工资项目
    salary_items = [
        {"name": "基本工资", "type": "addition", "is_percentage": 0, "is_system": 1},
        {"name": "加班费", "type": "addition", "is_percentage": 0, "is_system": 1},
        {"name": "奖金", "type": "addition", "is_percentage": 0, "is_system": 1},
        {"name": "绩效奖金", "type": "addition", "is_percentage": 0, "is_system": 1},
        {"name": "全勤奖", "type": "addition", "is_percentage": 0, "is_system": 1},
        {"name": "交通补贴", "type": "addition", "is_percentage": 0, "is_system": 1},
        {"name": "餐补", "type": "addition", "is_percentage": 0, "is_system": 1},
        {"name": "话费补贴", "type": "addition", "is_percentage": 0, "is_system": 0},
        {"name": "住房补贴", "type": "addition", "is_percentage": 0, "is_system": 0},
        {"name": "社保公积金", "type": "deduction", "is_percentage": 0, "is_system": 1},
        {"name": "个人所得税", "type": "deduction", "is_percentage": 0, "is_system": 1},
        {"name": "迟到扣款", "type": "deduction", "is_percentage": 0, "is_system": 1},
        {"name": "缺勤扣款", "type": "deduction", "is_percentage": 0, "is_system": 1},
        {"name": "其他扣款", "type": "deduction", "is_percentage": 0, "is_system": 0}
    ]
    
    # 检查是否已存在工资项目数据
    item_count = db.execute(text("SELECT COUNT(*) FROM salary_items")).scalar()
    if item_count == 0:
        for item in salary_items:
            db.execute(
                text("""
                    INSERT INTO salary_items (name, type, is_percentage, is_system) 
                    VALUES (:name, :type, :is_percentage, :is_system)
                """),
                item
            )
        print("工资项目基础数据初始化完成")
    
    # 3. 初始化社保配置
    social_security_configs = [
        {
            "name": "默认社保方案",
            "pension_rate": 8.00,
            "medical_rate": 2.00,
            "unemployment_rate": 0.50,
            "injury_rate": 0.00,
            "maternity_rate": 0.00,
            "housing_fund_rate": 12.00,
            "is_default": 1
        }
    ]
    
    # 检查是否已存在社保配置数据
    config_count = db.execute(text("SELECT COUNT(*) FROM social_security_config")).scalar()
    if config_count == 0:
        for config in social_security_configs:
            db.execute(
                text("""
                    INSERT INTO social_security_config 
                    (name, pension_rate, medical_rate, unemployment_rate, injury_rate, maternity_rate, housing_fund_rate, is_default) 
                    VALUES (:name, :pension_rate, :medical_rate, :unemployment_rate, :injury_rate, :maternity_rate, :housing_fund_rate, :is_default)
                """),
                config
            )
        print("社保配置基础数据初始化完成")
    
    # 4. 初始化系统参数
    system_params = [
        {"param_key": "overtime_rate", "param_value": "1.5", "description": "加班费倍率"},
        {"param_key": "tax_threshold", "param_value": "5000", "description": "个税起征点"},
        {"param_key": "work_days_per_month", "param_value": "22", "description": "每月工作日天数"},
        {"param_key": "work_hours_per_day", "param_value": "8", "description": "每日工作小时数"},
        {"param_key": "system_version", "param_value": "1.0.0", "description": "系统版本"}
    ]
    
    # 检查是否已存在系统参数数据
    param_count = db.execute(text("SELECT COUNT(*) FROM system_parameters")).scalar()
    if param_count == 0:
        for param in system_params:
            db.execute(
                text("""
                    INSERT INTO system_parameters (param_key, param_value, description) 
                    VALUES (:param_key, :param_value, :description)
                """),
                param
            )
        print("系统参数基础数据初始化完成")

def init_admin():
    """初始化管理员账号"""
    db = SessionLocal()
    try:
        # 检查是否已有用户
        user_count = db.execute(text("SELECT COUNT(*) FROM users")).scalar()
        if user_count > 0:
            print("管理员用户已存在，无需初始化")
            return
        
        # 先初始化基础数据
        print("开始初始化基础数据...")
        init_basic_data(db)
        
        # 创建管理员所在部门
        db.execute(
            text("INSERT INTO departments (name, description) VALUES (:name, :description)"),
            {"name": "管理部门", "description": "系统管理部门"}
        )
        result = db.execute(text("SELECT LAST_INSERT_ID()"))
        department_id = result.scalar()
        print(f"部门创建成功，ID: {department_id}")
        
        # 创建管理员职位（修复：添加department_id）
        db.execute(
            text("INSERT INTO positions (name, department_id, description) VALUES (:name, :department_id, :description)"),
            {"name": "系统管理员", "department_id": department_id, "description": "系统管理员职位"}
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
        result = db.execute(text("SELECT LAST_INSERT_ID()"))
        user_id = result.scalar()
        print(f"管理员用户创建成功，ID: {user_id}")
        
        # 为管理员配置社保（使用默认配置）
        default_config = db.execute(
            text("SELECT id FROM social_security_config WHERE is_default = 1 LIMIT 1")
        ).scalar()
        
        if default_config:
            db.execute(
                text("""
                    INSERT INTO employee_social_security 
                    (employee_id, config_id, base_number, housing_fund_base, effective_date) 
                    VALUES (:employee_id, :config_id, :base_number, :housing_fund_base, :effective_date)
                """),
                {
                    "employee_id": employee_id,
                    "config_id": default_config,
                    "base_number": 8000.00,
                    "housing_fund_base": 8000.00,
                    "effective_date": date(2020, 1, 1)
                }
            )
            print("管理员社保配置创建成功")
        
        db.commit()
        print("=" * 50)
        print("系统初始化完成！")
        print("管理员用户信息：")
        print("  用户名：admin")
        print("  密码：admin123")
        print("  角色：admin")
        print("=" * 50)
        
    except Exception as e:
        db.rollback()
        print(f"初始化失败: {e}")
        traceback.print_exc()  # 打印完整错误堆栈
    finally:
        db.close()

if __name__ == "__main__":
    init_admin() 