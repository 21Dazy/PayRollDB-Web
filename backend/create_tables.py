#!/usr/bin/env python
"""
数据库表初始化脚本
用于创建所有数据库表和基础数据
"""
from sqlalchemy import text

from app.db.base import Base
from app.db.session import engine
from app.models.attendance_status import AttendanceStatus
from app.models.salary_item import SalaryItem
from app.models.social_security_config import SocialSecurityConfig
from app.models.system_parameter import SystemParameter

def create_tables():
    print("开始创建数据库表...")
    Base.metadata.create_all(bind=engine)
    print("数据库表创建完成")

def init_basic_data():
    from sqlalchemy.orm import Session
    from app.db.session import SessionLocal
    
    print("开始初始化基础数据...")
    db = SessionLocal()
    try:
        # 初始化考勤状态
        if db.query(AttendanceStatus).count() == 0:
            attendance_statuses = [
                AttendanceStatus(name="正常", description="正常出勤", is_deduction=False, deduction_value=0),
                AttendanceStatus(name="迟到", description="迟到", is_deduction=True, deduction_value=50),
                AttendanceStatus(name="早退", description="早退", is_deduction=True, deduction_value=50),
                AttendanceStatus(name="缺勤", description="缺勤", is_deduction=True, deduction_value=200),
                AttendanceStatus(name="病假", description="病假", is_deduction=True, deduction_value=0.5),
                AttendanceStatus(name="事假", description="事假", is_deduction=True, deduction_value=1),
                AttendanceStatus(name="年假", description="年假", is_deduction=False, deduction_value=0),
                AttendanceStatus(name="调休", description="调休", is_deduction=False, deduction_value=0),
            ]
            
            for status in attendance_statuses:
                db.add(status)
            
            print(f"初始化了 {len(attendance_statuses)} 条考勤状态数据")
        
        # 初始化工资项目
        if db.query(SalaryItem).count() == 0:
            salary_items = [
                SalaryItem(name="基本工资", type="addition", is_percentage=False, is_system=True),
                SalaryItem(name="加班费", type="addition", is_percentage=False, is_system=True),
                SalaryItem(name="绩效奖金", type="addition", is_percentage=False, is_system=False),
                SalaryItem(name="全勤奖", type="addition", is_percentage=False, is_system=False),
                SalaryItem(name="交通补贴", type="addition", is_percentage=False, is_system=False),
                SalaryItem(name="餐补", type="addition", is_percentage=False, is_system=False),
                SalaryItem(name="社保个人部分", type="deduction", is_percentage=False, is_system=True),
                SalaryItem(name="公积金个人部分", type="deduction", is_percentage=False, is_system=True),
                SalaryItem(name="个人所得税", type="deduction", is_percentage=False, is_system=True),
                SalaryItem(name="迟到扣款", type="deduction", is_percentage=False, is_system=False),
                SalaryItem(name="缺勤扣款", type="deduction", is_percentage=False, is_system=False),
            ]
            
            for item in salary_items:
                db.add(item)
            
            print(f"初始化了 {len(salary_items)} 条工资项目数据")
        
        # 初始化社保配置
        if db.query(SocialSecurityConfig).count() == 0:
            config = SocialSecurityConfig(
                name="默认配置", 
                pension_rate=8.0,
                medical_rate=2.0, 
                unemployment_rate=0.5, 
                injury_rate=0.0,
                maternity_rate=0.0, 
                housing_fund_rate=12.0,
                is_default=True
            )
            db.add(config)
            print("初始化了默认社保配置")
        
        # 初始化系统参数
        if db.query(SystemParameter).count() == 0:
            system_parameters = [
                SystemParameter(param_key="overtime_rate", param_value="1.5", description="加班费率(工作日)"),
                SystemParameter(param_key="weekend_overtime_rate", param_value="2", description="加班费率(周末)"),
                SystemParameter(param_key="holiday_overtime_rate", param_value="3", description="加班费率(节假日)"),
                SystemParameter(param_key="tax_threshold", param_value="5000", description="个税起征点"),
                SystemParameter(param_key="salary_day", param_value="10", description="每月发薪日"),
            ]
            
            for param in system_parameters:
                db.add(param)
            
            print(f"初始化了 {len(system_parameters)} 条系统参数")
        
        db.commit()
        print("基础数据初始化完成")
    except Exception as e:
        print(f"初始化基础数据失败: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    create_tables()
    init_basic_data()
    
    # 提示用户运行初始化管理员脚本
    print("\n表和基础数据已创建完成！")
    print("请运行 python init_admin.py 创建管理员用户") 