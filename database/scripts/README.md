# 薪资管理系统数据库更新说明

## 数据库脚本说明

### 基础数据库脚本
1. `database_design.sql` - 基础数据库设计脚本，创建初始的表结构，包括部门、职位、员工、考勤、薪资等基础表
2. `database_designV2.sql` - 升级版数据库设计脚本，在基础表结构上整合了薪资组成项目字段，优化了表结构和索引
3. `consolidated_database_schema.sql` - 整合数据库脚本，集成了所有数据库设计和更新内容，包含完整的数据库结构

### 功能增强脚本
1. `user_self_service_enhancement.sql` - 用户自助服务功能增强脚本，添加用户注册验证、权限配置、信息变更申请等功能相关表
2. `employee_salary_config.sql` - 员工薪资配置表创建脚本，用于灵活配置员工的各项薪资组成

### 数据更新脚本
1. `update_salary_components.sql` - 薪资组成项目更新脚本，向薪资记录表添加新字段，创建触发器自动计算净工资
2. `migrate_salary_data.sql` - 薪资数据迁移脚本，将薪资明细数据迁移到薪资记录表的新字段中

## 薪资组成项目更新

为了确保薪资记录表包含所有薪资项目，我们创建了以下SQL脚本：

### 1. 数据库结构更新

执行 `update_salary_components.sql` 脚本，该脚本将：

- 向薪资记录表添加新的字段（绩效奖金、全勤奖、交通补贴、餐补、迟到扣款、缺勤扣款）
- 创建触发器自动计算净工资
- 添加索引提高查询性能
- 更新表注释

```bash
mysql -u username -p database_name < update_salary_components.sql
```

### 2. 数据迁移

执行 `migrate_salary_data.sql` 脚本，该脚本将：

- 备份现有薪资记录数据
- 从薪资明细表中提取数据到新增的字段
- 更新净工资计算
- 创建视图方便查询完整薪资信息

```bash
mysql -u username -p database_name < migrate_salary_data.sql
```

## 注意事项

1. 执行脚本前请先备份数据库
2. 执行顺序：先执行结构更新脚本，再执行数据迁移脚本
3. 更新完成后，需要重启应用服务器以使新的模型生效
4. 如果在执行过程中遇到错误，请查看MySQL错误日志并根据情况回滚

## 回滚方案

如果需要回滚更新，可以执行以下SQL语句：

```sql
-- 删除新增的字段
ALTER TABLE salary_records
DROP COLUMN performance_bonus,
DROP COLUMN attendance_bonus,
DROP COLUMN transportation_allowance,
DROP COLUMN meal_allowance,
DROP COLUMN late_deduction,
DROP COLUMN absence_deduction;

-- 删除触发器
DROP TRIGGER IF EXISTS calculate_net_salary_before_insert;
DROP TRIGGER IF EXISTS calculate_net_salary_before_update;

-- 删除视图
DROP VIEW IF EXISTS v_salary_complete;
``` 