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
          }
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
        ]
      },
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
