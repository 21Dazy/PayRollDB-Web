 # 工资管理系统数据库ER图说明文档

## 1. 数据库概述

本文档详细描述工资管理系统的数据库实体关系模型。该数据库设计支持企业员工管理、考勤记录、工资计算与发放等核心功能。

### 1.1 设计原则

1. **完整性**：通过主键、外键、唯一约束等保证数据完整性
2. **规范化**：遵循第三范式，减少数据冗余
3. **安全性**：敏感数据（如银行账号）采用加密存储
4. **可扩展性**：预留未来功能扩展的可能性
5. **性能优化**：合理设置索引提高查询效率

## 2. 实体关系图

```
+----------------+       +----------------+       +---------------+
| departments    |       | positions      |       | attendance_   |
+----------------+       +----------------+       | status        |
| PK id          |       | PK id          |       +---------------+
| name           |       | name           |       | PK id         |
| description    |       | description    |       | name          |
+----------------+       +----------------+       | is_deduction  |
        |                        |                | deduction_    |
        |                        |                | value         |
        |                        |                +---------------+
        |                        |                        |
        |                        |                        |
        v                        v                        v
+-------------------------------------------------------+
| employees                                             |
+-------------------------------------------------------+
| PK id                                                 |
| name                                                  |
| FK department_id                                      |
| FK position_id                                        |
| base_salary                                           |
| hire_date                                             |
| ... (其他个人信息)                                     |
| bank_account_encrypted                                |
| status                                                |
+-------------------------------------------------------+
        |                |                 |
        |                |                 |
        v                v                 v
+----------------+ +----------------+ +----------------+
| attendance     | | salary_records | | employee_      |
+----------------+ +----------------+ | social_security|
| PK id          | | PK id          | +----------------+
| FK employee_id | | FK employee_id | | PK id          |
| date           | | year           | | FK employee_id |
| FK status_id   | | month          | | FK config_id   |
| overtime_hours | | base_salary    | | base_number    |
+----------------+ | ... (其他薪资项) | | housing_fund_  |
        |          | net_salary     | | base           |
        |          | status         | +----------------+
        |          +----------------+         |
        |                   |                 |
        v                   v                 |
+----------------+ +----------------+         |
| salary_items   | | salary_details |         |
+----------------+ +----------------+         |
| PK id          | | PK id          |         |
| name           | | FK salary_id   |         |
| type           | | FK item_id     |         |
| is_percentage  | | amount         |         |
| is_system      | +----------------+         |
+----------------+                            |
                                              v
                                    +----------------+
                                    | social_        |
                                    | security_config|
                                    +----------------+
                                    | PK id          |
                                    | name           |
                                    | pension_rate   |
                                    | ... (其他比率)  |
                                    | is_default     |
                                    +----------------+

+----------------+       +----------------+
| users          |       | system_        |
+----------------+       | parameters     |
| PK id          |       +----------------+
| username       |       | PK id          |
| password       |       | param_key      |
| FK employee_id |       | param_value    |
| role           |       | description    |
| is_active      |       +----------------+
+----------------+
        |
        |
        v
+----------------+
| operation_logs |
+----------------+
| PK id          |
| FK user_id     |
| operation_type |
| operation_     |
| content        |
| ip_address     |
| operation_time |
+----------------+
```

## 3. 实体详细说明

### 3.1 主要实体

#### 3.1.1 部门 (departments)
- **主要属性**：id, name, description
- **业务角色**：作为组织结构的基本单元，用于员工归类管理
- **关联关系**：一个部门包含多名员工

#### 3.1.2 职位 (positions)
- **主要属性**：id, name, description
- **业务角色**：定义员工在组织中的职能角色
- **关联关系**：一个职位可由多名员工担任

#### 3.1.3 员工 (employees)
- **主要属性**：id, name, department_id, position_id, base_salary, hire_date, phone, email, bank_account_encrypted
- **业务角色**：系统的核心实体，记录员工基本信息
- **关联关系**：
  - 隶属于一个部门
  - 担任一个职位
  - 拥有多条考勤记录
  - 拥有多条工资记录
  - 有一个社保公积金配置
  - 可关联一个用户账号

#### 3.1.4 考勤状态 (attendance_status)
- **主要属性**：id, name, description, is_deduction, deduction_value
- **业务角色**：定义不同的考勤状态类型及相关规则
- **关联关系**：一个状态可用于多条考勤记录

#### 3.1.5 考勤 (attendance)
- **主要属性**：id, employee_id, date, status_id, overtime_hours
- **业务角色**：记录员工每日出勤情况，是工资计算的基础
- **关联关系**：
  - 属于一名员工
  - 使用一种考勤状态

#### 3.1.6 工资组成项目 (salary_items)
- **主要属性**：id, name, type, is_percentage, is_system
- **业务角色**：定义工资构成项目，如基本工资、绩效奖金等
- **关联关系**：一个项目可用于多条工资明细

#### 3.1.7 社保公积金配置 (social_security_config)
- **主要属性**：id, name, pension_rate, medical_rate, unemployment_rate, housing_fund_rate
- **业务角色**：定义社保公积金的计算比例规则
- **关联关系**：一个配置可应用于多个员工

#### 3.1.8 员工社保公积金 (employee_social_security)
- **主要属性**：id, employee_id, config_id, base_number, housing_fund_base, effective_date
- **业务角色**：记录每个员工的社保公积金缴纳基数和规则
- **关联关系**：
  - 属于一名员工
  - 使用一种社保配置

#### 3.1.9 工资记录 (salary_records)
- **主要属性**：id, employee_id, year, month, base_salary, overtime_pay, bonus, deduction, social_security, personal_tax, net_salary, status
- **业务角色**：记录员工月度工资情况，包括各项汇总数据
- **关联关系**：
  - 属于一名员工
  - 包含多条工资明细

#### 3.1.10 工资明细 (salary_details)
- **主要属性**：id, salary_id, item_id, amount
- **业务角色**：记录工资的详细构成项目和金额
- **关联关系**：
  - 属于一条工资记录
  - 关联一个工资项目

#### 3.1.11 用户 (users)
- **主要属性**：id, username, password, employee_id, role, is_active
- **业务角色**：管理系统用户账号和权限
- **关联关系**：
  - 可能关联一名员工
  - 拥有多条操作日志

#### 3.1.12 操作日志 (operation_logs)
- **主要属性**：id, user_id, operation_type, operation_content, ip_address, operation_time
- **业务角色**：记录系统操作，用于审计和追溯
- **关联关系**：属于一个用户

#### 3.1.13 系统参数 (system_parameters)
- **主要属性**：id, param_key, param_value, description
- **业务角色**：存储系统全局配置参数
- **关联关系**：独立实体，不与其他实体直接关联

## 4. 主要关系详解

### 4.1 一对多关系

1. **部门-员工**:
   - 关系描述：一个部门可以包含多名员工，一名员工只属于一个部门
   - 实现方式：在员工表中设置department_id外键
   - 业务意义：反映组织结构层次关系

2. **职位-员工**:
   - 关系描述：一个职位可以由多名员工担任，一名员工只担任一个职位
   - 实现方式：在员工表中设置position_id外键
   - 业务意义：定义员工在组织中的职能角色

3. **员工-考勤**:
   - 关系描述：一名员工有多条考勤记录，一条考勤记录只属于一名员工
   - 实现方式：在考勤表中设置employee_id外键
   - 业务意义：记录员工出勤情况，为工资计算提供依据

4. **考勤状态-考勤**:
   - 关系描述：一种考勤状态可用于多条考勤记录，一条考勤记录只使用一种状态
   - 实现方式：在考勤表中设置status_id外键
   - 业务意义：用不同状态标识员工考勤情况

5. **员工-工资记录**:
   - 关系描述：一名员工有多条工资记录，一条工资记录只属于一名员工
   - 实现方式：在工资记录表中设置employee_id外键
   - 业务意义：记录员工不同月份的工资情况

6. **工资记录-工资明细**:
   - 关系描述：一条工资记录包含多条明细，一条明细只属于一条工资记录
   - 实现方式：在工资明细表中设置salary_id外键
   - 业务意义：详细记录工资组成项目

7. **工资项目-工资明细**:
   - 关系描述：一个工资项目可用于多条工资明细，一条明细只使用一个项目
   - 实现方式：在工资明细表中设置item_id外键
   - 业务意义：定义工资组成项目类型

8. **社保配置-员工社保**:
   - 关系描述：一个社保配置可应用于多个员工，一个员工只使用一种配置
   - 实现方式：在员工社保表中设置config_id外键
   - 业务意义：灵活配置不同员工的社保公积金规则

9. **用户-操作日志**:
   - 关系描述：一个用户可产生多条操作日志，一条日志只属于一个用户
   - 实现方式：在操作日志表中设置user_id外键
   - 业务意义：记录用户操作，用于审计和追溯

### 4.2 一对一关系

1. **员工-用户**:
   - 关系描述：一名员工可能有一个用户账号，一个用户可能关联一名员工
   - 实现方式：在用户表中设置可为空的employee_id外键
   - 业务意义：员工可通过账号访问系统，但系统管理员等角色可能不是员工

## 5. 数据完整性约束

### 5.1 实体完整性

1. **主键约束**:
   - 所有表都设置了自增主键id，确保每条记录唯一标识
   - 例：`id INT AUTO_INCREMENT PRIMARY KEY`

### 5.2 参照完整性

1. **外键约束**:
   - 所有关联关系都设置了适当的外键约束，确保数据一致性
   - 例：`FOREIGN KEY (department_id) REFERENCES departments(id)`

### 5.3 域完整性

1. **非空约束**:
   - 关键业务字段设置为NOT NULL，确保必要数据存在
   - 例：员工表中的name、department_id、position_id等字段

2. **默认值约束**:
   - 为需要默认值的字段设置DEFAULT，简化数据录入
   - 例：员工状态默认为在职`status TINYINT DEFAULT 1`

3. **唯一约束**:
   - 对需要唯一值的字段设置UNIQUE KEY，防止重复数据
   - 例：用户名唯一`UNIQUE KEY uk_username (username)`

4. **复合唯一约束**:
   - 对需要联合唯一的多个字段设置复合唯一约束
   - 例：确保一个员工一个月只有一条工资记录`UNIQUE KEY uk_employee_year_month (employee_id, year, month)`

### 5.4 业务规则约束

1. **枚举约束**:
   - 使用ENUM类型限定字段可选值范围
   - 例：工资项目类型`type ENUM('addition', 'deduction')`

2. **状态标记**:
   - 使用TINYINT类型表示布尔状态
   - 例：是否激活`is_active TINYINT DEFAULT 1`

## 6. 索引设计

### 6.1 索引分类

1. **主键索引**:
   - 所有表的id字段自动创建主键索引
   - 提供最快的数据访问方式

2. **唯一索引**:
   - 用户名等需要唯一性的字段创建唯一索引
   - 既保证唯一性又提高查询效率

3. **普通索引**:
   - 在外键和常用查询条件字段上创建普通索引
   - 如员工表的department_id、position_id，工资记录表的year、month等

4. **复合索引**:
   - 对经常一起出现在查询条件中的多个字段创建复合索引
   - 如工资记录表的(year, month)字段

### 6.2 主要索引一览

| 表名 | 索引名 | 字段 | 索引类型 | 用途 |
|------|--------|------|---------|------|
| employees | PRIMARY | id | 主键 | 唯一标识员工 |
| employees | idx_department | department_id | 普通 | 加速按部门查询 |
| employees | idx_position | position_id | 普通 | 加速按职位查询 |
| employees | idx_status | status | 普通 | 加速按状态查询 |
| attendance | uk_employee_date | employee_id, date | 唯一 | 确保一天一条考勤记录 |
| attendance | idx_date | date | 普通 | 加速按日期查询 |
| salary_records | uk_employee_year_month | employee_id, year, month | 唯一 | 确保月度工资唯一 |
| salary_records | idx_year_month | year, month | 普通 | 加速按年月查询 |
| users | uk_username | username | 唯一 | 确保用户名唯一 |
| users | idx_role | role | 普通 | 加速按角色查询 |
| operation_logs | idx_operation_time | operation_time | 普通 | 加速按时间查询 |

## 7. 安全性设计

### 7.1 数据加密

1. **银行账号加密**:
   - 员工表中的bank_account_encrypted字段使用VARBINARY类型存储加密后的银行账号
   - 应用程序层负责加解密逻辑

2. **密码哈希存储**:
   - 用户表中的password字段存储密码哈希值，不存储明文密码
   - 使用bcrypt等安全哈希算法

### 7.2 审计追踪

1. **操作日志表**:
   - 记录关键操作的用户、时间、内容等信息
   - 支持安全审计和问题追溯

2. **时间戳记录**:
   - 所有表都包含created_at和updated_at字段
   - 自动记录数据创建和修改时间

## 8. 未来扩展考虑

1. **多币种支持**:
   - 可为工资相关金额字段添加货币类型字段
   - 支持国际化企业多币种工资发放

2. **绩效评估集成**:
   - 可添加绩效评估相关表
   - 与工资奖金系统集成

3. **团队结构扩展**:
   - 可添加团队表，支持部门内更细粒度的团队管理
   - 部门-团队-员工的多级组织结构

4. **多级审批流**:
   - 可添加审批流程和审批记录表
   - 支持工资、假期等多级审批

## 9. 数据示例

数据库包含丰富的示例数据，涵盖多个部门、职位和员工，以及完整的考勤记录和工资记录样例。详情可查看sample_data.sql文件。