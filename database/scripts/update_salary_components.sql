-- 更新薪资记录表，确保包含所有薪资项目
-- 创建日期: 2023-06-14

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