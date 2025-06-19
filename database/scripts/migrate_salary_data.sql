-- 薪资数据迁移脚本
-- 创建日期: 2023-06-14

-- 备份现有数据
CREATE TABLE IF NOT EXISTS salary_records_backup AS SELECT * FROM salary_records;

-- 更新现有记录，将可能存在的数据从薪资明细表中提取到主表对应字段
-- 绩效奖金
UPDATE salary_records sr
JOIN salary_details sd ON sr.id = sd.salary_id
JOIN salary_items si ON sd.item_id = si.id
SET sr.performance_bonus = sd.amount
WHERE si.name = '绩效奖金' AND si.type = 'addition';

-- 全勤奖
UPDATE salary_records sr
JOIN salary_details sd ON sr.id = sd.salary_id
JOIN salary_items si ON sd.item_id = si.id
SET sr.attendance_bonus = sd.amount
WHERE si.name = '全勤奖' AND si.type = 'addition';

-- 交通补贴
UPDATE salary_records sr
JOIN salary_details sd ON sr.id = sd.salary_id
JOIN salary_items si ON sd.item_id = si.id
SET sr.transportation_allowance = sd.amount
WHERE si.name = '交通补贴' AND si.type = 'addition';

-- 餐补
UPDATE salary_records sr
JOIN salary_details sd ON sr.id = sd.salary_id
JOIN salary_items si ON sd.item_id = si.id
SET sr.meal_allowance = sd.amount
WHERE si.name = '餐补' AND si.type = 'addition';

-- 迟到扣款
UPDATE salary_records sr
JOIN salary_details sd ON sr.id = sd.salary_id
JOIN salary_items si ON sd.item_id = si.id
SET sr.late_deduction = sd.amount
WHERE si.name = '迟到扣款' AND si.type = 'deduction';

-- 缺勤扣款
UPDATE salary_records sr
JOIN salary_details sd ON sr.id = sd.salary_id
JOIN salary_items si ON sd.item_id = si.id
SET sr.absence_deduction = sd.amount
WHERE si.name = '缺勤扣款' AND si.type = 'deduction';

-- 更新净工资计算
UPDATE salary_records
SET net_salary = base_salary + overtime_pay + bonus + performance_bonus + attendance_bonus + 
                transportation_allowance + meal_allowance - deduction - social_security - 
                personal_tax - late_deduction - absence_deduction;

-- 创建视图，方便查询完整薪资信息
CREATE OR REPLACE VIEW v_salary_complete AS
SELECT 
    sr.*,
    e.name AS employee_name,
    e.employee_number,
    d.name AS department_name,
    p.name AS position_name,
    (sr.base_salary + sr.overtime_pay + sr.bonus + sr.performance_bonus + 
     sr.attendance_bonus + sr.transportation_allowance + sr.meal_allowance) AS total_income,
    (sr.deduction + sr.social_security + sr.personal_tax + 
     sr.late_deduction + sr.absence_deduction) AS total_deduction
FROM 
    salary_records sr
    JOIN employees e ON sr.employee_id = e.id
    LEFT JOIN departments d ON e.department_id = d.id
    LEFT JOIN positions p ON e.position_id = p.id; 