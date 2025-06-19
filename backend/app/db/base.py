# Import all the models, so that Base has them before being imported by Alembic

from app.db.base_class import Base, NoUpdateBase

# 导入顺序很重要，先导入基本模型，后导入有关联的模型
from app.models.department import Department
from app.models.position import Position
from app.models.employee import Employee
from app.models.attendance_status import AttendanceStatus
from app.models.attendance import Attendance
from app.models.salary_item import SalaryItem
from app.models.social_security_config import SocialSecurityConfig
from app.models.employee_social_security import EmployeeSocialSecurity
from app.models.salary_record import SalaryRecord
from app.models.salary_detail import SalaryDetail
# 先导入OperationLog，后导入User，避免循环引用问题
from app.models.operation_log import OperationLog
from app.models.user import User
from app.models.system_parameter import SystemParameter

# 导入用户注册相关模型
from app.models.user_registration import (
    UserRegistration,
    UserPermission, 
    EmployeeChangeRequest,
    EmployeeEmergencyContact,
    UserSetting,
    UserActivityLog
)

# 导入关系定义，必须在所有模型导入后
from app.models.relationships import * 