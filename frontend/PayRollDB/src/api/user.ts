import { get, post, put, del } from '@/utils/request'

// 用户个人信息API

/**
 * 获取用户个人档案信息
 */
export function getUserProfile() {
  return get('/api/v1/user/profile/profile')
}

/**
 * 获取用户个人仪表板统计信息
 */
export function getUserDashboardStats() {
  return get('/api/v1/user/profile/dashboard')
}

/**
 * 获取用户权限列表
 */
export function getUserPermissions() {
  return get('/api/v1/user/profile/permissions')
}

/**
 * 获取用户活动日志
 */
export function getUserActivityLogs(params?: {
  skip?: number
  limit?: number
  action_type?: string
}) {
  return get('/api/v1/user/profile/activity-logs', { params })
}

/**
 * 获取用户设置
 */
export function getUserSettings() {
  return get('/api/v1/user/profile/settings')
}

/**
 * 创建用户设置
 */
export function createUserSetting(data: {
  setting_key: string
  setting_value: string
  description?: string
}) {
  return post('/api/v1/user/profile/settings', data)
}

/**
 * 更新用户设置
 */
export function updateUserSetting(setting_key: string, data: {
  setting_value: string
  description?: string
}) {
  return put(`/api/v1/user/profile/settings/${setting_key}`, data)
}

/**
 * 删除用户设置
 */
export function deleteUserSetting(setting_key: string) {
  return del(`/api/v1/user/profile/settings/${setting_key}`)
} 