import { createRouter, createWebHistory } from 'vue-router'
import type { RouteRecordRaw } from 'vue-router'
import AppLayout from '@/components/layout/AppLayout.vue'
import { useAuthStore } from '@/stores/auth'

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
        meta: { title: '首页', requiresAuth: true, roles: ['admin', 'hr', 'manager', 'employee'] }
      },
      // 员工管理路由 - 管理员权限
      {
        path: 'employee',
        name: 'employee',
        redirect: '/employee/list',
        meta: { title: '员工管理', requiresAuth: true, roles: ['admin', 'hr', 'manager'] },
        children: [
          {
            path: 'list',
            name: 'employee-list',
            component: () => import('@/views/employee/EmployeeListView.vue'),
            meta: { title: '员工列表', requiresAuth: true, roles: ['admin', 'hr', 'manager'] }
          },
          {
            path: 'add',
            name: 'employee-add',
            component: () => import('@/views/employee/EmployeeAddView.vue'),
            meta: { title: '添加员工', requiresAuth: true, roles: ['admin', 'hr', 'manager'] }
          },
          {
            path: 'edit/:id',
            name: 'employee-edit',
            component: () => import('@/views/employee/EmployeeEditView.vue'),
            meta: { title: '编辑员工', requiresAuth: true, roles: ['admin', 'hr', 'manager'] }
          },
          {
            path: 'salary/:id',
            name: 'employee-salary',
            component: () => import('@/views/employee/EmployeeSalaryView.vue'),
            meta: { title: '工资明细', requiresAuth: true, roles: ['admin', 'hr', 'manager'] }
          },
          {
            path: 'view/:id',
            name: 'employee-view',
            component: () => import('@/views/employee/EmployeeSalaryView.vue'),
            meta: { title: '员工详情', requiresAuth: true, roles: ['admin', 'hr', 'manager'] }
          }
        ]
      },
      // 部门管理路由 - 高级管理员权限
      {
        path: 'department',
        name: 'department',
        redirect: '/department/list',
        meta: { title: '部门管理', requiresAuth: true, roles: ['admin', 'hr'] },
        children: [
          {
            path: 'list',
            name: 'department-list',
            component: () => import('@/views/department/DepartmentListView.vue'),
            meta: { title: '部门列表', requiresAuth: true, roles: ['admin', 'hr'] }
          },
          {
            path: 'add',
            name: 'department-add',
            component: () => import('@/views/department/DepartmentAddView.vue'),
            meta: { title: '添加部门', requiresAuth: true, roles: ['admin', 'hr'] }
          },
          {
            path: 'edit/:id',
            name: 'department-edit',
            component: () => import('@/views/department/DepartmentEditView.vue'),
            meta: { title: '编辑部门', requiresAuth: true, roles: ['admin', 'hr'] }
          },
          {
            path: 'view/:id',
            name: 'department-view',
            component: () => import('@/views/department/DepartmentViewView.vue'),
            meta: { title: '部门详情', requiresAuth: true, roles: ['admin', 'hr'] }
          }
        ]
      },
      // 职位管理路由 - 高级管理员权限
      {
        path: 'position',
        name: 'position',
        redirect: '/position/list',
        meta: { title: '职位管理', requiresAuth: true, roles: ['admin', 'hr'] },
        children: [
          {
            path: 'list',
            name: 'position-list',
            component: () => import('@/views/position/PositionListView.vue'),
            meta: { title: '职位列表', requiresAuth: true, roles: ['admin', 'hr'] }
          },
          {
            path: 'add',
            name: 'position-add',
            component: () => import('@/views/position/PositionAddView.vue'),
            meta: { title: '添加职位', requiresAuth: true, roles: ['admin', 'hr'] }
          },
          {
            path: 'edit/:id',
            name: 'position-edit',
            component: () => import('@/views/position/PositionEditView.vue'),
            meta: { title: '编辑职位', requiresAuth: true, roles: ['admin', 'hr'] }
          },
          {
            path: 'view/:id',
            name: 'position-view',
            component: () => import('@/views/position/PositionViewView.vue'),
            meta: { title: '职位详情', requiresAuth: true, roles: ['admin', 'hr'] }
          }
        ]
      },
      // 薪资管理路由 - 管理员权限
      {
        path: 'salary',
        name: 'salary',
        redirect: '/salary/list',
        meta: { title: '薪资管理', requiresAuth: true, roles: ['admin', 'hr', 'manager'] },
        children: [
          {
            path: 'list',
            name: 'salary-list',
            component: () => import('@/views/salary/SalaryListView.vue'),
            meta: { title: '薪资列表', requiresAuth: true, roles: ['admin', 'hr', 'manager'] }
          },
          {
            path: 'pay',
            name: 'salary-pay',
            component: () => import('@/views/salary/SalaryPayView.vue'),
            meta: { title: '薪资发放', requiresAuth: true, roles: ['admin', 'hr', 'manager'] }
          },
          {
            path: 'detail/:id',
            name: 'salary-detail',
            component: () => import('@/views/salary/SalaryDetailView.vue'),
            meta: { title: '薪资详情', requiresAuth: true, roles: ['admin', 'hr', 'manager'] }
          },
          {
            path: 'items',
            name: 'salary-items',
            component: () => import('@/views/salary/SalaryItemView.vue'),
            meta: { title: '薪资项目管理', requiresAuth: true, roles: ['admin', 'hr', 'manager'] }
          },
          {
            path: 'config',
            name: 'salary-config',
            component: () => import('@/views/salary/SalaryConfigView.vue'),
            meta: { title: '薪资配置', requiresAuth: true, roles: ['admin', 'hr', 'manager'] }
          }
        ]
      },
      // 考勤管理路由 - 管理员权限
      {
        path: 'attendance',
        name: 'attendance',
        redirect: '/attendance/record',
        meta: { title: '考勤管理', requiresAuth: true, roles: ['admin', 'hr', 'manager'] },
        children: [
          {
            path: 'record',
            name: 'attendance-record',
            component: () => import('@/views/attendance/AttendanceRecordView.vue'),
            meta: { title: '考勤记录', requiresAuth: true, roles: ['admin', 'hr', 'manager'] }
          },
          {
            path: 'statistics',
            name: 'attendance-statistics',
            component: () => import('@/views/attendance/AttendanceStatisticsView.vue'),
            meta: { title: '考勤统计', requiresAuth: true, roles: ['admin', 'hr', 'manager'] }
          }
        ]
      },
      // 报表统计路由 - 管理员权限
          {
        path: 'report',
        name: 'report',
        redirect: '/report/salary',
        meta: { title: '报表统计', requiresAuth: true, roles: ['admin', 'hr', 'manager'] },
        children: [
          {
            path: 'salary',
            name: 'report-salary',
            component: () => import('@/views/dashboard/DashboardView.vue'), // 临时使用dashboard组件
            meta: { title: '薪资报表', requiresAuth: true, roles: ['admin', 'hr', 'manager'] }
          },
          {
            path: 'attendance',
            name: 'report-attendance',
            component: () => import('@/views/dashboard/DashboardView.vue'), // 临时使用dashboard组件
            meta: { title: '考勤报表', requiresAuth: true, roles: ['admin', 'hr', 'manager'] }
          },
          {
            path: 'department',
            name: 'report-department',
            component: () => import('@/views/dashboard/DashboardView.vue'), // 临时使用dashboard组件
            meta: { title: '部门报表', requiresAuth: true, roles: ['admin', 'hr', 'manager'] }
          }
        ]
      },
      // 系统管理路由 - 超级管理员权限
      {
        path: 'system',
        name: 'system',
        redirect: '/system/user',
        meta: { title: '系统管理', requiresAuth: true, roles: ['admin'] },
        children: [
          {
            path: 'user',
            name: 'system-user',
            component: () => import('@/views/dashboard/DashboardView.vue'), // 临时使用dashboard组件
            meta: { title: '用户管理', requiresAuth: true, roles: ['admin'] }
          },
          {
            path: 'role',
            name: 'system-role',
            component: () => import('@/views/dashboard/DashboardView.vue'), // 临时使用dashboard组件
            meta: { title: '角色管理', requiresAuth: true, roles: ['admin'] }
          },
          {
            path: 'menu',
            name: 'system-menu',
            component: () => import('@/views/dashboard/DashboardView.vue'), // 临时使用dashboard组件
            meta: { title: '菜单管理', requiresAuth: true, roles: ['admin'] }
          },
          {
            path: 'param',
            name: 'system-param',
            component: () => import('@/views/dashboard/DashboardView.vue'), // 临时使用dashboard组件
            meta: { title: '参数设置', requiresAuth: true, roles: ['admin'] }
          },
          {
            path: 'log',
            name: 'system-log',
            component: () => import('@/views/dashboard/DashboardView.vue'), // 临时使用dashboard组件
            meta: { title: '操作日志', requiresAuth: true, roles: ['admin'] }
          }
        ]
      },
      // 用户个人中心路由 - 所有用户都可以访问
      {
        path: 'user',
        name: 'user',
        redirect: '/user/profile',
        meta: { title: '用户中心', requiresAuth: true, roles: ['admin', 'hr', 'manager', 'employee'] },
        children: [
          {
            path: 'profile',
            name: 'user-profile',
            component: () => import('@/views/user/UserProfileView.vue'),
            meta: { title: '个人信息', requiresAuth: true, roles: ['admin', 'hr', 'manager', 'employee'] }
          },
          {
            path: 'salary',
            name: 'user-salary',
            component: () => import('@/views/salary/UserSalaryView.vue'),
            meta: { title: '我的薪资', requiresAuth: true, roles: ['admin', 'hr', 'manager', 'employee'] }
          },
          {
            path: 'attendance',
            name: 'user-attendance',
            component: () => import('@/views/attendance/UserAttendanceView.vue'),
            meta: { title: '我的考勤', requiresAuth: true, roles: ['admin', 'hr', 'manager', 'employee'] }
          }
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

// 检查用户角色权限
function hasRolePermission(userRole: string, requiredRoles: string[]): boolean {
  return requiredRoles.includes(userRole)
}

// 全局前置守卫
router.beforeEach((to, from, next) => {
  // 添加调试日志
  console.log('路由跳转:', { from: from.path, to: to.path, requiresAuth: to.meta.requiresAuth, roles: to.meta.roles })
  
  // 设置页面标题
  document.title = `${to.meta.title} - 薪资管理系统` || '薪资管理系统'
  
  // 判断是否需要登录
  if (to.meta.requiresAuth) {
    // 检查是否有token
    const token = localStorage.getItem('token')
    if (!token) {
      // 未登录，跳转到登录页
      console.log('需要登录权限，但未检测到token，重定向到登录页')
      next({ name: 'login' })
      return
    }

    // 已登录，检查角色权限
    const authStore = useAuthStore()
    const userRole = authStore.user?.role
    
    if (!userRole) {
      console.log('用户角色信息缺失，重定向到登录页')
      next({ name: 'login' })
      return
    }

    // 检查路由是否需要特定角色权限
    const requiredRoles = to.meta.roles as string[]
    if (requiredRoles && requiredRoles.length > 0) {
      if (!hasRolePermission(userRole, requiredRoles)) {
        console.log(`用户角色 ${userRole} 没有权限访问 ${to.path}，需要角色: ${requiredRoles.join(', ')}`)
        // 根据用户角色重定向到合适的页面
        if (userRole === 'employee') {
          next({ name: 'user-profile' }) // 普通用户重定向到个人中心
    } else {
          next({ name: 'dashboard' }) // 其他角色重定向到首页
        }
        return
      }
    }

    // 权限检查通过，允许访问
    console.log(`用户角色 ${userRole} 有权限访问 ${to.path}`)
      next()
  } else {
    // 不需要登录，直接放行
    console.log('不需要登录权限，直接放行')
    next()
  }
})

export default router
