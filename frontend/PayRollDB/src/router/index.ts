import { createRouter, createWebHistory } from 'vue-router'
import type { RouteRecordRaw } from 'vue-router'
import AppLayout from '@/components/layout/AppLayout.vue'

// 路由配置
const routes: RouteRecordRaw[] = [
  {
    path: '/login',
    name: 'login',
    component: () => import('@/views/auth/LoginView.vue'),
    meta: { title: '登录', requiresAuth: false }
  },
  {
    path: '/register',
    name: 'register',
    component: () => import('@/views/auth/RegisterView.vue'),
    meta: { title: '注册', requiresAuth: false }
  },
  {
    path: '/',
    component: AppLayout,
    redirect: '/dashboard',
    children: [
      {
        path: 'dashboard',
        name: 'dashboard',
        component: () => import('@/views/dashboard/DashboardView.vue'),
        meta: { title: '首页', requiresAuth: true }
      },
      // 员工管理路由
      {
        path: 'employee',
        name: 'employee',
        redirect: '/employee/list',
        meta: { title: '员工管理', requiresAuth: true },
        children: [
          {
            path: 'list',
            name: 'employee-list',
            component: () => import('@/views/employee/EmployeeListView.vue'),
            meta: { title: '员工列表', requiresAuth: true }
          },
          {
            path: 'add',
            name: 'employee-add',
            component: () => import('@/views/employee/EmployeeAddView.vue'),
            meta: { title: '添加员工', requiresAuth: true }
          },
          {
            path: 'edit/:id',
            name: 'employee-edit',
            component: () => import('@/views/employee/EmployeeEditView.vue'),
            meta: { title: '编辑员工', requiresAuth: true }
          },
          {
            path: 'salary/:id',
            name: 'employee-salary',
            component: () => import('@/views/employee/EmployeeSalaryView.vue'),
            meta: { title: '工资明细', requiresAuth: true }
          },
          {
            path: 'view/:id',
            name: 'employee-view',
            component: () => import('@/views/employee/EmployeeSalaryView.vue'),
            meta: { title: '员工详情', requiresAuth: true }
          }
          // 以下路由组件尚未实现
          /*
          {
            path: 'view/:id',
            name: 'employee-view',
            component: () => import('@/views/employee/EmployeeViewView.vue'),
            meta: { title: '员工详情', requiresAuth: true }
          }
          */
        ]
      },
      // 部门管理路由
      {
        path: 'department',
        name: 'department',
        redirect: '/department/list',
        meta: { title: '部门管理', requiresAuth: true },
        children: [
          {
            path: 'list',
            name: 'department-list',
            component: () => import('@/views/department/DepartmentListView.vue'),
            meta: { title: '部门列表', requiresAuth: true }
          },
          {
            path: 'add',
            name: 'department-add',
            component: () => import('@/views/department/DepartmentAddView.vue'),
            meta: { title: '添加部门', requiresAuth: true }
          },
          {
            path: 'edit/:id',
            name: 'department-edit',
            component: () => import('@/views/department/DepartmentEditView.vue'),
            meta: { title: '编辑部门', requiresAuth: true }
          },
          {
            path: 'view/:id',
            name: 'department-view',
            component: () => import('@/views/department/DepartmentViewView.vue'),
            meta: { title: '部门详情', requiresAuth: true }
          }
        ]
      },
      // 职位管理路由
      {
        path: 'position',
        name: 'position',
        redirect: '/position/list',
        meta: { title: '职位管理', requiresAuth: true },
        children: [
          {
            path: 'list',
            name: 'position-list',
            component: () => import('@/views/position/PositionListView.vue'),
            meta: { title: '职位列表', requiresAuth: true }
          },
          {
            path: 'add',
            name: 'position-add',
            component: () => import('@/views/position/PositionAddView.vue'),
            meta: { title: '添加职位', requiresAuth: true }
          },
          {
            path: 'edit/:id',
            name: 'position-edit',
            component: () => import('@/views/position/PositionEditView.vue'),
            meta: { title: '编辑职位', requiresAuth: true }
          },
          {
            path: 'view/:id',
            name: 'position-view',
            component: () => import('@/views/position/PositionViewView.vue'),
            meta: { title: '职位详情', requiresAuth: true }
          }
        ]
      },
      // 薪资管理路由
      {
        path: 'salary',
        name: 'salary',
        redirect: '/salary/list',
        meta: { title: '薪资管理', requiresAuth: true },
        children: [
          {
            path: 'list',
            name: 'salary-list',
            component: () => import('@/views/salary/SalaryListView.vue'),
            meta: { title: '薪资列表', requiresAuth: true }
          },
          {
            path: 'pay',
            name: 'salary-pay',
            component: () => import('@/views/salary/SalaryPayView.vue'),
            meta: { title: '薪资发放', requiresAuth: true }
          },
          // 已实现的薪资详情页面
          {
            path: 'detail/:id',
            name: 'salary-detail',
            component: () => import('@/views/salary/SalaryDetailView.vue'),
            meta: { title: '薪资详情', requiresAuth: true }
          },
          // 薪资项目管理
          {
            path: 'items',
            name: 'salary-items',
            component: () => import('@/views/salary/SalaryItemView.vue'),
            meta: { title: '薪资项目管理', requiresAuth: true }
          },
          // 薪资配置
          {
            path: 'config',
            name: 'salary-config',
            component: () => import('@/views/salary/SalaryConfigView.vue'),
            meta: { title: '薪资配置', requiresAuth: true }
          }
          // 其他未实现路由
          /*
          {
            path: 'employee/:id',
            name: 'salary-employee',
            component: () => import('@/views/salary/SalaryEmployeeView.vue'),
            meta: { title: '员工薪资', requiresAuth: true }
          }
          */
        ]
      },
      // 考勤管理路由
      {
        path: 'attendance',
        name: 'attendance',
        redirect: '/attendance/record',
        meta: { title: '考勤管理', requiresAuth: true },
        children: [
          {
            path: 'record',
            name: 'attendance-record',
            component: () => import('@/views/attendance/AttendanceRecordView.vue'),
            meta: { title: '考勤记录', requiresAuth: true }
          },
          {
            path: 'statistics',
            name: 'attendance-statistics',
            component: () => import('@/views/attendance/AttendanceStatisticsView.vue'),
            meta: { title: '考勤统计', requiresAuth: true }
          }
          // 以下路由组件尚未实现
          /*
          {
            path: 'employee/:id',
            name: 'attendance-employee',
            component: () => import('@/views/attendance/AttendanceEmployeeView.vue'),
            meta: { title: '员工考勤', requiresAuth: true }
          }
          */
        ]
      },
      // 系统管理路由 - 暂时注释，等待相关组件实现
      /*
      {
        path: 'system',
        name: 'system',
        redirect: '/system/user',
        meta: { title: '系统管理', requiresAuth: true },
        children: [
          {
            path: 'user',
            name: 'system-user',
            component: () => import('@/views/system/SystemUserView.vue'),
            meta: { title: '用户管理', requiresAuth: true }
          },
          {
            path: 'role',
            name: 'system-role',
            component: () => import('@/views/system/SystemRoleView.vue'),
            meta: { title: '角色管理', requiresAuth: true }
          },
          {
            path: 'permission',
            name: 'system-permission',
            component: () => import('@/views/system/SystemPermissionView.vue'),
            meta: { title: '权限管理', requiresAuth: true }
          },
          {
            path: 'settings',
            name: 'system-settings',
            component: () => import('@/views/system/SystemSettingsView.vue'),
            meta: { title: '系统设置', requiresAuth: true }
          }
        ]
      },
      */
      // 用户信息路由
      {
        path: 'user',
        name: 'user',
        redirect: '/user/profile',
        meta: { title: '用户中心', requiresAuth: true },
        children: [
          {
            path: 'profile',
            name: 'user-profile',
            component: () => import('@/views/user/UserProfileView.vue'),
            meta: { title: '个人信息', requiresAuth: true }
          }
          // 以下路由组件尚未实现
          /*
          {
            path: 'password',
            name: 'user-password',
            component: () => import('@/views/user/UserPasswordView.vue'),
            meta: { title: '修改密码', requiresAuth: true }
          }
          */
        ]
      }
    ]
  },
  // 404页面
  {
    path: '/:pathMatch(.*)*',
    name: 'not-found',
    component: () => import('@/views/NotFoundView.vue'),
    meta: { title: '404', requiresAuth: false }
  }
]

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes
})

// 全局前置守卫
router.beforeEach((to, from, next) => {
  // 设置页面标题
  document.title = `${to.meta.title} - 薪资管理系统` || '薪资管理系统'
  
  // 判断是否需要登录
  if (to.meta.requiresAuth) {
    // 检查是否有token
    const token = localStorage.getItem('token')
    if (!token) {
      // 未登录，跳转到登录页
      next({ name: 'login' })
    } else {
      // 已登录，放行
      next()
    }
  } else {
    // 不需要登录，直接放行
    next()
  }
})

export default router
