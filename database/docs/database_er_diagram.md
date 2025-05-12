# 工资管理系统数据库ER图描述

## 实体关系

### 主要实体
1. **部门(departments)**
   - 属性：id, name, description
   - 关系：一个部门有多个员工

2. **职位(positions)**
   - 属性：id, name, description
   - 关系：一个职位有多个员工

3. **员工(employees)**
   - 属性：id, name, department_id, position_id, base_salary, hire_date, phone, email, bank_account等
   - 关系：
     - 属于一个部门
     - 属于一个职位
     - 有多条考勤记录
     - 有多条工资记录
     - 有一个社保公积金配置

4. **考勤状态(attendance_status)**
   - 属性：id, name, description, is_deduction, deduction_value
   - 关系：一个状态对应多条考勤记录

5. **考勤(attendance)**
   - 属性：id, employee_id, date, status_id, overtime_hours
   - 关系：
     - 属于一个员工
     - 有一个考勤状态

6. **工资组成项目(salary_items)**
   - 属性：id, name, type, is_percentage, is_system
   - 关系：一个项目对应多条工资明细

7. **社保公积金配置(social_security_config)**
   - 属性：id, name, pension_rate, medical_rate, unemployment_rate等
   - 关系：一个配置对应多个员工社保公积金设置

8. **员工社保公积金(employee_social_security)**
   - 属性：id, employee_id, config_id, base_number, housing_fund_base, effective_date
   - 关系：
     - 属于一个员工
     - 使用一个社保公积金配置

9. **工资记录(salary_records)**
   - 属性：id, employee_id, year, month, base_salary, bonus, deduction, social_security, net_salary等
   - 关系：
     - 属于一个员工
     - 有多条工资明细

10. **工资明细(salary_details)**
    - 属性：id, salary_id, item_id, amount
    - 关系：
      - 属于一条工资记录
      - 关联一个工资项目

11. **用户(users)**
    - 属性：id, username, password, employee_id, role
    - 关系：
      - 可能关联一个员工
      - 有多条操作日志

12. **操作日志(operation_logs)**
    - 属性：id, user_id, operation_type, operation_content, ip_address, operation_time
    - 关系：属于一个用户

13. **系统参数(system_parameters)**
    - 属性：id, param_key, param_value, description

## 主要关系

1. **部门-员工**: 一对多关系，一个部门包含多名员工
2. **职位-员工**: 一对多关系，一个职位可以由多名员工担任
3. **员工-考勤**: 一对多关系，一名员工有多条考勤记录
4. **考勤状态-考勤**: 一对多关系，一种考勤状态对应多条考勤记录
5. **员工-工资记录**: 一对多关系，一名员工有多条工资记录
6. **工资记录-工资明细**: 一对多关系，一条工资记录包含多条明细
7. **工资项目-工资明细**: 一对多关系，一个工资项目出现在多条工资明细中
8. **社保配置-员工社保**: 一对多关系，一个社保配置可应用于多个员工
9. **员工-社保配置**: 一对一关系，一名员工有一个社保配置
10. **员工-用户**: 一对一关系，一名员工可能关联一个用户账号
11. **用户-操作日志**: 一对多关系，一个用户有多条操作日志

## 数据完整性约束

1. **主键约束**: 所有表都有自增主键id
2. **外键约束**: 所有关联关系都有适当的外键约束
3. **唯一约束**:
   - 员工考勤表对(employee_id, date)的唯一约束
   - 工资记录表对(employee_id, year, month)的唯一约束
   - 用户表对username的唯一约束
   - 系统参数表对param_key的唯一约束
4. **非空约束**: 关键字段都有非空约束
5. **默认值约束**: 适当字段设置了默认值
6. **索引**: 为提高查询效率，在关键字段上创建了索引

## 安全性考虑

- 员工表中包含bank_account_encrypted字段，用于存储加密后的银行账号
- 用户表中密码字段需要加密存储
- 操作日志表记录关键操作，确保可追溯性 