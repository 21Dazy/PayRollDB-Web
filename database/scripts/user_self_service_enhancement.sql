-- 普通用户自助服务功能增强脚本
-- 创建日期: 2025-06-14

USE salary_management_system;

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
CREATE VIEW user_salary_view AS
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
CREATE VIEW user_attendance_view AS
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