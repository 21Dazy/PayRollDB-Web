from typing import List, Optional, Dict, Any
from datetime import date, datetime, timedelta
from decimal import Decimal
from sqlalchemy.orm import Session
from sqlalchemy import and_

from app.models.employee import Employee
from app.models.salary_config import EmployeeSalaryConfig
from app.models.salary_record import SalaryRecord
from app.models.salary_detail import SalaryDetail
from app.models.salary_item import SalaryItem
from app.models.attendance import Attendance
from app.models.attendance_status import AttendanceStatus
from app.crud.crud_salary_config import salary_config as crud_salary_config
from app.crud import employee as crud_employee

class SalaryService:
    def __init__(self, db: Session):
        self.db = db
    
    def calculate_employee_salary(
        self, 
        employee_id: int, 
        year: int, 
        month: int
    ) -> Dict[str, Any]:
        """计算单个员工的薪资"""
        # 获取员工信息
        employee = crud_employee.get(self.db, id=employee_id)
        if not employee:
            raise ValueError(f"员工ID {employee_id} 不存在")
        
        # 获取月份的最后一天作为有效日期
        if month == 12:
            effective_date = date(year + 1, 1, 1) - timedelta(days=1)
        else:
            effective_date = date(year, month + 1, 1) - timedelta(days=1)
        
        # 获取员工薪资配置
        configs = crud_salary_config.get_employee_config(
            self.db, 
            employee_id=employee_id,
            effective_date=effective_date
        )
        
        # 打印薪资配置，用于调试
        print(f"员工 {employee_id} 的薪资配置数量: {len(configs)}")
        for config in configs:
            print(f"薪资配置: item_id={config.item_id}, value={config.value}, item_name={config.salary_item.name if config.salary_item else 'None'}")
        
        # 初始化薪资组成
        salary_components = {
            'base_salary': Decimal(str(employee.base_salary or '0')),  # 默认使用员工基本工资
            'overtime_pay': Decimal('0'),
            'bonus': Decimal('0'),
            'performance_bonus': Decimal('0'),
            'attendance_bonus': Decimal('0'),
            'transportation_allowance': Decimal('0'),
            'meal_allowance': Decimal('0'),
            'deduction': Decimal('0'),
            'social_security': Decimal('0'),
            'late_deduction': Decimal('0'),
            'absence_deduction': Decimal('0'),
            'personal_tax': Decimal('0')
        }
        
        # 详细项目列表
        details = []
        
        # 处理薪资配置项
        has_base_salary_config = False
        
        if configs:
            print("开始处理薪资配置项...")
            for config in configs:
                item = config.salary_item
                if not item:
                    print(f"配置项 {config.id} 没有关联的薪资项目，跳过")
                    continue
                
                print(f"处理薪资项目: {item.name}, 类型: {item.type}, 值: {config.value}")
                    
                value = Decimal(str(config.value or '0'))
                
                # 如果是百分比，需要计算实际金额
                if item.is_percentage and config.base_item:
                    base_value = self._get_base_value(employee, config.base_item)
                    actual_value = base_value * value / 100
                    print(f"百分比计算: {value}% * {base_value} = {actual_value}")
                else:
                    actual_value = value
                    print(f"固定金额: {actual_value}")
                
                # 根据项目类型和名称累加到相应组成部分
                if item.type == 'addition':
                    if item.name == '基本工资':
                        print(f"设置基本工资: {actual_value}")
                        salary_components['base_salary'] = actual_value
                        has_base_salary_config = True
                    elif item.name == '加班费':
                        print(f"累加加班费: {actual_value}")
                        salary_components['overtime_pay'] += actual_value
                    elif item.name == '绩效奖金':
                        print(f"累加绩效奖金: {actual_value}")
                        salary_components['performance_bonus'] += actual_value
                    elif item.name == '全勤奖':
                        print(f"累加全勤奖: {actual_value}")
                        salary_components['attendance_bonus'] += actual_value
                    elif item.name == '交通补贴':
                        print(f"累加交通补贴: {actual_value}")
                        salary_components['transportation_allowance'] += actual_value
                    elif item.name == '餐补':
                        print(f"累加餐补: {actual_value}")
                        salary_components['meal_allowance'] += actual_value
                    else:
                        print(f"累加奖金: {actual_value}")
                        salary_components['bonus'] += actual_value
                else:  # deduction
                    if '社保' in item.name or '公积金' in item.name:
                        print(f"累加社保公积金: {actual_value}")
                        salary_components['social_security'] += actual_value
                    elif '税' in item.name:
                        print(f"累加个税: {actual_value}")
                        salary_components['personal_tax'] += actual_value
                    elif '迟到' in item.name:
                        print(f"累加迟到扣款: {actual_value}")
                        salary_components['late_deduction'] += actual_value
                    elif '缺勤' in item.name:
                        print(f"累加缺勤扣款: {actual_value}")
                        salary_components['absence_deduction'] += actual_value
                    else:
                        print(f"累加扣款: {actual_value}")
                        salary_components['deduction'] += actual_value
                
                # 添加到详细列表
                details.append({
                    'item_id': item.id,
                    'amount': actual_value
                })
                
            # 打印薪资组成
            print("薪资组成:", salary_components)
        
        # 如果没有基本工资配置，使用员工表中的基本工资
        if not has_base_salary_config:
            print(f"没有基本工资配置，使用员工表中的基本工资: {salary_components['base_salary']}")
            base_salary_item = self.db.query(SalaryItem).filter(SalaryItem.name == '基本工资').first()
            if base_salary_item:
                print(f"找到基本工资项目: id={base_salary_item.id}, name={base_salary_item.name}")
                details.append({
                    'item_id': base_salary_item.id,
                    'amount': salary_components['base_salary']
                })
            else:
                print("未找到基本工资项目，请确保数据库中有名为'基本工资'的薪资项目")
        
        # 计算考勤扣款
        try:
            attendance_deduction = self._calculate_attendance_deduction(
                employee_id, year, month
            )
            salary_components['absence_deduction'] += attendance_deduction
        except Exception as e:
            print(f"计算考勤扣款出错: {str(e)}")
        
        # 计算实发工资
        net_salary = (
            salary_components['base_salary'] +
            salary_components['overtime_pay'] +
            salary_components['bonus'] +
            salary_components['performance_bonus'] +
            salary_components['attendance_bonus'] +
            salary_components['transportation_allowance'] +
            salary_components['meal_allowance'] -
            salary_components['deduction'] -
            salary_components['social_security'] -
            salary_components['personal_tax'] -
            salary_components['late_deduction'] -
            salary_components['absence_deduction']
        )
        
        print(f"计算实发工资: {salary_components['base_salary']} + {salary_components['overtime_pay']} + {salary_components['bonus']} + "
              f"{salary_components['performance_bonus']} + {salary_components['attendance_bonus']} + {salary_components['transportation_allowance']} + "
              f"{salary_components['meal_allowance']} - {salary_components['deduction']} - {salary_components['social_security']} - "
              f"{salary_components['personal_tax']} - {salary_components['late_deduction']} - {salary_components['absence_deduction']} = {net_salary}")
        
        result = {
            'employee_id': employee_id,
            'year': year,
            'month': month,
            'components': salary_components,
            'net_salary': net_salary,
            'details': details
        }
        
        print(f"返回薪资计算结果: {result}")
        return result
    
    def _get_base_value(self, employee: Employee, base_item: str) -> Decimal:
        """获取基准值"""
        if base_item == 'base_salary':
            return Decimal(str(employee.base_salary or '0'))
        # 可以扩展其他基准项
        return Decimal('0')
    
    def _calculate_attendance_deduction(
        self, 
        employee_id: int, 
        year: int, 
        month: int
    ) -> Decimal:
        """计算考勤扣款"""
        try:
            # 获取该月的考勤记录
            start_date = date(year, month, 1)
            if month == 12:
                end_date = date(year + 1, 1, 1)
            else:
                end_date = date(year, month + 1, 1)
            
            # 联合查询考勤记录和考勤状态
            attendances = self.db.query(Attendance).join(
                AttendanceStatus, Attendance.status_id == AttendanceStatus.id
            ).filter(
                Attendance.employee_id == employee_id,
                Attendance.date >= start_date,
                Attendance.date < end_date
            ).all()
            
            # 获取员工基本工资
            employee = crud_employee.get(self.db, id=employee_id)
            if not employee:
                print(f"员工ID {employee_id} 不存在，无法计算考勤扣款")
                return Decimal('0')
            
            base_salary = Decimal(str(employee.base_salary or '0'))
            daily_salary = base_salary / Decimal('22')  # 假设每月22个工作日
            
            # 统计不同类型的考勤状态
            late_count = 0
            absent_count = 0
            total_deduction = Decimal('0')
            
            print(f"开始计算员工 {employee_id} 的考勤扣款，共 {len(attendances)} 条记录")
            
            for attendance in attendances:
                # 获取考勤状态
                status = attendance.status
                if not status:
                    print(f"考勤记录 {attendance.id} 没有关联的状态，跳过")
                    continue
                
                print(f"处理考勤记录: 日期={attendance.date}, 状态={status.name}, is_deduction={status.is_deduction}, deduction_value={status.deduction_value}")
                
                # 如果是扣款状态
                if status.is_deduction:
                    if '迟到' in status.name:
                        late_count += 1
                        # 迟到扣款，通常是固定金额
                        deduction = Decimal(str(status.deduction_value))
                        print(f"迟到扣款: {deduction}")
                    elif '缺勤' in status.name or '旷工' in status.name:
                        absent_count += 1
                        # 缺勤扣款，通常是日工资的倍数
                        if status.deduction_value <= 2:  # 如果是比例
                            deduction = daily_salary * Decimal(str(status.deduction_value))
                        else:  # 如果是固定金额
                            deduction = Decimal(str(status.deduction_value))
                        print(f"缺勤扣款: 日工资={daily_salary}, 扣款比例/金额={status.deduction_value}, 实际扣款={deduction}")
                    else:
                        # 其他扣款情况
                        if status.deduction_value <= 2:  # 如果是比例
                            deduction = daily_salary * Decimal(str(status.deduction_value))
                        else:  # 如果是固定金额
                            deduction = Decimal(str(status.deduction_value))
                        print(f"其他扣款: {deduction}")
                    
                    total_deduction += deduction
            
            print(f"员工 {employee_id} 的考勤扣款统计: 迟到={late_count}次, 缺勤={absent_count}次, 总扣款={total_deduction}")
            
            return total_deduction
        except Exception as e:
            print(f"计算考勤扣款出错: {str(e)}")
            return Decimal('0')
    
    def generate_salary_records(
        self,
        year: int,
        month: int,
        department_id: Optional[int] = None,
        employee_ids: Optional[List[int]] = None
    ) -> Dict[str, Any]:
        """批量生成薪资记录"""
        generated_count = 0
        failed_count = 0
        errors = []
        
        # 获取需要生成薪资的员工列表
        query = self.db.query(Employee).filter(Employee.status == True)
        
        if department_id:
            query = query.filter(Employee.department_id == department_id)
        
        if employee_ids:
            query = query.filter(Employee.id.in_(employee_ids))
        
        employees = query.all()
        
        for employee in employees:
            try:
                # 检查是否已存在薪资记录
                existing = self.db.query(SalaryRecord).filter(
                    SalaryRecord.employee_id == employee.id,
                    SalaryRecord.year == year,
                    SalaryRecord.month == month
                ).first()
                
                # 计算薪资
                salary_data = self.calculate_employee_salary(
                    employee.id, year, month
                )
                
                if existing:
                    # 如果已存在且状态为已发放，则不更新
                    if existing.status == 'paid':
                        errors.append(f"员工 {employee.name} 的薪资记录已发放，无法更新")
                        failed_count += 1
                        continue
                    
                    # 更新现有记录
                    existing.base_salary = salary_data['components']['base_salary']
                    existing.overtime_pay = salary_data['components']['overtime_pay']
                    existing.bonus = salary_data['components']['bonus']
                    existing.performance_bonus = salary_data['components']['performance_bonus']
                    existing.attendance_bonus = salary_data['components']['attendance_bonus']
                    existing.transportation_allowance = salary_data['components']['transportation_allowance']
                    existing.meal_allowance = salary_data['components']['meal_allowance']
                    existing.deduction = salary_data['components']['deduction']
                    existing.social_security = salary_data['components']['social_security']
                    existing.late_deduction = salary_data['components']['late_deduction']
                    existing.absence_deduction = salary_data['components']['absence_deduction']
                    existing.personal_tax = salary_data['components']['personal_tax']
                    existing.net_salary = salary_data['net_salary']
                    
                    # 删除旧的薪资明细
                    self.db.query(SalaryDetail).filter(SalaryDetail.salary_id == existing.id).delete()
                    
                    salary_record = existing
                else:
                    # 创建薪资记录
                    salary_record = SalaryRecord(
                        employee_id=employee.id,
                        year=year,
                        month=month,
                        base_salary=salary_data['components']['base_salary'],
                        overtime_pay=salary_data['components']['overtime_pay'],
                        bonus=salary_data['components']['bonus'],
                        performance_bonus=salary_data['components']['performance_bonus'],
                        attendance_bonus=salary_data['components']['attendance_bonus'],
                        transportation_allowance=salary_data['components']['transportation_allowance'],
                        meal_allowance=salary_data['components']['meal_allowance'],
                        deduction=salary_data['components']['deduction'],
                        social_security=salary_data['components']['social_security'],
                        late_deduction=salary_data['components']['late_deduction'],
                        absence_deduction=salary_data['components']['absence_deduction'],
                        personal_tax=salary_data['components']['personal_tax'],
                        net_salary=salary_data['net_salary'],
                        status='pending'
                    )
                    
                    self.db.add(salary_record)
                    self.db.flush()  # 获取ID
                
                # 创建薪资明细
                for detail in salary_data['details']:
                    salary_detail = SalaryDetail(
                        salary_id=salary_record.id,
                        item_id=detail['item_id'],
                        amount=detail['amount']
                    )
                    self.db.add(salary_detail)
                
                generated_count += 1
                
            except Exception as e:
                errors.append(f"员工 {employee.name} 生成失败: {str(e)}")
                failed_count += 1
        
        self.db.commit()
        
        return {
            'generated_count': generated_count,
            'failed_count': failed_count,
            'errors': errors
        } 