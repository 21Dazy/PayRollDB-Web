# 工资管理系统 API 文档

## 基础信息

- 基础路径: `/api/v1`
- 认证方式: Bearer Token (JWT)
- 响应格式: JSON

## 目录

1. [身份验证](#1-身份验证)
2. [用户管理](#2-用户管理)
3. [部门管理](#3-部门管理)
4. [职位管理](#4-职位管理)
5. [员工管理](#5-员工管理)
6. [考勤管理](#6-考勤管理)
7. [工资管理](#7-工资管理)
8. [社保管理](#8-社保管理)
9. [系统管理](#9-系统管理)

## 1. 身份验证

### 1.1 用户登录

- **接口**: `POST /auth/login`
- **描述**: 用户登录获取访问令牌
- **权限**: 无需认证
- **请求体**:
  ```json
  {
    "username": "admin",
    "password": "password123"
  }
  ```
- **响应**:
  ```json
  {
    "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "token_type": "bearer"
  }
  ```
- **状态码**:
  - `200 OK`: 登录成功
  - `401 Unauthorized`: 用户名或密码错误
  - `400 Bad Request`: 用户未激活

### 1.2 获取当前用户信息

- **接口**: `GET /auth/me`
- **描述**: 获取当前登录用户信息
- **权限**: 已登录用户
- **响应**:
  ```json
  {
    "id": 1,
    "username": "admin",
    "employee_id": null,
    "role": "admin",
    "is_active": true,
    "last_login": "2023-05-20T10:30:00"
  }
  ```
- **状态码**:
  - `200 OK`: 成功
  - `401 Unauthorized`: 未认证

## 2. 用户管理

### 2.1 获取用户列表

- **接口**: `GET /users/`
- **描述**: 获取系统用户列表
- **权限**: 管理员
- **查询参数**:
  - `skip`: 跳过记录数 (默认: 0)
  - `limit`: 返回记录数 (默认: 100)
  - `role`: 按角色筛选 (可选)
  - `is_active`: 按状态筛选 (可选)
- **响应**:
  ```json
  [
    {
      "id": 1,
      "username": "admin",
      "employee_id": null,
      "role": "admin",
      "is_active": true,
      "last_login": "2023-05-20T10:30:00"
    },
    // ...
  ]
  ```

### 2.2 创建用户

- **接口**: `POST /users/`
- **描述**: 创建新用户
- **权限**: 管理员
- **请求体**:
  ```json
  {
    "username": "newuser",
    "password": "password123",
    "employee_id": 5,
    "role": "employee"
  }
  ```
- **响应**:
  ```json
  {
    "id": 10,
    "username": "newuser",
    "employee_id": 5,
    "role": "employee",
    "is_active": true,
    "last_login": null
  }
  ```
- **状态码**:
  - `201 Created`: 创建成功
  - `400 Bad Request`: 请求数据无效
  - `409 Conflict`: 用户名已存在

### 2.3 获取单个用户

- **接口**: `GET /users/{user_id}`
- **描述**: 获取指定用户详情
- **权限**: 管理员
- **路径参数**:
  - `user_id`: 用户ID
- **响应**:
  ```json
  {
    "id": 10,
    "username": "newuser",
    "employee_id": 5,
    "role": "employee",
    "is_active": true,
    "last_login": null
  }
  ```
- **状态码**:
  - `200 OK`: 成功
  - `404 Not Found`: 用户不存在

### 2.4 更新用户

- **接口**: `PUT /users/{user_id}`
- **描述**: 更新用户信息
- **权限**: 管理员
- **路径参数**:
  - `user_id`: 用户ID
- **请求体**:
  ```json
  {
    "username": "updateduser",
    "role": "hr",
    "is_active": false
  }
  ```
- **响应**:
  ```json
  {
    "id": 10,
    "username": "updateduser",
    "employee_id": 5,
    "role": "hr",
    "is_active": false,
    "last_login": null
  }
  ```
- **状态码**:
  - `200 OK`: 更新成功
  - `404 Not Found`: 用户不存在
  - `409 Conflict`: 用户名已存在

### 2.5 删除用户

- **接口**: `DELETE /users/{user_id}`
- **描述**: 删除用户
- **权限**: 管理员
- **路径参数**:
  - `user_id`: 用户ID
- **状态码**:
  - `204 No Content`: 删除成功
  - `404 Not Found`: 用户不存在

### 2.6 修改密码

- **接口**: `POST /users/{user_id}/change-password`
- **描述**: 修改用户密码
- **权限**: 管理员或本人
- **路径参数**:
  - `user_id`: 用户ID
- **请求体**:
  ```json
  {
    "current_password": "oldpassword",
    "new_password": "newpassword"
  }
  ```
- **状态码**:
  - `200 OK`: 密码修改成功
  - `400 Bad Request`: 当前密码错误
  - `404 Not Found`: 用户不存在

## 3. 部门管理

### 3.1 获取部门列表

- **接口**: `GET /departments/`
- **描述**: 获取所有部门列表
- **权限**: 已登录用户
- **查询参数**:
  - `skip`: 跳过记录数 (默认: 0)
  - `limit`: 返回记录数 (默认: 100)
- **响应**:
  ```json
  [
    {
      "id": 1,
      "name": "人力资源部",
      "description": "负责人员招聘和管理",
      "created_at": "2023-01-01T00:00:00",
      "updated_at": "2023-01-01T00:00:00"
    },
    // ...
  ]
  ```

### 3.2 获取部门及员工数量

- **接口**: `GET /departments/with-employee-count`
- **描述**: 获取部门列表及各部门员工数量
- **权限**: 已登录用户
- **响应**:
  ```json
  [
    {
      "id": 1,
      "name": "人力资源部",
      "description": "负责人员招聘和管理",
      "created_at": "2023-01-01T00:00:00",
      "updated_at": "2023-01-01T00:00:00",
      "employee_count": 5
    },
    // ...
  ]
  ```

### 3.3 创建部门

- **接口**: `POST /departments/`
- **描述**: 创建新部门
- **权限**: HR或管理员
- **请求体**:
  ```json
  {
    "name": "市场营销部",
    "description": "负责产品营销和推广"
  }
  ```
- **响应**:
  ```json
  {
    "id": 5,
    "name": "市场营销部",
    "description": "负责产品营销和推广",
    "created_at": "2023-05-20T15:30:00",
    "updated_at": "2023-05-20T15:30:00"
  }
  ```
- **状态码**:
  - `201 Created`: 创建成功
  - `400 Bad Request`: 请求数据无效

### 3.4 获取部门详情

- **接口**: `GET /departments/{department_id}`
- **描述**: 获取特定部门详情
- **权限**: 已登录用户
- **路径参数**:
  - `department_id`: 部门ID
- **响应**:
  ```json
  {
    "id": 5,
    "name": "市场营销部",
    "description": "负责产品营销和推广",
    "created_at": "2023-05-20T15:30:00",
    "updated_at": "2023-05-20T15:30:00"
  }
  ```
- **状态码**:
  - `200 OK`: 成功
  - `404 Not Found`: 部门不存在

### 3.5 更新部门

- **接口**: `PUT /departments/{department_id}`
- **描述**: 更新部门信息
- **权限**: HR或管理员
- **路径参数**:
  - `department_id`: 部门ID
- **请求体**:
  ```json
  {
    "name": "市场部",
    "description": "负责市场营销和品牌推广"
  }
  ```
- **响应**:
  ```json
  {
    "id": 5,
    "name": "市场部",
    "description": "负责市场营销和品牌推广",
    "created_at": "2023-05-20T15:30:00",
    "updated_at": "2023-05-20T16:00:00"
  }
  ```
- **状态码**:
  - `200 OK`: 更新成功
  - `404 Not Found`: 部门不存在

### 3.6 删除部门

- **接口**: `DELETE /departments/{department_id}`
- **描述**: 删除部门（仅当部门下没有员工时可删除）
- **权限**: HR或管理员
- **路径参数**:
  - `department_id`: 部门ID
- **状态码**:
  - `204 No Content`: 删除成功
  - `400 Bad Request`: 部门下有员工，无法删除
  - `404 Not Found`: 部门不存在

## 4. 职位管理

### 4.1 获取职位列表

- **接口**: `GET /positions/`
- **描述**: 获取所有职位列表
- **权限**: 已登录用户
- **查询参数**:
  - `skip`: 跳过记录数 (默认: 0)
  - `limit`: 返回记录数 (默认: 100)
- **响应**:
  ```json
  [
    {
      "id": 1,
      "name": "总经理",
      "description": "公司最高管理者",
      "created_at": "2023-01-01T00:00:00",
      "updated_at": "2023-01-01T00:00:00"
    },
    // ...
  ]
  ```

### 4.2 创建职位

- **接口**: `POST /positions/`
- **描述**: 创建新职位
- **权限**: HR或管理员
- **请求体**:
  ```json
  {
    "name": "项目经理",
    "description": "负责项目规划和执行"
  }
  ```
- **响应**:
  ```json
  {
    "id": 8,
    "name": "项目经理",
    "description": "负责项目规划和执行",
    "created_at": "2023-05-20T15:40:00",
    "updated_at": "2023-05-20T15:40:00"
  }
  ```
- **状态码**:
  - `201 Created`: 创建成功
  - `400 Bad Request`: 请求数据无效

### 4.3 获取职位详情

- **接口**: `GET /positions/{position_id}`
- **描述**: 获取特定职位详情
- **权限**: 已登录用户
- **路径参数**:
  - `position_id`: 职位ID
- **响应**:
  ```json
  {
    "id": 8,
    "name": "项目经理",
    "description": "负责项目规划和执行",
    "created_at": "2023-05-20T15:40:00",
    "updated_at": "2023-05-20T15:40:00"
  }
  ```
- **状态码**:
  - `200 OK`: 成功
  - `404 Not Found`: 职位不存在

### 4.4 更新职位

- **接口**: `PUT /positions/{position_id}`
- **描述**: 更新职位信息
- **权限**: HR或管理员
- **路径参数**:
  - `position_id`: 职位ID
- **请求体**:
  ```json
  {
    "name": "高级项目经理",
    "description": "负责重要项目的规划和执行"
  }
  ```
- **响应**:
  ```json
  {
    "id": 8,
    "name": "高级项目经理",
    "description": "负责重要项目的规划和执行",
    "created_at": "2023-05-20T15:40:00",
    "updated_at": "2023-05-20T16:10:00"
  }
  ```
- **状态码**:
  - `200 OK`: 更新成功
  - `404 Not Found`: 职位不存在

### 4.5 删除职位

- **接口**: `DELETE /positions/{position_id}`
- **描述**: 删除职位（仅当职位下没有员工时可删除）
- **权限**: HR或管理员
- **路径参数**:
  - `position_id`: 职位ID
- **状态码**:
  - `204 No Content`: 删除成功
  - `400 Bad Request`: 职位下有员工，无法删除
  - `404 Not Found`: 职位不存在

## 5. 员工管理

### 5.1 获取员工列表

- **接口**: `GET /employees/`
- **描述**: 获取员工列表
- **权限**: 已登录用户
- **查询参数**:
  - `skip`: 跳过记录数 (默认: 0)
  - `limit`: 返回记录数 (默认: 100)
  - `department_id`: 按部门筛选 (可选)
  - `position_id`: 按职位筛选 (可选)
  - `status`: 按状态筛选 (可选，1:在职，0:离职)
  - `name`: 按姓名搜索 (可选)
- **响应**:
  ```json
  [
    {
      "id": 1,
      "name": "张三",
      "department": {
        "id": 1,
        "name": "人力资源部"
      },
      "position": {
        "id": 3,
        "name": "HR专员"
      },
      "base_salary": 8000.00,
      "hire_date": "2022-01-15",
      "status": true,
      "phone": "13800138000",
      "email": "zhangsan@example.com"
    },
    // ...
  ]
  ```

### 5.2 创建员工

- **接口**: `POST /employees/`
- **描述**: 创建新员工
- **权限**: HR或管理员
- **请求体**:
  ```json
  {
    "name": "李四",
    "department_id": 2,
    "position_id": 5,
    "base_salary": 10000.00,
    "hire_date": "2023-05-01",
    "phone": "13900139000",
    "email": "lisi@example.com",
    "address": "北京市朝阳区",
    "id_card": "110101199001011234",
    "bank_name": "中国建设银行",
    "bank_account": "6227001234567890123"
  }
  ```
- **响应**:
  ```json
  {
    "id": 10,
    "name": "李四",
    "department_id": 2,
    "position_id": 5,
    "base_salary": 10000.00,
    "hire_date": "2023-05-01",
    "status": true,
    "phone": "13900139000",
    "email": "lisi@example.com",
    "address": "北京市朝阳区",
    "id_card": "110101199001011234",
    "bank_name": "中国建设银行",
    "created_at": "2023-05-20T16:20:00",
    "updated_at": "2023-05-20T16:20:00"
  }
  ```
- **状态码**:
  - `201 Created`: 创建成功
  - `400 Bad Request`: 请求数据无效

### 5.3 获取员工详情

- **接口**: `GET /employees/{employee_id}`
- **描述**: 获取特定员工详情
- **权限**: 已登录用户
- **路径参数**:
  - `employee_id`: 员工ID
- **响应**:
  ```json
  {
    "id": 10,
    "name": "李四",
    "department": {
      "id": 2,
      "name": "技术部"
    },
    "position": {
      "id": 5,
      "name": "高级工程师"
    },
    "base_salary": 10000.00,
    "hire_date": "2023-05-01",
    "status": true,
    "phone": "13900139000",
    "email": "lisi@example.com",
    "address": "北京市朝阳区",
    "id_card": "110101199001011234",
    "bank_name": "中国建设银行",
    "bank_account": "6227001234567890123",
    "created_at": "2023-05-20T16:20:00",
    "updated_at": "2023-05-20T16:20:00"
  }
  ```
- **状态码**:
  - `200 OK`: 成功
  - `404 Not Found`: 员工不存在

### 5.4 更新员工信息

- **接口**: `PUT /employees/{employee_id}`
- **描述**: 更新员工信息
- **权限**: HR或管理员
- **路径参数**:
  - `employee_id`: 员工ID
- **请求体**:
  ```json
  {
    "department_id": 3,
    "position_id": 6,
    "base_salary": 12000.00,
    "phone": "13900139001",
    "email": "lisi_new@example.com"
  }
  ```
- **响应**:
  ```json
  {
    "id": 10,
    "name": "李四",
    "department_id": 3,
    "position_id": 6,
    "base_salary": 12000.00,
    "hire_date": "2023-05-01",
    "status": true,
    "phone": "13900139001",
    "email": "lisi_new@example.com",
    "address": "北京市朝阳区",
    "id_card": "110101199001011234",
    "bank_name": "中国建设银行",
    "updated_at": "2023-05-20T16:30:00"
  }
  ```
- **状态码**:
  - `200 OK`: 更新成功
  - `404 Not Found`: 员工不存在

### 5.5 离职员工

- **接口**: `PUT /employees/{employee_id}/leave`
- **描述**: 设置员工离职状态
- **权限**: HR或管理员
- **路径参数**:
  - `employee_id`: 员工ID
- **请求体**:
  ```json
  {
    "leave_date": "2023-06-30",
    "remarks": "个人原因离职"
  }
  ```
- **响应**:
  ```json
  {
    "id": 10,
    "name": "李四",
    "status": false,
    "updated_at": "2023-05-20T16:40:00"
  }
  ```
- **状态码**:
  - `200 OK`: 更新成功
  - `404 Not Found`: 员工不存在

### 5.6 获取员工工资记录

- **接口**: `GET /employees/{employee_id}/salaries`
- **描述**: 获取特定员工的工资记录
- **权限**: HR、管理员或本人
- **路径参数**:
  - `employee_id`: 员工ID
- **查询参数**:
  - `year`: 年份筛选 (可选)
  - `month`: 月份筛选 (可选)
- **响应**:
  ```json
  [
    {
      "id": 101,
      "year": 2023,
      "month": 4,
      "base_salary": 10000.00,
      "overtime_pay": 500.00,
      "bonus": 1000.00,
      "deduction": 200.00,
      "social_security": 1500.00,
      "personal_tax": 500.00,
      "net_salary": 9300.00,
      "status": "paid",
      "payment_date": "2023-05-10T10:00:00"
    },
    // ...
  ]
  ```

### 5.7 获取员工考勤记录

- **接口**: `GET /employees/{employee_id}/attendance`
- **描述**: 获取特定员工的考勤记录
- **权限**: HR、管理员或本人
- **路径参数**:
  - `employee_id`: 员工ID
- **查询参数**:
  - `start_date`: 开始日期 (格式: YYYY-MM-DD)
  - `end_date`: 结束日期 (格式: YYYY-MM-DD)
- **响应**:
  ```json
  [
    {
      "id": 501,
      "date": "2023-05-01",
      "status": {
        "id": 1,
        "name": "正常"
      },
      "overtime_hours": 0,
      "remarks": null
    },
    // ...
  ]
  ```

## 6. 考勤管理

### 6.1 获取考勤状态列表

- **接口**: `GET /attendance/status`
- **描述**: 获取所有考勤状态类型
- **权限**: 已登录用户
- **响应**:
  ```json
  [
    {
      "id": 1,
      "name": "正常",
      "description": "正常出勤",
      "is_deduction": false,
      "deduction_value": 0
    },
    {
      "id": 2,
      "name": "迟到",
      "description": "迟到",
      "is_deduction": true,
      "deduction_value": 50
    },
    // ...
  ]
  ```

### 6.2 创建考勤状态

- **接口**: `POST /attendance/status`
- **描述**: 创建新考勤状态
- **权限**: HR或管理员
- **请求体**:
  ```json
  {
    "name": "培训",
    "description": "参加培训",
    "is_deduction": false,
    "deduction_value": 0
  }
  ```
- **响应**:
  ```json
  {
    "id": 9,
    "name": "培训",
    "description": "参加培训",
    "is_deduction": false,
    "deduction_value": 0,
    "created_at": "2023-05-20T17:00:00",
    "updated_at": "2023-05-20T17:00:00"
  }
  ```

### 6.3 更新考勤状态

- **接口**: `PUT /attendance/status/{status_id}`
- **描述**: 更新考勤状态
- **权限**: HR或管理员
- **路径参数**:
  - `status_id`: 状态ID
- **请求体**:
  ```json
  {
    "name": "培训",
    "description": "外部培训",
    "is_deduction": false,
    "deduction_value": 0
  }
  ```
- **响应**:
  ```json
  {
    "id": 9,
    "name": "培训",
    "description": "外部培训",
    "is_deduction": false,
    "deduction_value": 0,
    "updated_at": "2023-05-20T17:10:00"
  }
  ```

### 6.4 获取考勤记录

- **接口**: `GET /attendance/`
- **描述**: 获取考勤记录列表
- **权限**: HR或管理员
- **查询参数**:
  - `start_date`: 开始日期 (格式: YYYY-MM-DD)
  - `end_date`: 结束日期 (格式: YYYY-MM-DD)
  - `department_id`: 按部门筛选 (可选)
  - `employee_id`: 按员工筛选 (可选)
  - `status_id`: 按状态筛选 (可选)
- **响应**:
  ```json
  [
    {
      "id": 1001,
      "employee": {
        "id": 5,
        "name": "王五"
      },
      "date": "2023-05-01",
      "status": {
        "id": 1,
        "name": "正常"
      },
      "overtime_hours": 2,
      "remarks": "加班处理紧急项目"
    },
    // ...
  ]
  ```

### 6.5 创建考勤记录

- **接口**: `POST /attendance/`
- **描述**: 创建新考勤记录
- **权限**: HR或管理员
- **请求体**:
  ```json
  {
    "employee_id": 5,
    "date": "2023-05-21",
    "status_id": 1,
    "overtime_hours": 1.5,
    "remarks": "加班完成月度报表"
  }
  ```
- **响应**:
  ```json
  {
    "id": 1050,
    "employee_id": 5,
    "date": "2023-05-21",
    "status_id": 1,
    "overtime_hours": 1.5,
    "remarks": "加班完成月度报表",
    "created_at": "2023-05-20T17:20:00",
    "updated_at": "2023-05-20T17:20:00"
  }
  ```
- **状态码**:
  - `201 Created`: 创建成功
  - `400 Bad Request`: 请求数据无效或该员工当日已有考勤记录

### 6.6 更新考勤记录

- **接口**: `PUT /attendance/{attendance_id}`
- **描述**: 更新考勤记录
- **权限**: HR或管理员
- **路径参数**:
  - `attendance_id`: 考勤记录ID
- **请求体**:
  ```json
  {
    "status_id": 2,
    "overtime_hours": 0,
    "remarks": "迟到30分钟"
  }
  ```
- **响应**:
  ```json
  {
    "id": 1050,
    "employee_id": 5,
    "date": "2023-05-21",
    "status_id": 2,
    "overtime_hours": 0,
    "remarks": "迟到30分钟",
    "updated_at": "2023-05-20T17:30:00"
  }
  ```

### 6.7 批量导入考勤记录

- **接口**: `POST /attendance/batch`
- **描述**: 批量导入考勤记录
- **权限**: HR或管理员
- **请求体**:
  ```json
  {
    "records": [
      {
        "employee_id": 1,
        "date": "2023-05-21",
        "status_id": 1,
        "overtime_hours": 0
      },
      {
        "employee_id": 2,
        "date": "2023-05-21",
        "status_id": 1,
        "overtime_hours": 0
      },
      // ...
    ]
  }
  ```
- **响应**:
  ```json
  {
    "success_count": 10,
    "failed_count": 0,
    "failed_records": []
  }
  ```

## 7. 工资管理

### 7.1 获取工资项目列表

- **接口**: `GET /salaries/items`
- **描述**: 获取工资组成项目列表
- **权限**: HR或管理员
- **响应**:
  ```json
  [
    {
      "id": 1,
      "name": "基本工资",
      "type": "addition",
      "is_percentage": false,
      "is_system": true
    },
    {
      "id": 2,
      "name": "加班费",
      "type": "addition",
      "is_percentage": false,
      "is_system": true
    },
    // ...
  ]
  ```

### 7.2 创建工资项目

- **接口**: `POST /salaries/items`
- **描述**: 创建新工资项目
- **权限**: HR或管理员
- **请求体**:
  ```json
  {
    "name": "项目奖金",
    "type": "addition",
    "is_percentage": false,
    "is_system": false
  }
  ```
- **响应**:
  ```json
  {
    "id": 12,
    "name": "项目奖金",
    "type": "addition",
    "is_percentage": false,
    "is_system": false,
    "created_at": "2023-05-20T18:00:00",
    "updated_at": "2023-05-20T18:00:00"
  }
  ```

### 7.3 更新工资项目

- **接口**: `PUT /salaries/items/{item_id}`
- **描述**: 更新工资项目
- **权限**: HR或管理员
- **路径参数**:
  - `item_id`: 工资项目ID
- **请求体**:
  ```json
  {
    "name": "季度项目奖金",
    "type": "addition",
    "is_percentage": false
  }
  ```
- **响应**:
  ```json
  {
    "id": 12,
    "name": "季度项目奖金",
    "type": "addition",
    "is_percentage": false,
    "is_system": false,
    "updated_at": "2023-05-20T18:10:00"
  }
  ```
- **状态码**:
  - `200 OK`: 更新成功
  - `400 Bad Request`: 系统项不可修改
  - `404 Not Found`: 项目不存在

### 7.4 获取工资记录列表

- **接口**: `GET /salaries/records`
- **描述**: 获取工资记录列表
- **权限**: HR或管理员
- **查询参数**:
  - `year`: 年份筛选
  - `month`: 月份筛选
  - `department_id`: 按部门筛选 (可选)
  - `employee_id`: 按员工筛选 (可选)
  - `status`: 按状态筛选 (可选: pending, paid)
- **响应**:
  ```json
  [
    {
      "id": 2001,
      "employee": {
        "id": 5,
        "name": "王五"
      },
      "year": 2023,
      "month": 4,
      "base_salary": 12000.00,
      "overtime_pay": 600.00,
      "bonus": 1000.00,
      "deduction": 0.00,
      "social_security": 1800.00,
      "personal_tax": 580.00,
      "net_salary": 11220.00,
      "status": "paid",
      "payment_date": "2023-05-10T10:00:00"
    },
    // ...
  ]
  ```

### 7.5 生成月度工资记录

- **接口**: `POST /salaries/generate`
- **描述**: 生成指定月份的工资记录
- **权限**: HR或管理员
- **请求体**:
  ```json
  {
    "year": 2023,
    "month": 5,
    "department_id": null  // 可选，不指定则生成所有部门
  }
  ```
- **响应**:
  ```json
  {
    "success": true,
    "total_count": 50,
    "message": "成功生成50条工资记录"
  }
  ```
- **状态码**:
  - `200 OK`: 生成成功
  - `400 Bad Request`: 参数无效或该月工资已生成

### 7.6 获取单条工资记录详情

- **接口**: `GET /salaries/records/{record_id}`
- **描述**: 获取单条工资记录及明细
- **权限**: HR、管理员或本人
- **路径参数**:
  - `record_id`: 工资记录ID
- **响应**:
  ```json
  {
    "id": 2001,
    "employee": {
      "id": 5,
      "name": "王五",
      "department": {
        "id": 2,
        "name": "技术部"
      }
    },
    "year": 2023,
    "month": 4,
    "base_salary": 12000.00,
    "overtime_pay": 600.00,
    "bonus": 1000.00,
    "deduction": 0.00,
    "social_security": 1800.00,
    "personal_tax": 580.00,
    "net_salary": 11220.00,
    "status": "paid",
    "payment_date": "2023-05-10T10:00:00",
    "remark": null,
    "details": [
      {
        "id": 5001,
        "item": {
          "id": 1,
          "name": "基本工资"
        },
        "amount": 12000.00
      },
      {
        "id": 5002,
        "item": {
          "id": 2,
          "name": "加班费"
        },
        "amount": 600.00
      },
      // ...
    ]
  }
  ```

### 7.7 更新工资记录

- **接口**: `PUT /salaries/records/{record_id}`
- **描述**: 更新工资记录
- **权限**: HR或管理员
- **路径参数**:
  - `record_id`: 工资记录ID
- **请求体**:
  ```json
  {
    "bonus": 1500.00,
    "remark": "增加季度绩效奖金",
    "details": [
      {
        "item_id": 3,
        "amount": 1500.00
      }
    ]
  }
  ```
- **响应**:
  ```json
  {
    "id": 2001,
    "bonus": 1500.00,
    "net_salary": 11720.00,
    "remark": "增加季度绩效奖金",
    "updated_at": "2023-05-20T18:30:00"
  }
  ```

### 7.8 批量发放工资

- **接口**: `POST /salaries/pay`
- **描述**: 批量更新工资记录状态为已发放
- **权限**: HR或管理员
- **请求体**:
  ```json
  {
    "record_ids": [2001, 2002, 2003, 2004],
    "payment_date": "2023-05-20T00:00:00"
  }
  ```
- **响应**:
  ```json
  {
    "success": true,
    "count": 4,
    "message": "成功更新4条工资记录为已发放状态"
  }
  ```

### 7.9 导出工资单

- **接口**: `GET /salaries/export`
- **描述**: 导出工资单（CSV或Excel格式）
- **权限**: HR或管理员
- **查询参数**:
  - `year`: 年份
  - `month`: 月份
  - `department_id`: 部门ID (可选)
  - `format`: 导出格式 (csv 或 excel)
- **响应**: 文件下载

## 8. 社保管理

### 8.1 获取社保配置列表

- **接口**: `GET /social-security/configs`
- **描述**: 获取社保公积金配置列表
- **权限**: HR或管理员
- **响应**:
  ```json
  [
    {
      "id": 1,
      "name": "默认配置",
      "pension_rate": 8.00,
      "medical_rate": 2.00,
      "unemployment_rate": 0.50,
      "injury_rate": 0.00,
      "maternity_rate": 0.00,
      "housing_fund_rate": 12.00,
      "is_default": true
    },
    // ...
  ]
  ```

### 8.2 创建社保配置

- **接口**: `POST /social-security/configs`
- **描述**: 创建新社保公积金配置
- **权限**: HR或管理员
- **请求体**:
  ```json
  {
    "name": "高比例配置",
    "pension_rate": 8.00,
    "medical_rate": 2.00,
    "unemployment_rate": 0.50,
    "injury_rate": 0.00,
    "maternity_rate": 0.00,
    "housing_fund_rate": 15.00,
    "is_default": false
  }
  ```
- **响应**:
  ```json
  {
    "id": 2,
    "name": "高比例配置",
    "pension_rate": 8.00,
    "medical_rate": 2.00,
    "unemployment_rate": 0.50,
    "injury_rate": 0.00,
    "maternity_rate": 0.00,
    "housing_fund_rate": 15.00,
    "is_default": false,
    "created_at": "2023-05-20T19:00:00",
    "updated_at": "2023-05-20T19:00:00"
  }
  ```

### 8.3 更新社保配置

- **接口**: `PUT /social-security/configs/{config_id}`
- **描述**: 更新社保公积金配置
- **权限**: HR或管理员
- **路径参数**:
  - `config_id`: 配置ID
- **请求体**:
  ```json
  {
    "name": "高比例公积金配置",
    "housing_fund_rate": 20.00
  }
  ```
- **响应**:
  ```json
  {
    "id": 2,
    "name": "高比例公积金配置",
    "pension_rate": 8.00,
    "medical_rate": 2.00,
    "unemployment_rate": 0.50,
    "injury_rate": 0.00,
    "maternity_rate": 0.00,
    "housing_fund_rate": 20.00,
    "is_default": false,
    "updated_at": "2023-05-20T19:10:00"
  }
  ```

### 8.4 设置默认社保配置

- **接口**: `PUT /social-security/configs/{config_id}/set-default`
- **描述**: 设置指定配置为默认配置
- **权限**: HR或管理员
- **路径参数**:
  - `config_id`: 配置ID
- **响应**:
  ```json
  {
    "success": true,
    "message": "成功设置默认配置"
  }
  ```

### 8.5 获取员工社保配置

- **接口**: `GET /social-security/employees`
- **描述**: 获取员工社保公积金配置列表
- **权限**: HR或管理员
- **查询参数**:
  - `department_id`: 按部门筛选 (可选)
  - `employee_id`: 按员工筛选 (可选)
- **响应**:
  ```json
  [
    {
      "id": 101,
      "employee": {
        "id": 5,
        "name": "王五"
      },
      "config": {
        "id": 1,
        "name": "默认配置"
      },
      "base_number": 5000.00,
      "housing_fund_base": 5000.00,
      "effective_date": "2023-01-01"
    },
    // ...
  ]
  ```

### 8.6 设置员工社保配置

- **接口**: `POST /social-security/employees`
- **描述**: 为员工设置社保公积金配置
- **权限**: HR或管理员
- **请求体**:
  ```json
  {
    "employee_id": 10,
    "config_id": 2,
    "base_number": 6000.00,
    "housing_fund_base": 6000.00,
    "effective_date": "2023-06-01"
  }
  ```
- **响应**:
  ```json
  {
    "id": 120,
    "employee_id": 10,
    "config_id": 2,
    "base_number": 6000.00,
    "housing_fund_base": 6000.00,
    "effective_date": "2023-06-01",
    "created_at": "2023-05-20T19:20:00",
    "updated_at": "2023-05-20T19:20:00"
  }
  ```

### 8.7 更新员工社保配置

- **接口**: `PUT /social-security/employees/{record_id}`
- **描述**: 更新员工社保公积金配置
- **权限**: HR或管理员
- **路径参数**:
  - `record_id`: 记录ID
- **请求体**:
  ```json
  {
    "config_id": 1,
    "base_number": 8000.00,
    "housing_fund_base": 8000.00,
    "effective_date": "2023-07-01"
  }
  ```
- **响应**:
  ```json
  {
    "id": 120,
    "employee_id": 10,
    "config_id": 1,
    "base_number": 8000.00,
    "housing_fund_base": 8000.00,
    "effective_date": "2023-07-01",
    "updated_at": "2023-05-20T19:30:00"
  }
  ```

### 8.8 批量设置员工社保配置

- **接口**: `POST /social-security/employees/batch`
- **描述**: 批量设置员工社保公积金配置
- **权限**: HR或管理员
- **请求体**:
  ```json
  {
    "config_id": 1,
    "employee_ids": [11, 12, 13, 14],
    "base_number": 6000.00,
    "housing_fund_base": 6000.00,
    "effective_date": "2023-06-01"
  }
  ```
- **响应**:
  ```json
  {
    "success": true,
    "count": 4,
    "message": "成功设置4名员工的社保公积金配置"
  }
  ```

## 9. 系统管理

### 9.1 获取系统参数列表

- **接口**: `GET /system/parameters`
- **描述**: 获取系统参数列表
- **权限**: 管理员
- **响应**:
  ```json
  [
    {
      "id": 1,
      "param_key": "overtime_rate",
      "param_value": "1.5",
      "description": "加班费率(工作日)"
    },
    {
      "id": 2,
      "param_key": "weekend_overtime_rate",
      "param_value": "2",
      "description": "加班费率(周末)"
    },
    // ...
  ]
  ```

### 9.2 更新系统参数

- **接口**: `PUT /system/parameters/{param_id}`
- **描述**: 更新系统参数
- **权限**: 管理员
- **路径参数**:
  - `param_id`: 参数ID
- **请求体**:
  ```json
  {
    "param_value": "2.0",
    "description": "更新后的工作日加班费率"
  }
  ```
- **响应**:
  ```json
  {
    "id": 1,
    "param_key": "overtime_rate",
    "param_value": "2.0",
    "description": "更新后的工作日加班费率",
    "updated_at": "2023-05-20T20:00:00"
  }
  ```

### 9.3 获取操作日志

- **接口**: `GET /system/logs`
- **描述**: 获取系统操作日志
- **权限**: 管理员
- **查询参数**:
  - `start_time`: 开始时间 (ISO格式)
  - `end_time`: 结束时间 (ISO格式)
  - `user_id`: 按用户筛选 (可选)
  - `operation_type`: 按操作类型筛选 (可选)
  - `skip`: 跳过记录数 (默认: 0)
  - `limit`: 返回记录数 (默认: 100)
- **响应**:
  ```json
  [
    {
      "id": 5001,
      "user": {
        "id": 1,
        "username": "admin"
      },
      "operation_type": "登录",
      "operation_content": "用户登录系统",
      "ip_address": "192.168.1.100",
      "operation_time": "2023-05-20T09:30:00"
    },
    // ...
  ]
  ```

### 9.4 系统备份

- **接口**: `POST /system/backup`
- **描述**: 创建系统数据备份
- **权限**: 管理员
- **响应**:
  ```json
  {
    "success": true,
    "backup_file": "backup_20230520210000.sql",
    "size": "2.5MB",
    "created_at": "2023-05-20T21:00:00"
  }
  ```

### 9.5 系统恢复

- **接口**: `POST /system/restore`
- **描述**: 从备份恢复系统数据
- **权限**: 管理员
- **请求体**:
  ```json
  {
    "backup_file": "backup_20230520210000.sql"
  }
  ```
- **响应**:
  ```json
  {
    "success": true,
    "message": "系统数据恢复成功"
  }
  ```

### 9.6 获取系统统计数据

- **接口**: `GET /system/statistics`
- **描述**: 获取系统统计数据
- **权限**: 管理员或HR
- **响应**:
  ```json
  {
    "employee_count": 56,
    "department_count": 5,
    "active_user_count": 60,
    "this_month_salary_total": 680000.00,
    "last_month_salary_total": 650000.00
  }
  ``` 