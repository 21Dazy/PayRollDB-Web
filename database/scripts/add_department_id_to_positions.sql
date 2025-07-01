-- 为 positions 表添加 department_id 字段
-- 解决 "Unknown column 'positions.department_id' in 'field list'" 错误

USE salary_management_system;

-- 添加 department_id 字段
ALTER TABLE positions 
ADD COLUMN department_id INT NOT NULL DEFAULT 1 COMMENT '所属部门ID' AFTER name;

-- 添加外键约束
ALTER TABLE positions 
ADD CONSTRAINT fk_positions_department 
FOREIGN KEY (department_id) REFERENCES departments(id);

-- 添加索引以提高查询性能
ALTER TABLE positions 
ADD INDEX idx_department_id (department_id);

-- 如果有现有的职位数据，需要手动设置合适的部门ID
-- 这里设置所有现有职位都属于第一个部门（如果存在的话）
UPDATE positions 
SET department_id = (
    SELECT id FROM departments 
    ORDER BY id 
    LIMIT 1
) 
WHERE department_id = 1;

-- 验证修改结果
SELECT 'positions table structure after modification:' as message;
DESCRIBE positions; 