# 用户注册API使用说明

## 概述

本文档描述了工资管理系统的用户注册功能API接口。用户可以通过这些接口进行自助注册并绑定员工信息。

## API接口列表

### 1. 员工信息验证

**接口地址：** `POST /api/v1/registration/verify-employee`

**功能：** 验证员工信息是否存在且可以绑定

**请求参数：**
```json
{
  "real_name": "张三",
  "id_card": "110101199001011234",  // 身份证号（可选）
  "employee_id": 1                 // 员工工号（可选）
}
```

**响应示例：**
```json
{
  "found": true,
  "employee_id": 1,
  "employee_name": "张三",
  "department_name": "研发部",
  "position_name": "软件工程师",
  "message": "员工信息验证成功，可以进行注册"
}
```

### 2. 发送验证码

**接口地址：** `POST /api/v1/registration/send-verification-code`

**功能：** 向指定手机号发送验证码

**请求参数：**
```json
{
  "phone": "13800138000"
}
```

**响应示例：**
```json
{
  "message": "验证码已发送",
  "debug_code": "123456"  // 开发环境下返回验证码
}
```

### 3. 用户注册

**接口地址：** `POST /api/v1/registration/register`

**功能：** 提交用户注册申请

**请求参数：**
```json
{
  "username": "testuser001",
  "password": "password123",
  "real_name": "张三",
  "id_card": "110101199001011234",
  "phone": "13800138000",
  "email": "test@example.com",
  "employee_id": 1,
  "verification_code": "123456"
}
```

**响应示例：**
```json
{
  "id": 1,
  "username": "testuser001",
  "real_name": "张三",
  "phone": "13800138000",
  "email": "test@example.com",
  "status": "pending",
  "employee_id": 1,
  "created_at": "2023-12-14T10:30:00",
  "message": "注册申请已提交，请等待管理员审核"
}
```

### 4. 查询注册状态

**接口地址：** `GET /api/v1/registration/my-registration`

**功能：** 查询注册申请的审核状态

**请求参数：**
```
?username=testuser001
```

**响应示例：**
```json
{
  "status": "pending",
  "message": "注册申请审核中，请耐心等待",
  "created_at": "2023-12-14T10:30:00",
  "admin_remarks": null
}
```

## 管理员接口

### 5. 获取注册申请列表

**接口地址：** `GET /api/v1/registration/registrations`

**权限要求：** 管理员

**请求参数：**
```
?skip=0&limit=100&status=pending
```

**响应示例：**
```json
[
  {
    "id": 1,
    "username": "testuser001",
    "real_name": "张三",
    "phone": "13800138000",
    "email": "test@example.com",
    "status": "pending",
    "employee_name": "张三",
    "department_name": "研发部",
    "position_name": "软件工程师",
    "created_at": "2023-12-14T10:30:00",
    "admin_remarks": null
  }
]
```

### 6. 审核注册申请

**接口地址：** `POST /api/v1/registration/registrations/{registration_id}/approve`

**权限要求：** 管理员

**请求参数：**
```json
{
  "action": "approve",  // "approve" 或 "reject"
  "remarks": "审核通过"
}
```

**响应示例：**
```json
{
  "message": "注册申请已通过",
  "status": "approved"
}
```

## 注册流程

1. **员工信息验证**
   - 用户提供真实姓名和身份证号/工号
   - 系统验证员工信息是否存在且未绑定

2. **发送验证码**
   - 向用户手机号发送6位数字验证码
   - 验证码有效期30分钟

3. **提交注册申请**
   - 用户填写完整注册信息
   - 验证手机验证码
   - 创建待审核的注册申请

4. **管理员审核**
   - 管理员查看注册申请列表
   - 验证用户身份信息
   - 通过或拒绝申请

5. **账号激活**
   - 审核通过后自动创建用户账号
   - 分配默认权限
   - 用户可以使用用户名密码登录

## 错误码说明

| 错误码 | 说明 |
|--------|------|
| 400 | 请求参数错误（如身份证格式不正确） |
| 409 | 用户名已存在或员工已绑定 |
| 404 | 资源不存在 |
| 403 | 权限不足 |
| 500 | 服务器内部错误 |

## 数据验证规则

### 用户名
- 长度：3-50个字符
- 格式：只能包含字母、数字、下划线和短横线
- 唯一性：系统内唯一

### 密码
- 长度：6-128个字符
- 安全性：建议包含大小写字母、数字和特殊字符

### 身份证号
- 格式：18位数字，最后一位可能是X
- 验证：包含校验位验证

### 手机号
- 格式：11位数字，以1开头
- 验证：符合中国大陆手机号格式

## 测试说明

1. **运行测试脚本**
   ```bash
   cd backend
   python test_user_registration.py
   ```

2. **前置条件**
   - 后端服务运行在 http://localhost:8000
   - 数据库已创建相关表结构
   - 至少有一个员工记录用于测试

3. **测试数据**
   - 测试用户名：testuser001
   - 测试手机号：13800138000
   - 测试身份证：110101199001011234

## 安全考虑

1. **验证码安全**
   - 验证码有过期时间
   - 限制发送频率
   - 使用后即失效

2. **密码安全**
   - 密码使用bcrypt加密存储
   - 不会在API响应中返回密码

3. **权限控制**
   - 管理员接口需要认证
   - 普通用户只能查询自己的申请

4. **数据脱敏**
   - 敏感信息在展示时进行脱敏处理
   - 身份证号、银行账号等部分隐藏

## 注意事项

1. **员工绑定**
   - 一个员工只能绑定一个用户账号
   - 离职员工无法注册新账号

2. **审核机制**
   - 所有注册申请都需要管理员审核
   - 可以配置自动审核规则

3. **日志记录**
   - 所有操作都会记录到操作日志
   - 便于审计和问题排查 