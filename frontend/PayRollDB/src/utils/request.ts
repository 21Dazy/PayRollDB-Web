import axios from 'axios'
import type { AxiosInstance, InternalAxiosRequestConfig, AxiosResponse } from 'axios'
import { ElMessage } from 'element-plus'
import router from '@/router'

// 获取环境变量中的API基础URL
const baseURL = ''

// 是否正在尝试重新登录
let isRefreshing = false
// 等待重新登录完成的请求队列
let requestsQueue: Array<{ 
  config: InternalAxiosRequestConfig; 
  resolve: (value: any) => void; 
  reject: (reason?: any) => void 
}> = []

// 创建axios实例
const service: AxiosInstance = axios.create({
  baseURL, // url = base url + request url
  timeout: 15000, // 请求超时时间
  withCredentials: true, // 跨域请求时发送Cookie
})

// 检查token是否即将过期
function isTokenExpired(): boolean {
  try {
    const token = localStorage.getItem('token')
    if (!token) return true
    
    // 从JWT token中提取过期时间
    const base64Url = token.split('.')[1]
    const base64 = base64Url.replace(/-/g, '+').replace(/_/g, '/')
    const jsonPayload = decodeURIComponent(atob(base64).split('').map(c => {
      return '%' + ('00' + c.charCodeAt(0).toString(16)).slice(-2)
    }).join(''))
    
    const { exp } = JSON.parse(jsonPayload)
    const expirationTime = exp * 1000 // 转换为毫秒
    
    // 如果剩余时间小于5分钟，视为即将过期
    return Date.now() > expirationTime - 5 * 60 * 1000
  } catch (error) {
    console.error('解析token出错:', error)
    return true // 出错时认为已过期
  }
}

// 处理未授权错误
function handleUnauthorized(message: string = '未授权，请重新登录') {
  // 尝试自动重新登录
  if (!isRefreshing) {
    isRefreshing = true
    
    // 动态导入auth store以避免循环依赖
    import('@/stores/auth').then(({ useAuthStore }) => {
      const authStore = useAuthStore()
      
      // 尝试自动重新登录
      authStore.autoRelogin().then(success => {
        isRefreshing = false
        
        if (success) {
          // 重新登录成功，重试所有等待的请求
          requestsQueue.forEach(({ config, resolve }) => {
            // 确保重新获取token
            if (config.headers) {
              const newToken = localStorage.getItem('token')
              config.headers.Authorization = `Bearer ${newToken}`
            }
            
            // 重新发送请求
            service(config).then(resolve).catch(err => {
              // 如果重试还是失败，则不再尝试
              handleFinalError(err)
            })
          })
          
          // 清空队列
          requestsQueue = []
          
          // 提示用户已自动重新登录
          ElMessage({
            message: '已自动重新登录',
            type: 'success',
            duration: 2000
          })
        } else {
          // 重新登录失败，清除凭据并跳转到登录页
          handleFinalError({ message })
          
          // 拒绝所有等待的请求
          requestsQueue.forEach(({ reject }) => {
            reject(new Error('自动登录失败'))
          })
          
          // 清空队列
          requestsQueue = []
        }
      }).catch(() => {
        isRefreshing = false
        handleFinalError({ message })
        
        // 拒绝所有等待的请求
        requestsQueue.forEach(({ reject }) => {
          reject(new Error('自动登录失败'))
        })
        
        // 清空队列
        requestsQueue = []
      })
    })
  }
}

// 最终处理错误（当自动重新登录也失败时）
function handleFinalError(error: any) {
  const message = error.message || '未授权，请重新登录'
  
  // 清除token和用户信息
  localStorage.removeItem('token')
  localStorage.removeItem('user')
  
  // 显示提示消息
  ElMessage({
    message,
    type: 'warning',
    duration: 3000
  })
  
  // 如果当前不在登录页，则跳转到登录页
  if (router.currentRoute.value.path !== '/login') {
    router.push('/login')
  }
}

// 请求拦截器
service.interceptors.request.use(
  (config: InternalAxiosRequestConfig) => {
    // 在发送请求之前做些什么
    const token = localStorage.getItem('token')
    
    // 检查token是否存在且未过期
    if (token) {
      if (isTokenExpired() && !config.url?.includes('/auth/login')) {
        // token即将过期，且不是登录请求
        return new Promise((resolve, reject) => {
          // 将请求加入队列
          requestsQueue.push({ config, resolve, reject })
          
          // 触发自动重新登录
          handleUnauthorized('登录已过期，正在尝试自动重新登录')
        })
      }
      
      if (config.headers) {
        // 让每个请求携带token
        config.headers.Authorization = `Bearer ${token}`
      }
    }
    
    return config
  },
  (error) => {
    // 处理请求错误
    console.error(error)
    return Promise.reject(error)
  }
)

// 响应拦截器
service.interceptors.response.use(
  (response: AxiosResponse) => {
    // FastAPI 直接返回数据，不需要额外处理
    return response.data;
  },
  (error) => {
    console.error('请求错误', error)
    
    // 处理网络错误
    let message = '请求失败'
    if (error.response) {
      // 记录错误状态码以便调试
      console.log(`响应错误状态码: ${error.response.status}`)
      console.log('响应错误数据:', error.response.data)
      
      // 提取错误消息
      if (error.response.data && error.response.data.detail) {
        message = error.response.data.detail;
      }
      
      const status = error.response.status
      // 401错误特殊处理 - 尝试自动重新登录
      if (status === 401 && !error.config.url.includes('/auth/login')) {
        // 将原始请求配置存储起来
        const originalRequest = error.config
        
        return new Promise((resolve, reject) => {
          // 将请求加入队列
          requestsQueue.push({ 
            config: originalRequest, 
            resolve, 
            reject 
          })
          
          // 触发自动重新登录
          handleUnauthorized(message || '未授权，正在尝试自动重新登录')
        })
      } else {
        switch (status) {
          case 400:
            message = '请求错误'
            break
          case 403:
            message = '拒绝访问'
            break
          case 404:
            message = '请求地址出错'
            break
          case 408:
            message = '请求超时'
            break
          case 500:
            message = '服务器内部错误'
            break
          case 501:
            message = '服务未实现'
            break
          case 502:
            message = '网关错误'
            break
          case 503:
            message = '服务不可用'
            break
          case 504:
            message = '网关超时'
            break
          case 505:
            message = 'HTTP版本不受支持'
            break
          default:
            message = `请求失败(${status})`
        }
        
        // 非401错误时显示错误消息
        ElMessage({
          message,
          type: 'error',
          duration: 5 * 1000,
        })
      }
    } else if (error.request) {
      message = '服务器未响应'
      ElMessage({
        message,
        type: 'error',
        duration: 5 * 1000,
      })
    } else {
      message = error.message
      // 过滤掉因token过期主动拒绝的请求错误提示
      if (message !== 'Token expired') {
        ElMessage({
          message,
          type: 'error',
          duration: 5 * 1000,
        })
      }
    }
    
    return Promise.reject(error)
  }
)

// 封装GET请求
export const get = <T = any>(url: string, params?: any, config?: InternalAxiosRequestConfig): Promise<T> => {
  // 打印请求参数
  console.log('GET请求参数:', params);
  
  // 如果params是对象且包含params属性，说明是嵌套的，需要解构
  if (params && typeof params === 'object' && 'params' in params) {
    console.log('检测到嵌套params，正在解构');
    params = params.params;
  }
  
  return service.get(url, { params, ...config })
}

// 封装POST请求
export const post = <T = any>(url: string, data?: any, config?: any): Promise<T> => {
  return service.post(url, data, config)
}

// 封装PUT请求
export const put = <T = any>(url: string, data?: any, config?: any): Promise<T> => {
  return service.put(url, data, config)
}

// 封装DELETE请求
export const del = <T = any>(url: string, config?: InternalAxiosRequestConfig): Promise<T> => {
  return service.delete(url, config)
}

export default service 