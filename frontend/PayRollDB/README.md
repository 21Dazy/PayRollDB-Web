# 薪资管理系统前端

## 项目简介

这是一个基于Vue 3 + TypeScript + Element Plus开发的薪资管理系统前端项目。

## 技术栈

- Vue 3.5.x (使用Composition API + `<script setup>` 语法)
- TypeScript
- Vite 构建工具
- Element Plus UI组件库
- Pinia 状态管理
- Vue Router 路由管理
- Axios HTTP客户端
- SCSS 样式预处理器
- Mock.js 模拟数据

## 项目结构

```
src/
├── assets/         # 静态资源
├── components/     # 组件
│   ├── common/     # 通用组件
│   └── layout/     # 布局组件
├── composables/    # 组合式函数
├── router/         # 路由配置
├── stores/         # Pinia状态管理
├── styles/         # 全局样式
├── utils/          # 工具函数
├── views/          # 页面组件
│   ├── auth/       # 认证相关页面
│   ├── admin/      # 管理员页面
│   ├── employee/   # 员工页面
│   ├── dashboard/  # 仪表盘页面
│   ├── salary/     # 薪资相关页面
│   ├── attendance/ # 考勤相关页面
│   ├── user/       # 用户中心页面
│   └── shared/     # 共享页面
└── main.ts         # 入口文件
```

## 开发环境

- Node.js >= 18.x
- npm >= 9.x

## 安装依赖

```bash
npm install
```

## 开发

```bash
npm run dev
```

## 构建

```bash
npm run build
```

## 预览构建结果

```bash
npm run preview
```

## 类型检查

```bash
npm run type-check
```

## 功能特性

### 用户注册与登录

系统支持用户自助注册功能：
1. 普通用户可以通过注册页面进行账号注册
2. 注册时需要验证员工信息（姓名、身份证号等）
3. 验证通过后直接创建用户账号，无需管理员审批

### 薪资管理

系统支持全面的薪资管理功能：
1. 薪资组成项目配置
2. 薪资发放记录管理
3. 薪资明细查看
4. 个人薪资查询

### 考勤管理

系统提供考勤管理功能：
1. 考勤记录录入
2. 考勤统计查询
3. 个人考勤查看

## 接口约定

本项目使用统一的接口返回格式：

```typescript
{
  code: number,      // 状态码，200表示成功
  message: string,   // 提示信息
  data: any          // 返回数据
}
```

## 与后端集成

本项目设计用于与FastAPI后端集成。在开发阶段使用Mock.js模拟API数据，生产环境连接实际API。

- 开发环境API基础路径: `/api`
- 生产环境API基础路径: 通过环境变量`VITE_API_BASE_URL`配置

### 后端数据库结构

后端使用MySQL数据库，主要脚本位于`database/scripts`目录：

#### 基础数据库脚本
- `database_design.sql` - 基础数据库设计脚本
- `database_designV2.sql` - 升级版数据库设计脚本
- `consolidated_database_schema.sql` - 整合数据库脚本

#### 功能增强脚本
- `user_self_service_enhancement.sql` - 用户自助服务功能增强脚本
- `employee_salary_config.sql` - 员工薪资配置表创建脚本

#### 数据更新脚本
- `update_salary_components.sql` - 薪资组成项目更新脚本
- `migrate_salary_data.sql` - 薪资数据迁移脚本

## 权限控制

系统支持多种用户角色:

- 员工: 只能查看自己的相关信息
- 管理员: 可以管理所有数据
- HR: 可以管理员工和薪资信息
- 部门经理: 可以查看和管理部门员工信息

路由导航守卫会根据用户角色控制页面访问权限。
