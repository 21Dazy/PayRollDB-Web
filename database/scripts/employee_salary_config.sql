-- 员工薪资配置表
USE salary_management_system;

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