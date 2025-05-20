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