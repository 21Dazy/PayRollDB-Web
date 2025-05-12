-- 工资管理系统数据库设计
-- 创建数据库
CREATE DATABASE IF NOT EXISTS salary_management_system CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

USE salary_management_system;

-- 部门表
CREATE TABLE IF NOT EXISTS departments (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(50) NOT NULL COMMENT '部门名称',
    description VARCHAR(255) COMMENT '部门描述',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
) COMMENT '部门信息表';

-- 职位表
CREATE TABLE IF NOT EXISTS positions (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(50) NOT NULL COMMENT '职位名称',
    description VARCHAR(255) COMMENT '职位描述',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
) COMMENT '职位信息表';

-- 员工表
CREATE TABLE IF NOT EXISTS employees (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(50) NOT NULL COMMENT '姓名',
    department_id INT NOT NULL COMMENT '部门ID',
    position_id INT NOT NULL COMMENT '职位ID',
    base_salary DECIMAL(10, 2) NOT NULL COMMENT '基本工资',
    hire_date DATE NOT NULL COMMENT '入职日期',
    phone VARCHAR(20) COMMENT '联系电话',
    email VARCHAR(100) COMMENT '电子邮箱',
    address VARCHAR(255) COMMENT '地址',
    id_card VARCHAR(18) COMMENT '身份证号',
    bank_name VARCHAR(100) COMMENT '开户行',
    bank_account VARCHAR(100) COMMENT '银行账号',
    bank_account_encrypted VARBINARY(255) COMMENT '加密后的银行账号',
    status TINYINT DEFAULT 1 COMMENT '状态(1:在职, 0:离职)',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (department_id) REFERENCES departments(id),
    FOREIGN KEY (position_id) REFERENCES positions(id),
    INDEX idx_department (department_id),
    INDEX idx_position (position_id),
    INDEX idx_status (status)
) COMMENT '员工信息表';

-- 考勤状态表
CREATE TABLE IF NOT EXISTS attendance_status (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(20) NOT NULL COMMENT '状态名称',
    description VARCHAR(100) COMMENT '状态描述',
    is_deduction TINYINT DEFAULT 0 COMMENT '是否扣款(1:是, 0:否)',
    deduction_value DECIMAL(10, 2) DEFAULT 0 COMMENT '扣款金额或比例',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
) COMMENT '考勤状态表';

-- 考勤表
CREATE TABLE IF NOT EXISTS attendance (
    id INT AUTO_INCREMENT PRIMARY KEY,
    employee_id INT NOT NULL COMMENT '员工ID',
    date DATE NOT NULL COMMENT '日期',
    status_id INT NOT NULL COMMENT '出勤状态ID',
    overtime_hours DECIMAL(5, 2) DEFAULT 0 COMMENT '加班时长(小时)',
    remarks VARCHAR(255) COMMENT '备注',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (employee_id) REFERENCES employees(id),
    FOREIGN KEY (status_id) REFERENCES attendance_status(id),
    UNIQUE KEY uk_employee_date (employee_id, date),
    INDEX idx_date (date),
    INDEX idx_employee_id (employee_id)
) COMMENT '考勤记录表';

-- 工资组成项目表
CREATE TABLE IF NOT EXISTS salary_items (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(50) NOT NULL COMMENT '项目名称',
    type ENUM('addition', 'deduction') NOT NULL COMMENT '类型(addition:加项, deduction:减项)',
    is_percentage TINYINT DEFAULT 0 COMMENT '是否百分比(1:是, 0:否)',
    is_system TINYINT DEFAULT 0 COMMENT '是否系统项(1:是, 0:否)',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
) COMMENT '工资组成项目表';

-- 社保公积金配置表
CREATE TABLE IF NOT EXISTS social_security_config (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(50) NOT NULL COMMENT '配置名称',
    pension_rate DECIMAL(5, 2) NOT NULL COMMENT '养老保险比例',
    medical_rate DECIMAL(5, 2) NOT NULL COMMENT '医疗保险比例',
    unemployment_rate DECIMAL(5, 2) NOT NULL COMMENT '失业保险比例',
    injury_rate DECIMAL(5, 2) NOT NULL COMMENT '工伤保险比例',
    maternity_rate DECIMAL(5, 2) NOT NULL COMMENT '生育保险比例',
    housing_fund_rate DECIMAL(5, 2) NOT NULL COMMENT '住房公积金比例',
    is_default TINYINT DEFAULT 0 COMMENT '是否默认(1:是, 0:否)',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
) COMMENT '社保公积金配置表';

-- 员工社保公积金配置表
CREATE TABLE IF NOT EXISTS employee_social_security (
    id INT AUTO_INCREMENT PRIMARY KEY,
    employee_id INT NOT NULL COMMENT '员工ID',
    config_id INT NOT NULL COMMENT '社保配置ID',
    base_number DECIMAL(10, 2) NOT NULL COMMENT '社保基数',
    housing_fund_base DECIMAL(10, 2) NOT NULL COMMENT '公积金基数',
    effective_date DATE NOT NULL COMMENT '生效日期',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (employee_id) REFERENCES employees(id),
    FOREIGN KEY (config_id) REFERENCES social_security_config(id),
    INDEX idx_employee_id (employee_id)
) COMMENT '员工社保公积金配置表';

-- 工资记录表
CREATE TABLE IF NOT EXISTS salary_records (
    id INT AUTO_INCREMENT PRIMARY KEY,
    employee_id INT NOT NULL COMMENT '员工ID',
    year INT NOT NULL COMMENT '年份',
    month INT NOT NULL COMMENT '月份',
    base_salary DECIMAL(10, 2) NOT NULL COMMENT '基本工资',
    overtime_pay DECIMAL(10, 2) DEFAULT 0 COMMENT '加班费',
    bonus DECIMAL(10, 2) DEFAULT 0 COMMENT '奖金',
    deduction DECIMAL(10, 2) DEFAULT 0 COMMENT '扣款',
    social_security DECIMAL(10, 2) DEFAULT 0 COMMENT '社保公积金',
    personal_tax DECIMAL(10, 2) DEFAULT 0 COMMENT '个人所得税',
    net_salary DECIMAL(10, 2) NOT NULL COMMENT '实发工资',
    status ENUM('pending', 'paid') DEFAULT 'pending' COMMENT '发放状态',
    payment_date DATETIME COMMENT '发放日期',
    remark VARCHAR(255) COMMENT '备注',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (employee_id) REFERENCES employees(id),
    UNIQUE KEY uk_employee_year_month (employee_id, year, month),
    INDEX idx_year_month (year, month),
    INDEX idx_status (status),
    INDEX idx_employee_id (employee_id)
) COMMENT '工资记录表';

-- 工资明细表
CREATE TABLE IF NOT EXISTS salary_details (
    id INT AUTO_INCREMENT PRIMARY KEY,
    salary_id INT NOT NULL COMMENT '工资记录ID',
    item_id INT NOT NULL COMMENT '工资项目ID',
    amount DECIMAL(10, 2) NOT NULL COMMENT '金额',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (salary_id) REFERENCES salary_records(id) ON DELETE CASCADE,
    FOREIGN KEY (item_id) REFERENCES salary_items(id),
    INDEX idx_salary_id (salary_id)
) COMMENT '工资明细表';

-- 用户表
CREATE TABLE IF NOT EXISTS users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) NOT NULL COMMENT '用户名',
    password VARCHAR(255) NOT NULL COMMENT '密码(加密存储)',
    employee_id INT COMMENT '关联员工ID',
    role ENUM('admin', 'hr', 'manager', 'employee') NOT NULL COMMENT '角色',
    is_active TINYINT DEFAULT 1 COMMENT '是否激活(1:是, 0:否)',
    last_login DATETIME COMMENT '上次登录时间',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    UNIQUE KEY uk_username (username),
    FOREIGN KEY (employee_id) REFERENCES employees(id),
    INDEX idx_role (role),
    INDEX idx_is_active (is_active)
) COMMENT '用户表';

-- 操作日志表
CREATE TABLE IF NOT EXISTS operation_logs (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL COMMENT '用户ID',
    operation_type VARCHAR(50) NOT NULL COMMENT '操作类型',
    operation_content TEXT COMMENT '操作内容',
    ip_address VARCHAR(50) COMMENT 'IP地址',
    operation_time DATETIME NOT NULL COMMENT '操作时间',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id),
    INDEX idx_user_id (user_id),
    INDEX idx_operation_time (operation_time)
) COMMENT '操作日志表';

-- 系统参数表
CREATE TABLE IF NOT EXISTS system_parameters (
    id INT AUTO_INCREMENT PRIMARY KEY,
    param_key VARCHAR(50) NOT NULL COMMENT '参数键',
    param_value VARCHAR(255) NOT NULL COMMENT '参数值',
    description VARCHAR(255) COMMENT '参数描述',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    UNIQUE KEY uk_param_key (param_key)
) COMMENT '系统参数表';

-- 初始化基础数据
INSERT INTO attendance_status (name, description, is_deduction, deduction_value) VALUES 
('正常', '正常出勤', 0, 0),
('迟到', '迟到', 1, 50),
('早退', '早退', 1, 50),
('缺勤', '缺勤', 1, 200),
('病假', '病假', 1, 0.5),
('事假', '事假', 1, 1),
('年假', '年假', 0, 0),
('调休', '调休', 0, 0);

INSERT INTO salary_items (name, type, is_percentage, is_system) VALUES 
('基本工资', 'addition', 0, 1),
('加班费', 'addition', 0, 1),
('绩效奖金', 'addition', 0, 0),
('全勤奖', 'addition', 0, 0),
('交通补贴', 'addition', 0, 0),
('餐补', 'addition', 0, 0),
('社保个人部分', 'deduction', 0, 1),
('公积金个人部分', 'deduction', 0, 1),
('个人所得税', 'deduction', 0, 1),
('迟到扣款', 'deduction', 0, 0),
('缺勤扣款', 'deduction', 0, 0);

INSERT INTO social_security_config (name, pension_rate, medical_rate, unemployment_rate, injury_rate, maternity_rate, housing_fund_rate, is_default) VALUES 
('默认配置', 8, 2, 0.5, 0, 0, 12, 1);

-- 系统参数初始化
INSERT INTO system_parameters (param_key, param_value, description) VALUES 
('overtime_rate', '1.5', '加班费率(工作日)'),
('weekend_overtime_rate', '2', '加班费率(周末)'),
('holiday_overtime_rate', '3', '加班费率(节假日)'),
('tax_threshold', '5000', '个税起征点'),
('salary_day', '10', '每月发薪日'); 