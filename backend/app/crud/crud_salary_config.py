from typing import List, Optional
from datetime import date
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import and_, or_

from app.crud.base import CRUDBase
from app.models.salary_config import EmployeeSalaryConfig
from app.models.salary_item import SalaryItem
from app.schemas.salary_config import SalaryConfigItemCreate, SalaryConfigItemUpdate

class CRUDSalaryConfig(CRUDBase[EmployeeSalaryConfig, SalaryConfigItemCreate, SalaryConfigItemUpdate]):
    
    def get_employee_config(
        self, 
        db: Session, 
        *, 
        employee_id: int,
        effective_date: Optional[date] = None
    ) -> List[EmployeeSalaryConfig]:
        """获取员工的薪资配置"""
        print(f"获取员工 {employee_id} 的薪资配置，有效日期: {effective_date}")
        
        # 先检查是否有任何配置
        all_configs = db.query(EmployeeSalaryConfig).filter(
            EmployeeSalaryConfig.employee_id == employee_id
        ).all()
        print(f"员工 {employee_id} 的所有配置数量: {len(all_configs)}")
        
        # 打印所有配置的详细信息，帮助诊断问题
        for config in all_configs:
            print(f"配置ID: {config.id}, 项目ID: {config.item_id}, 值: {config.value}, 是否激活: {config.is_active}, 生效日期: {config.effective_date}, 失效日期: {config.expiry_date}")
        
        # 修改查询逻辑，忽略is_active字段，只根据日期判断有效性
        query = db.query(EmployeeSalaryConfig).filter(
            EmployeeSalaryConfig.employee_id == employee_id
        ).options(joinedload(EmployeeSalaryConfig.salary_item))
        
        if effective_date:
            query = query.filter(
                EmployeeSalaryConfig.effective_date <= effective_date,
                or_(
                    EmployeeSalaryConfig.expiry_date.is_(None),
                    EmployeeSalaryConfig.expiry_date >= effective_date
                )
            )
        else:
            # 如果没有提供有效日期，则获取最新的配置
            query = query.order_by(EmployeeSalaryConfig.effective_date.desc())
        
        configs = query.all()
        print(f"获取到 {len(configs)} 条有效薪资配置")
        
        # 检查每个配置的薪资项目
        valid_configs = []
        for config in configs:
            item = db.query(SalaryItem).filter(SalaryItem.id == config.item_id).first()
            if item:
                print(f"薪资配置项: item_id={config.item_id}, value={config.value}, 项目名称={item.name}")
                valid_configs.append(config)
            else:
                print(f"警告: 配置项 {config.id} 引用了不存在的薪资项目 {config.item_id}")
        
        # 如果没有找到有效配置，但有任何配置，则返回最新的配置
        if not valid_configs and all_configs:
            print("没有找到有效配置，尝试返回最新的配置")
            # 按生效日期降序排序
            all_configs.sort(key=lambda x: x.effective_date, reverse=True)
            for config in all_configs:
                item = db.query(SalaryItem).filter(SalaryItem.id == config.item_id).first()
                if item:
                    print(f"使用最新配置: item_id={config.item_id}, value={config.value}, 项目名称={item.name}")
                    valid_configs.append(config)
                    break
        
        return valid_configs
    
    def create_employee_config(
        self,
        db: Session,
        *,
        employee_id: int,
        config_items: List[SalaryConfigItemCreate]
    ) -> List[EmployeeSalaryConfig]:
        """创建员工薪资配置"""
        db_configs = []
        
        for item in config_items:
            db_config = EmployeeSalaryConfig(
                employee_id=employee_id,
                item_id=item.item_id,
                value=item.value,
                base_item=item.base_item,
                is_active=item.is_active,
                effective_date=item.effective_date
            )
            db.add(db_config)
            db_configs.append(db_config)
        
        db.commit()
        
        # 重新加载以获取关联数据
        for config in db_configs:
            db.refresh(config)
        
        return db_configs
    
    def update_employee_config(
        self,
        db: Session,
        *,
        employee_id: int,
        config_items: List[SalaryConfigItemCreate]
    ) -> List[EmployeeSalaryConfig]:
        """更新员工薪资配置"""
        print(f"更新员工 {employee_id} 的薪资配置，收到 {len(config_items)} 条配置项")
        
        # 获取现有配置
        existing_configs = db.query(EmployeeSalaryConfig).filter(
            EmployeeSalaryConfig.employee_id == employee_id
        ).all()
        print(f"员工 {employee_id} 现有配置数量: {len(existing_configs)}")
        
        # 不再禁用所有配置，而是根据项目ID更新或创建
        db_configs = []
        
        for item in config_items:
            print(f"处理配置项: item_id={item.item_id}, value={item.value}")
            
            # 检查是否已存在该项目的配置
            existing = next((
                config for config in existing_configs 
                if config.item_id == item.item_id
            ), None)
            
            if existing:
                print(f"更新现有配置: id={existing.id}, item_id={existing.item_id}")
                # 更新现有配置
                existing.value = item.value
                existing.base_item = item.base_item
                existing.effective_date = item.effective_date or date.today()
                existing.is_active = True
                db.add(existing)
                db_configs.append(existing)
            else:
                print(f"创建新配置: item_id={item.item_id}")
                # 创建新配置
                db_config = EmployeeSalaryConfig(
                    employee_id=employee_id,
                    item_id=item.item_id,
                    value=item.value,
                    base_item=item.base_item,
                    is_active=True,
                    effective_date=item.effective_date or date.today()
                )
                db.add(db_config)
                db_configs.append(db_config)
        
        db.commit()
        
        # 重新加载以获取关联数据
        for config in db_configs:
            db.refresh(config)
        
        print(f"更新了 {len(db_configs)} 条薪资配置")
        return db_configs
    
    def delete_employee_config(
        self,
        db: Session,
        *,
        employee_id: int,
        item_id: Optional[int] = None
    ) -> bool:
        """删除员工薪资配置"""
        query = db.query(EmployeeSalaryConfig).filter(
            EmployeeSalaryConfig.employee_id == employee_id
        )
        
        if item_id:
            query = query.filter(EmployeeSalaryConfig.item_id == item_id)
        
        count = query.delete()
        db.commit()
        
        return count > 0

salary_config = CRUDSalaryConfig(EmployeeSalaryConfig) 