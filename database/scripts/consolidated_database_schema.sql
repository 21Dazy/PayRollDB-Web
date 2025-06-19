-- =================================================================================================
-- 工资管理系统 - 整合数据库脚本
-- =================================================================================================
-- 此脚本整合了以下文件：
-- 1. database_design.sql (基础表结构)
-- 2. update_salary_components.sql (更新薪资记录表)
-- 3. employee_salary_config.sql (员工薪资配置表)
-- 4. user_self_service_enhancement.sql (用户自助服务功能增强)
-- =================================================================================================

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
    department_id INT NOT NULL COMMENT '所属部门ID',
    description VARCHAR(255) COMMENT '职位描述',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (department_id) REFERENCES departments(id),
    INDEX idx_department (department_id)
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


-- =================================================================================================
-- 来自: update_salary_components.sql
-- =================================================================================================
-- 添加缺失的薪资组成项目字段
ALTER TABLE salary_records
ADD COLUMN performance_bonus DECIMAL(10, 2) DEFAULT 0 COMMENT '绩效奖金' AFTER bonus,
ADD COLUMN attendance_bonus DECIMAL(10, 2) DEFAULT 0 COMMENT '全勤奖' AFTER performance_bonus,
ADD COLUMN transportation_allowance DECIMAL(10, 2) DEFAULT 0 COMMENT '交通补贴' AFTER attendance_bonus,
ADD COLUMN meal_allowance DECIMAL(10, 2) DEFAULT 0 COMMENT '餐补' AFTER transportation_allowance,
ADD COLUMN late_deduction DECIMAL(10, 2) DEFAULT 0 COMMENT '迟到扣款' AFTER social_security,
ADD COLUMN absence_deduction DECIMAL(10, 2) DEFAULT 0 COMMENT '缺勤扣款' AFTER late_deduction;

-- 更新净工资计算逻辑
-- 更新已有记录的净工资计算
UPDATE salary_records
SET net_salary = base_salary + overtime_pay + bonus + performance_bonus + attendance_bonus + 
                transportation_allowance + meal_allowance - deduction - social_security - 
                personal_tax - late_deduction - absence_deduction;

-- 创建触发器，确保新记录的净工资自动计算
DELIMITER //
CREATE TRIGGER IF NOT EXISTS calculate_net_salary_before_insert
BEFORE INSERT ON salary_records
FOR EACH ROW
BEGIN
    SET NEW.net_salary = NEW.base_salary + NEW.overtime_pay + NEW.bonus + 
                        NEW.performance_bonus + NEW.attendance_bonus + 
                        NEW.transportation_allowance + NEW.meal_allowance - 
                        NEW.deduction - NEW.social_security - NEW.personal_tax - 
                        NEW.late_deduction - NEW.absence_deduction;
END //

CREATE TRIGGER IF NOT EXISTS calculate_net_salary_before_update
BEFORE UPDATE ON salary_records
FOR EACH ROW
BEGIN
    SET NEW.net_salary = NEW.base_salary + NEW.overtime_pay + NEW.bonus + 
                        NEW.performance_bonus + NEW.attendance_bonus + 
                        NEW.transportation_allowance + NEW.meal_allowance - 
                        NEW.deduction - NEW.social_security - NEW.personal_tax - 
                        NEW.late_deduction - NEW.absence_deduction;
END //
DELIMITER ;

-- 更新薪资明细表，确保与薪资项目表关联正确
-- 检查并修复薪资明细表中的项目ID引用
UPDATE salary_details sd
JOIN salary_items si ON sd.item_id = si.id
SET sd.item_id = si.id
WHERE sd.item_id IS NOT NULL;

-- 添加索引以提高查询性能
ALTER TABLE salary_records
ADD INDEX idx_performance_bonus (performance_bonus),
ADD INDEX idx_attendance_bonus (attendance_bonus),
ADD INDEX idx_transportation_allowance (transportation_allowance),
ADD INDEX idx_meal_allowance (meal_allowance),
ADD INDEX idx_late_deduction (late_deduction),
ADD INDEX idx_absence_deduction (absence_deduction);

-- 更新注释
ALTER TABLE salary_records COMMENT '工资记录表 - 包含所有薪资组成项目';


-- =================================================================================================
-- 来自: employee_salary_config.sql
-- =================================================================================================
-- 员工薪资配置表
CREATE TABLE IF NOT EXISTS employee_salary_config (
    id INT AUTO_INCREMENT PRIMARY KEY,
    employee_id INT NOT NULL COMMENT '员工ID',
    item_id INT NOT NULL COMMENT '薪资项目ID',
    value DECIMAL(10, 2) NOT NULL COMMENT '金额或百分比值',
    base_item VARCHAR(50) COMMENT '基准项目(用于百分比计算)',
    is_active TINYINT DEFAULT 1 COMMENT '是否启用(1:是, 0:否)',
    effective_date DATE NOT NULL COMMENT '生效日期',
    expiry_date DATE COMMENT '失效日期',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (employee_id) REFERENCES employees(id),
    FOREIGN KEY (item_id) REFERENCES salary_items(id),
    INDEX idx_employee_id (employee_id),
    INDEX idx_item_id (item_id),
    INDEX idx_effective_date (effective_date),
    INDEX idx_is_active (is_active)
) COMMENT '员工薪资配置表';

-- 添加唯一约束，确保同一员工同一项目在同一时间只有一个有效配置
ALTER TABLE employee_salary_config 
ADD UNIQUE KEY uk_employee_item_date (employee_id, item_id, effective_date);

-- 插入一些示例数据（可选）
-- INSERT INTO employee_salary_config (employee_id, item_id, value, effective_date) 
-- SELECT 
--     e.id,
--     si.id,
--     CASE 
--         WHEN si.name = '基本工资' THEN e.base_salary
--         WHEN si.name = '交通补贴' THEN 300
--         WHEN si.name = '餐补' THEN 500
--         ELSE 0
--     END,
--     CURDATE()
-- FROM employees e
-- CROSS JOIN salary_items si
-- WHERE si.name IN ('基本工资', '交通补贴', '餐补')
-- AND e.status = 1; 


-- =================================================================================================
-- 来自: user_self_service_enhancement.sql
-- =================================================================================================
-- 用户注册验证表
CREATE TABLE IF NOT EXISTS user_registrations (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) NOT NULL COMMENT '用户名',
    password VARCHAR(255) NOT NULL COMMENT '密码(加密存储)',
    real_name VARCHAR(50) NOT NULL COMMENT '真实姓名',
    id_card VARCHAR(18) NOT NULL COMMENT '身份证号',
    phone VARCHAR(20) NOT NULL COMMENT '手机号',
    email VARCHAR(100) COMMENT '邮箱',
    employee_id INT COMMENT '申请绑定的员工ID',
    verification_code VARCHAR(10) COMMENT '验证码',
    verification_expires DATETIME COMMENT '验证码过期时间',
    status ENUM('pending', 'approved', 'rejected') DEFAULT 'pending' COMMENT '审核状态',
    admin_id INT COMMENT '审核管理员ID',
    admin_remarks VARCHAR(255) COMMENT '管理员审核备注',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (employee_id) REFERENCES employees(id),
    FOREIGN KEY (admin_id) REFERENCES users(id),
    INDEX idx_username (username),
    INDEX idx_id_card (id_card),
    INDEX idx_phone (phone),
    INDEX idx_status (status),
    INDEX idx_employee_id (employee_id)
) COMMENT '用户注册申请表';

-- 用户权限配置表
CREATE TABLE IF NOT EXISTS user_permissions (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL COMMENT '用户ID',
    permission_type ENUM('view_salary', 'view_attendance', 'edit_profile', 'view_payslip') NOT NULL COMMENT '权限类型',
    is_granted TINYINT DEFAULT 1 COMMENT '是否授权(1:是, 0:否)',
    granted_by INT COMMENT '授权人ID',
    granted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '授权时间',
    expires_at DATETIME COMMENT '权限过期时间',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (granted_by) REFERENCES users(id),
    UNIQUE KEY uk_user_permission (user_id, permission_type),
    INDEX idx_user_id (user_id),
    INDEX idx_permission_type (permission_type)
) COMMENT '用户权限配置表';

-- 员工信息变更申请表
CREATE TABLE IF NOT EXISTS employee_change_requests (
    id INT AUTO_INCREMENT PRIMARY KEY,
    employee_id INT NOT NULL COMMENT '员工ID',
    user_id INT NOT NULL COMMENT '申请用户ID',
    change_type ENUM('phone', 'email', 'address', 'bank_info', 'emergency_contact') NOT NULL COMMENT '变更类型',
    field_name VARCHAR(50) NOT NULL COMMENT '字段名称',
    old_value TEXT COMMENT '原值',
    new_value TEXT NOT NULL COMMENT '新值',
    reason VARCHAR(255) COMMENT '变更原因',
    status ENUM('pending', 'approved', 'rejected') DEFAULT 'pending' COMMENT '审核状态',
    admin_id INT COMMENT '审核管理员ID',
    admin_remarks VARCHAR(255) COMMENT '管理员审核备注',
    approved_at DATETIME COMMENT '审核时间',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (employee_id) REFERENCES employees(id),
    FOREIGN KEY (user_id) REFERENCES users(id),
    FOREIGN KEY (admin_id) REFERENCES users(id),
    INDEX idx_employee_id (employee_id),
    INDEX idx_user_id (user_id),
    INDEX idx_status (status),
    INDEX idx_change_type (change_type)
) COMMENT '员工信息变更申请表';

-- 员工紧急联系人表
CREATE TABLE IF NOT EXISTS employee_emergency_contacts (
    id INT AUTO_INCREMENT PRIMARY KEY,
    employee_id INT NOT NULL COMMENT '员工ID',
    contact_name VARCHAR(50) NOT NULL COMMENT '联系人姓名',
    relationship VARCHAR(20) NOT NULL COMMENT '关系',
    phone VARCHAR(20) NOT NULL COMMENT '联系电话',
    address VARCHAR(255) COMMENT '联系地址',
    is_primary TINYINT DEFAULT 0 COMMENT '是否主要联系人',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (employee_id) REFERENCES employees(id) ON DELETE CASCADE,
    INDEX idx_employee_id (employee_id)
) COMMENT '员工紧急联系人表';

-- 用户个人设置表
CREATE TABLE IF NOT EXISTS user_settings (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL COMMENT '用户ID',
    setting_key VARCHAR(50) NOT NULL COMMENT '设置键',
    setting_value VARCHAR(255) NOT NULL COMMENT '设置值',
    description VARCHAR(255) COMMENT '设置描述',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    UNIQUE KEY uk_user_setting (user_id, setting_key),
    INDEX idx_user_id (user_id)
) COMMENT '用户个人设置表';

-- 添加员工表缺失字段
ALTER TABLE employees 
ADD COLUMN emergency_contact_name VARCHAR(50) COMMENT '紧急联系人姓名' AFTER bank_account_encrypted,
ADD COLUMN emergency_contact_phone VARCHAR(20) COMMENT '紧急联系人电话' AFTER emergency_contact_name,
ADD COLUMN emergency_contact_relationship VARCHAR(20) COMMENT '紧急联系人关系' AFTER emergency_contact_phone;

-- 创建用户活动日志表
CREATE TABLE IF NOT EXISTS user_activity_logs (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL COMMENT '用户ID',
    action_type VARCHAR(50) NOT NULL COMMENT '操作类型',
    resource_type VARCHAR(50) COMMENT '资源类型',
    resource_id INT COMMENT '资源ID',
    description TEXT COMMENT '操作描述',
    ip_address VARCHAR(50) COMMENT 'IP地址',
    user_agent VARCHAR(255) COMMENT '用户代理',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id),
    INDEX idx_user_id (user_id),
    INDEX idx_action_type (action_type),
    INDEX idx_created_at (created_at)
) COMMENT '用户活动日志表';

-- 初始化默认用户权限
INSERT INTO user_permissions (user_id, permission_type, is_granted, granted_by) 
SELECT 
    u.id,
    'view_salary',
    1,
    (SELECT id FROM users WHERE role = 'admin' LIMIT 1)
FROM users u 
WHERE u.role = 'employee' AND u.employee_id IS NOT NULL;

INSERT INTO user_permissions (user_id, permission_type, is_granted, granted_by) 
SELECT 
    u.id,
    'view_attendance',
    1,
    (SELECT id FROM users WHERE role = 'admin' LIMIT 1)
FROM users u 
WHERE u.role = 'employee' AND u.employee_id IS NOT NULL;

INSERT INTO user_permissions (user_id, permission_type, is_granted, granted_by) 
SELECT 
    u.id,
    'edit_profile',
    1,
    (SELECT id FROM users WHERE role = 'admin' LIMIT 1)
FROM users u 
WHERE u.role = 'employee' AND u.employee_id IS NOT NULL;

INSERT INTO user_permissions (user_id, permission_type, is_granted, granted_by) 
SELECT 
    u.id,
    'view_payslip',
    1,
    (SELECT id FROM users WHERE role = 'admin' LIMIT 1)
FROM users u 
WHERE u.role = 'employee' AND u.employee_id IS NOT NULL;

-- 初始化系统参数
INSERT INTO system_parameters (param_key, param_value, description) VALUES 
('user_registration_enabled', '1', '是否允许用户自助注册'),
('registration_approval_required', '1', '用户注册是否需要管理员审核'),
('employee_info_change_approval', '1', '员工信息变更是否需要审核'),
('max_login_attempts', '5', '最大登录尝试次数'),
('session_timeout_minutes', '120', '会话超时时间(分钟)');

-- 创建视图：用户可访问的薪资记录
CREATE OR REPLACE VIEW user_salary_view AS
SELECT 
    sr.id,
    sr.employee_id,
    sr.year,
    sr.month,
    sr.base_salary,
    sr.overtime_pay,
    sr.bonus,
    sr.performance_bonus,
    sr.attendance_bonus,
    sr.transportation_allowance,
    sr.meal_allowance,
    sr.deduction,
    sr.social_security,
    sr.late_deduction,
    sr.absence_deduction,
    sr.personal_tax,
    sr.net_salary,
    sr.status,
    sr.payment_date,
    sr.created_at,
    e.name as employee_name,
    d.name as department_name,
    p.name as position_name
FROM salary_records sr
JOIN employees e ON sr.employee_id = e.id
JOIN departments d ON e.department_id = d.id
JOIN positions p ON e.position_id = p.id
WHERE e.status = 1;

-- 创建视图：用户可访问的考勤记录
CREATE OR REPLACE VIEW user_attendance_view AS
SELECT 
    a.id,
    a.employee_id,
    a.date,
    a.overtime_hours,
    a.remarks,
    a.created_at,
    ast.name as status_name,
    ast.description as status_description,
    ast.is_deduction,
    ast.deduction_value,
    e.name as employee_name,
    d.name as department_name,
    p.name as position_name
FROM attendance a
JOIN attendance_status ast ON a.status_id = ast.id
JOIN employees e ON a.employee_id = e.id
JOIN departments d ON e.department_id = d.id
JOIN positions p ON e.position_id = p.id
WHERE e.status = 1;

-- 创建索引以提高查询性能
ALTER TABLE user_registrations
ADD INDEX idx_created_at (created_at),
ADD INDEX idx_verification_expires (verification_expires);

ALTER TABLE employee_change_requests
ADD INDEX idx_created_at (created_at),
ADD INDEX idx_approved_at (approved_at);

-- 创建触发器：用户注册成功后自动分配默认权限
DELIMITER //
CREATE TRIGGER IF NOT EXISTS assign_default_permissions_after_user_creation
AFTER INSERT ON users
FOR EACH ROW
BEGIN
    IF NEW.role = 'employee' AND NEW.employee_id IS NOT NULL THEN
        INSERT INTO user_permissions (user_id, permission_type, is_granted, granted_by) VALUES
        (NEW.id, 'view_salary', 1, 1),
        (NEW.id, 'view_attendance', 1, 1),
        (NEW.id, 'edit_profile', 1, 1),
        (NEW.id, 'view_payslip', 1, 1);
    END IF;
END //
DELIMITER ; 