-- 工资管理系统数据库表结构文档
-- 本文件用于记录和解释数据库表结构，为开发和维护人员提供参考

/*
=============================================================
表命名规范
=============================================================
1. 使用小写字母和下划线命名
2. 使用复数形式表示集合
3. 使用有意义的名称，避免缩写
4. 表名不超过30个字符

字段命名规范
=============================================================
1. 使用小写字母和下划线命名
2. 主键统一命名为id
3. 外键命名规则: 关联表名的单数形式_id
4. 创建时间统一命名为created_at
5. 更新时间统一命名为updated_at
6. 状态字段根据业务命名，如status, is_active等
7. 避免使用数据库关键字作为字段名

索引命名规范
=============================================================
1. 主键索引: PRIMARY KEY
2. 唯一索引: uk_表名_字段名
3. 普通索引: idx_表名_字段名
4. 外键约束: FOREIGN KEY
*/

/*
=============================================================
表结构详细说明
=============================================================
*/

/*
部门表 (departments)
- 存储公司的部门信息
- 作为员工表的外键引用
*/
/*
CREATE TABLE departments (
    id INT AUTO_INCREMENT PRIMARY KEY,        -- 部门ID，自增主键
    name VARCHAR(50) NOT NULL,                -- 部门名称，非空
    description VARCHAR(255),                 -- 部门描述，可为空
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,            -- 创建时间
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP  -- 更新时间
);
*/

/*
职位表 (positions)
- 存储公司的职位信息
- 作为员工表的外键引用
*/
/*
CREATE TABLE positions (
    id INT AUTO_INCREMENT PRIMARY KEY,        -- 职位ID，自增主键
    name VARCHAR(50) NOT NULL,                -- 职位名称，非空
    description VARCHAR(255),                 -- 职位描述，可为空
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,            -- 创建时间
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP  -- 更新时间
);
*/

/*
员工表 (employees)
- 存储员工基本信息
- 关联部门和职位
- 包含工资相关信息
- 敏感信息需要加密处理
*/
/*
CREATE TABLE employees (
    id INT AUTO_INCREMENT PRIMARY KEY,           -- 员工ID，自增主键
    name VARCHAR(50) NOT NULL,                   -- 姓名，非空
    department_id INT NOT NULL,                  -- 部门ID，外键
    position_id INT NOT NULL,                    -- 职位ID，外键
    base_salary DECIMAL(10, 2) NOT NULL,         -- 基本工资，非空
    hire_date DATE NOT NULL,                     -- 入职日期，非空
    phone VARCHAR(20),                           -- 联系电话，可为空
    email VARCHAR(100),                          -- 电子邮箱，可为空
    address VARCHAR(255),                        -- 地址，可为空
    id_card VARCHAR(18),                         -- 身份证号，可为空
    bank_name VARCHAR(100),                      -- 开户行，可为空
    bank_account VARCHAR(100),                   -- 银行账号，可为空
    bank_account_encrypted VARBINARY(255),       -- 加密后的银行账号，可为空，用于安全存储
    status TINYINT DEFAULT 1,                    -- 状态(1:在职, 0:离职)，默认在职
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,               -- 创建时间
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,     -- 更新时间
    FOREIGN KEY (department_id) REFERENCES departments(id),  -- 外键约束，关联部门表
    FOREIGN KEY (position_id) REFERENCES positions(id),     -- 外键约束，关联职位表
    INDEX idx_department (department_id),        -- 索引，提高按部门查询效率
    INDEX idx_position (position_id),            -- 索引，提高按职位查询效率
    INDEX idx_status (status)                    -- 索引，提高按状态查询效率
);
*/

/*
考勤状态表 (attendance_status)
- 存储各种考勤状态定义
- 包含是否扣款及扣款标准
*/
/*
CREATE TABLE attendance_status (
    id INT AUTO_INCREMENT PRIMARY KEY,        -- 状态ID，自增主键
    name VARCHAR(20) NOT NULL,                -- 状态名称，非空
    description VARCHAR(100),                 -- 状态描述，可为空
    is_deduction TINYINT DEFAULT 0,           -- 是否扣款(1:是, 0:否)，默认否
    deduction_value DECIMAL(10, 2) DEFAULT 0, -- 扣款金额或比例，默认0
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,            -- 创建时间
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP  -- 更新时间
);
*/

/*
考勤表 (attendance)
- 记录员工每日考勤情况
- 关联员工和考勤状态
- 包含加班信息
*/
/*
CREATE TABLE attendance (
    id INT AUTO_INCREMENT PRIMARY KEY,        -- 考勤ID，自增主键
    employee_id INT NOT NULL,                 -- 员工ID，外键
    date DATE NOT NULL,                       -- 日期，非空
    status_id INT NOT NULL,                   -- 出勤状态ID，外键
    overtime_hours DECIMAL(5, 2) DEFAULT 0,   -- 加班时长(小时)，默认0
    remarks VARCHAR(255),                     -- 备注，可为空
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,            -- 创建时间
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,  -- 更新时间
    FOREIGN KEY (employee_id) REFERENCES employees(id),  -- 外键约束，关联员工表
    FOREIGN KEY (status_id) REFERENCES attendance_status(id),  -- 外键约束，关联状态表
    UNIQUE KEY uk_employee_date (employee_id, date),  -- 唯一约束，确保一个员工一天只有一条考勤记录
    INDEX idx_date (date),                    -- 索引，提高按日期查询效率
    INDEX idx_employee_id (employee_id)       -- 索引，提高按员工查询效率
);
*/

/*
工资组成项目表 (salary_items)
- 定义工资构成的各个项目
- 区分加项和减项
- 标识是否为系统默认项
*/
/*
CREATE TABLE salary_items (
    id INT AUTO_INCREMENT PRIMARY KEY,        -- 项目ID，自增主键
    name VARCHAR(50) NOT NULL,                -- 项目名称，非空
    type ENUM('addition', 'deduction') NOT NULL,  -- 类型(addition:加项, deduction:减项)，非空
    is_percentage TINYINT DEFAULT 0,          -- 是否百分比(1:是, 0:否)，默认否
    is_system TINYINT DEFAULT 0,              -- 是否系统项(1:是, 0:否)，默认否，系统项不可删除
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,            -- 创建时间
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP  -- 更新时间
);
*/

/*
社保公积金配置表 (social_security_config)
- 定义社保公积金的各项比例
- 可设置多个配置方案
*/
/*
CREATE TABLE social_security_config (
    id INT AUTO_INCREMENT PRIMARY KEY,        -- 配置ID，自增主键
    name VARCHAR(50) NOT NULL,                -- 配置名称，非空
    pension_rate DECIMAL(5, 2) NOT NULL,      -- 养老保险比例，非空
    medical_rate DECIMAL(5, 2) NOT NULL,      -- 医疗保险比例，非空
    unemployment_rate DECIMAL(5, 2) NOT NULL, -- 失业保险比例，非空
    injury_rate DECIMAL(5, 2) NOT NULL,       -- 工伤保险比例，非空
    maternity_rate DECIMAL(5, 2) NOT NULL,    -- 生育保险比例，非空
    housing_fund_rate DECIMAL(5, 2) NOT NULL, -- 住房公积金比例，非空
    is_default TINYINT DEFAULT 0,             -- 是否默认(1:是, 0:否)，默认否
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,            -- 创建时间
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP  -- 更新时间
);
*/

/*
员工社保公积金配置表 (employee_social_security)
- 记录每个员工的社保公积金配置
- 关联员工和社保配置
- 记录基数和生效日期
*/
/*
CREATE TABLE employee_social_security (
    id INT AUTO_INCREMENT PRIMARY KEY,        -- ID，自增主键
    employee_id INT NOT NULL,                 -- 员工ID，外键
    config_id INT NOT NULL,                   -- 社保配置ID，外键
    base_number DECIMAL(10, 2) NOT NULL,      -- 社保基数，非空
    housing_fund_base DECIMAL(10, 2) NOT NULL,-- 公积金基数，非空
    effective_date DATE NOT NULL,             -- 生效日期，非空
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,            -- 创建时间
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,  -- 更新时间
    FOREIGN KEY (employee_id) REFERENCES employees(id),  -- 外键约束，关联员工表
    FOREIGN KEY (config_id) REFERENCES social_security_config(id),  -- 外键约束，关联配置表
    INDEX idx_employee_id (employee_id)       -- 索引，提高按员工查询效率
);
*/

/*
工资记录表 (salary_records)
- 记录每个员工每月的工资情况
- 包含各类工资项目的汇总数据
- 记录发放状态和日期
*/
/*
CREATE TABLE salary_records (
    id INT AUTO_INCREMENT PRIMARY KEY,           -- ID，自增主键
    employee_id INT NOT NULL,                    -- 员工ID，外键
    year INT NOT NULL,                           -- 年份，非空
    month INT NOT NULL,                          -- 月份，非空
    base_salary DECIMAL(10, 2) NOT NULL,         -- 基本工资，非空
    overtime_pay DECIMAL(10, 2) DEFAULT 0,       -- 加班费，默认0
    bonus DECIMAL(10, 2) DEFAULT 0,              -- 奖金，默认0
    deduction DECIMAL(10, 2) DEFAULT 0,          -- 扣款，默认0
    social_security DECIMAL(10, 2) DEFAULT 0,    -- 社保公积金，默认0
    personal_tax DECIMAL(10, 2) DEFAULT 0,       -- 个人所得税，默认0
    net_salary DECIMAL(10, 2) NOT NULL,          -- 实发工资，非空
    status ENUM('pending', 'paid') DEFAULT 'pending',  -- 发放状态，默认待发放
    payment_date DATETIME,                       -- 发放日期，可为空
    remark VARCHAR(255),                         -- 备注，可为空
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,               -- 创建时间
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,     -- 更新时间
    FOREIGN KEY (employee_id) REFERENCES employees(id),  -- 外键约束，关联员工表
    UNIQUE KEY uk_employee_year_month (employee_id, year, month),  -- 唯一约束，确保一个员工一个月只有一条工资记录
    INDEX idx_year_month (year, month),          -- 索引，提高按年月查询效率
    INDEX idx_status (status),                   -- 索引，提高按状态查询效率
    INDEX idx_employee_id (employee_id)          -- 索引，提高按员工查询效率
);
*/

/*
工资明细表 (salary_details)
- 记录工资记录的详细构成
- 关联工资记录和工资项目
*/
/*
CREATE TABLE salary_details (
    id INT AUTO_INCREMENT PRIMARY KEY,        -- ID，自增主键
    salary_id INT NOT NULL,                   -- 工资记录ID，外键
    item_id INT NOT NULL,                     -- 工资项目ID，外键
    amount DECIMAL(10, 2) NOT NULL,           -- 金额，非空
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,            -- 创建时间
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,  -- 更新时间
    FOREIGN KEY (salary_id) REFERENCES salary_records(id) ON DELETE CASCADE,  -- 外键约束，级联删除
    FOREIGN KEY (item_id) REFERENCES salary_items(id),  -- 外键约束，关联项目表
    INDEX idx_salary_id (salary_id)           -- 索引，提高按工资记录查询效率
);
*/

/*
用户表 (users)
- 存储系统用户信息
- 关联员工表，一个员工可能有一个用户账号
- 区分不同角色的用户
*/
/*
CREATE TABLE users (
    id INT AUTO_INCREMENT PRIMARY KEY,        -- ID，自增主键
    username VARCHAR(50) NOT NULL,            -- 用户名，非空
    password VARCHAR(255) NOT NULL,           -- 密码(加密存储)，非空
    employee_id INT,                          -- 关联员工ID，可为空（如系统管理员可能不是员工）
    role ENUM('admin', 'hr', 'manager', 'employee') NOT NULL,  -- 角色，非空
    is_active TINYINT DEFAULT 1,              -- 是否激活(1:是, 0:否)，默认激活
    last_login DATETIME,                      -- 上次登录时间，可为空
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,            -- 创建时间
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,  -- 更新时间
    UNIQUE KEY uk_username (username),        -- 唯一约束，确保用户名唯一
    FOREIGN KEY (employee_id) REFERENCES employees(id),  -- 外键约束，关联员工表
    INDEX idx_role (role),                    -- 索引，提高按角色查询效率
    INDEX idx_is_active (is_active)           -- 索引，提高按状态查询效率
);
*/

/*
操作日志表 (operation_logs)
- 记录系统重要操作日志
- 关联用户表，记录操作者
- 记录操作类型、内容、IP地址和时间
*/
/*
CREATE TABLE operation_logs (
    id INT AUTO_INCREMENT PRIMARY KEY,        -- ID，自增主键
    user_id INT NOT NULL,                     -- 用户ID，外键
    operation_type VARCHAR(50) NOT NULL,      -- 操作类型，非空
    operation_content TEXT,                   -- 操作内容，可为空
    ip_address VARCHAR(50),                   -- IP地址，可为空
    operation_time DATETIME NOT NULL,         -- 操作时间，非空
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,            -- 创建时间
    FOREIGN KEY (user_id) REFERENCES users(id),  -- 外键约束，关联用户表
    INDEX idx_user_id (user_id),              -- 索引，提高按用户查询效率
    INDEX idx_operation_time (operation_time)  -- 索引，提高按时间查询效率
);
*/

/*
系统参数表 (system_parameters)
- 存储系统配置参数
- 包含参数键、值和描述
*/
/*
CREATE TABLE system_parameters (
    id INT AUTO_INCREMENT PRIMARY KEY,        -- ID，自增主键
    param_key VARCHAR(50) NOT NULL,           -- 参数键，非空
    param_value VARCHAR(255) NOT NULL,        -- 参数值，非空
    description VARCHAR(255),                 -- 参数描述，可为空
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,            -- 创建时间
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,  -- 更新时间
    UNIQUE KEY uk_param_key (param_key)       -- 唯一约束，确保参数键唯一
);
*/

/*
=============================================================
数据库关系图解释
=============================================================

主要实体和关系:

1. 部门与员工：一对多关系
   - 一个部门可以有多个员工
   - 一个员工只属于一个部门

2. 职位与员工：一对多关系
   - 一个职位可以由多个员工担任
   - 一个员工只担任一个职位

3. 员工与考勤：一对多关系
   - 一个员工有多条考勤记录
   - 一条考勤记录只属于一个员工

4. 考勤状态与考勤：一对多关系
   - 一个考勤状态可用于多条考勤记录
   - 一条考勤记录只有一种状态

5. 员工与工资记录：一对多关系
   - 一个员工有多条工资记录（按月份）
   - 一条工资记录只属于一个员工

6. 工资记录与工资明细：一对多关系
   - 一条工资记录包含多条工资明细
   - 一条工资明细只属于一条工资记录

7. 工资项目与工资明细：一对多关系
   - 一个工资项目可用于多条工资明细
   - 一条工资明细只关联一个工资项目

8. 社保配置与员工社保：一对多关系
   - 一个社保配置可应用于多个员工
   - 一个员工的社保只使用一种配置

9. 员工与用户：一对一关系（可选）
   - 一个员工可能有一个用户账号
   - 一个用户账号可能关联一个员工（管理员等系统角色可能不关联员工）

10. 用户与操作日志：一对多关系
    - 一个用户可以产生多条操作日志
    - 一条操作日志只属于一个用户
*/ 