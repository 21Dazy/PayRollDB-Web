# 导入所有模型，确保SQLAlchemy能够正确创建表关系

from .user import User
from .employee import Employee  
from .department import Department
from .position import Position
from .attendance import Attendance
from .attendance_status import AttendanceStatus
from .salary_record import SalaryRecord
from .salary_detail import SalaryDetail
from .salary_item import SalaryItem
from .salary_config import EmployeeSalaryConfig
from .social_security_config import SocialSecurityConfig
from .employee_social_security import EmployeeSocialSecurity
from .operation_log import OperationLog
from .system_parameter import SystemParameter

# 用户注册相关模型
from .user_registration import (
    UserRegistration,
    UserPermission, 
    EmployeeChangeRequest,
    EmployeeEmergencyContact,
    UserSetting,
    UserActivityLog
) 