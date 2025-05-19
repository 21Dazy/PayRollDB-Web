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

## 启动服务

开发模式启动：

```bash
uvicorn main:app --reload
```

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