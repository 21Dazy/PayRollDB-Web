# 工资管理系统后端

本项目是工资管理系统的后端API服务，基于FastAPI框架开发。

## 项目结构

```
backend/
│
├── app/                    # 应用主目录
│   ├── api/                # API相关代码
│   │   ├── api_v1/         # API v1版本
│   │   │   ├── endpoints/  # API端点
│   │   │   └── api.py      # API路由注册
│   │   └── deps.py         # API依赖项
│   │
│   ├── core/               # 核心功能
│   │   ├── config.py       # 配置
│   │   └── security.py     # 安全相关
│   │
│   ├── crud/               # CRUD操作
│   │
│   ├── db/                 # 数据库相关
│   │   ├── base.py         # 导入所有模型
│   │   ├── base_class.py   # 基础模型类
│   │   └── session.py      # 数据库会话
│   │
│   ├── models/             # 数据库模型
│   │
│   ├── schemas/            # Pydantic模式
│   │
│   └── utils/              # 工具函数
│
├── .env                    # 环境变量配置
├── .env.example            # 环境变量示例
├── main.py                 # 应用入口
└── requirements.txt        # 依赖项
```

## 安装

1. 克隆项目代码
2. 创建并激活虚拟环境
3. 安装依赖项：

```bash
pip install -r requirements.txt
```

4. 复制`.env.example`为`.env`并配置环境变量
5. 创建数据库并初始化

## 数据库初始化

项目使用MySQL数据库，在启动前需要初始化数据库。

### 1. 创建数据库

首先确保MySQL服务已启动，然后创建数据库：

```sql
CREATE DATABASE salary_management_system CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

### 2. 初始化表结构和基础数据

运行创建表和初始化基础数据的脚本：

```bash
python create_tables.py
```

这将创建所有必要的表结构，并初始化基础数据，包括：
- 考勤状态
- 工资项目
- 默认社保配置
- 系统参数

### 3. 创建管理员用户

运行创建管理员用户的脚本：

```bash
python init_admin.py
```

这将创建：
- 管理部门
- 系统管理员职位
- 管理员员工
- 管理员用户

默认的管理员用户名和密码为：
- 用户名：`admin`
- 密码：`admin123`

## 启动应用

初始化完成后，启动应用：

```bash
uvicorn main:app --reload
```

或者直接运行：

```bash
python main.py
```

然后访问：http://localhost:8000/docs 查看API文档并进行测试。

## API测试

1. 打开Swagger UI：http://localhost:8000/docs
2. 使用`/api/v1/auth/login`接口登录获取令牌
   - 用户名：`admin`
   - 密码：`admin123`
3. 点击Authorize按钮，输入获取的令牌
4. 现在可以测试所有需要认证的API了

## API文档

启动服务后可访问以下地址查看API文档：

- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## 数据库迁移

本项目使用Alembic进行数据库迁移管理。

初始化迁移：

```bash
alembic init alembic
```

创建迁移脚本：

```bash
alembic revision --autogenerate -m "描述"
```

应用迁移：

```bash
alembic upgrade head
``` 