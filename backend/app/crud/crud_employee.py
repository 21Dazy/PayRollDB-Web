from typing import List, Optional, Dict, Any

from sqlalchemy.orm import Session
from sqlalchemy import or_

from app.crud.base import CRUDBase
from app.models.employee import Employee
from app.schemas.employee import EmployeeCreate, EmployeeUpdate


class CRUDEmployee(CRUDBase[Employee, EmployeeCreate, EmployeeUpdate]):
    def get_multi_with_filters(
        self, 
        db: Session, 
        *, 
        skip: int = 0, 
        limit: int = 100,
        department_id: Optional[int] = None,
        position_id: Optional[int] = None,
        status: Optional[bool] = None,
        name: Optional[str] = None
    ) -> List[Employee]:
        """
        获取员工列表，支持筛选
        """
        query = db.query(self.model)
        
        # 应用筛选条件
        if department_id is not None:
            query = query.filter(self.model.department_id == department_id)
        
        if position_id is not None:
            query = query.filter(self.model.position_id == position_id)
        
        if status is not None:
            query = query.filter(self.model.status == status)
        
        if name:
            query = query.filter(self.model.name.like(f"%{name}%"))
        
        # 加载关联的部门和职位信息
        query = query.join(self.model.department).join(self.model.position)
        
        return query.offset(skip).limit(limit).all()
    
    def search_employees(
        self,
        db: Session,
        *,
        keyword: Optional[str] = None,
        department_id: Optional[int] = None,
        skip: int = 0,
        limit: int = 100
    ) -> List[Employee]:
        """
        搜索员工，支持关键词搜索和部门筛选
        
        如果提供了关键词，将搜索员工姓名、工号、职位名称匹配的员工
        如果提供了部门ID，将只返回该部门的员工
        如果同时提供了关键词和部门ID，将返回该部门中匹配关键词的员工
        """
        query = db.query(self.model)
        
        # 应用部门筛选
        if department_id is not None:
            query = query.filter(self.model.department_id == department_id)
        
        # 应用关键词搜索
        if keyword:
            # 使用or_()组合多个搜索条件
            query = query.filter(
                or_(
                    self.model.name.ilike(f"%{keyword}%"),  # 姓名匹配
                    self.model.employee_id.ilike(f"%{keyword}%"),  # 工号匹配
                    # 其他可能的匹配字段，如电话、邮箱等
                    self.model.phone.ilike(f"%{keyword}%"),
                    self.model.email.ilike(f"%{keyword}%") if self.model.email else False
                )
            )
        
        # 默认只返回在职员工
        query = query.filter(self.model.status == True)
        
        # 加载关联的部门和职位信息以便返回详细信息
        query = query.join(self.model.department).join(self.model.position)
        
        return query.offset(skip).limit(limit).all()
    
    def get_with_relations(self, db: Session, id: int) -> Optional[Employee]:
        """
        获取员工详情，包括关联的部门和职位信息
        """
        return (
            db.query(self.model)
            .filter(self.model.id == id)
            .join(self.model.department)
            .join(self.model.position)
            .first()
        )
    
    def create_with_encrypted_bank_account(
        self, db: Session, *, obj_in: EmployeeCreate, encrypted_bank_account: bytes = None
    ) -> Employee:
        """
        创建员工并加密银行账号
        """
        obj_in_data = obj_in.dict()
        if encrypted_bank_account:
            obj_in_data["bank_account_encrypted"] = encrypted_bank_account
        
        db_obj = Employee(**obj_in_data)
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj


employee = CRUDEmployee(Employee) 