import { defineStore } from 'pinia';
import { ref } from 'vue';
import { get, post, put, del } from '@/utils/request';

interface SystemParameter {
  id: number;
  param_key: string;
  param_value: string;
  description?: string;
  created_at: string;
  updated_at?: string;
  [key: string]: any;
}

interface SystemParameterCreateUpdate {
  param_key: string;
  param_value: string;
  description?: string;
}

interface OperationLog {
  id: number;
  user_id: number;
  operation_type: string;
  operation_detail: string;
  ip_address?: string;
  created_at: string;
  user?: any;
  [key: string]: any;
}

interface QueryParams {
  skip?: number;
  limit?: number;
  user_id?: number;
  operation_type?: string;
  start_date?: string;
  end_date?: string;
}

export const useSystemStore = defineStore('system', () => {
  const systemParameters = ref<SystemParameter[]>([]);
  const currentParameter = ref<SystemParameter | null>(null);
  const operationLogs = ref<OperationLog[]>([]);
  const totalCount = ref<number>(0);
  const isLoading = ref<boolean>(false);
  const error = ref<string | null>(null);

  // 获取系统参数列表
  async function getSystemParameters(params: {skip?: number, limit?: number} = {}) {
    isLoading.value = true;
    error.value = null;
    try {
      const response = await get('/api/v1/system/parameters', { params });
      systemParameters.value = response;
      totalCount.value = response.length;
      return response;
    } catch (err: any) {
      error.value = err.message || '获取系统参数列表失败';
      throw err;
    } finally {
      isLoading.value = false;
    }
  }

  // 获取单个系统参数
  async function getSystemParameter(id: number) {
    isLoading.value = true;
    error.value = null;
    try {
      const response = await get(`/api/v1/system/parameters/${id}`);
      currentParameter.value = response;
      return response;
    } catch (err: any) {
      error.value = err.message || '获取系统参数详情失败';
      throw err;
    } finally {
      isLoading.value = false;
    }
  }

  // 创建系统参数
  async function createSystemParameter(paramData: SystemParameterCreateUpdate) {
    isLoading.value = true;
    error.value = null;
    try {
      const response = await post('/api/v1/system/parameters', paramData);
      // 重新获取系统参数列表以更新状态
      await getSystemParameters();
      return response;
    } catch (err: any) {
      error.value = err.message || '创建系统参数失败';
      throw err;
    } finally {
      isLoading.value = false;
    }
  }

  // 更新系统参数
  async function updateSystemParameter(id: number, paramData: SystemParameterCreateUpdate) {
    isLoading.value = true;
    error.value = null;
    try {
      const response = await put(`/api/v1/system/parameters/${id}`, paramData);
      // 更新本地数据
      const index = systemParameters.value.findIndex(param => param.id === id);
      if (index !== -1) {
        systemParameters.value[index] = { ...systemParameters.value[index], ...response };
      }
      if (currentParameter.value && currentParameter.value.id === id) {
        currentParameter.value = { ...currentParameter.value, ...response };
      }
      return response;
    } catch (err: any) {
      error.value = err.message || '更新系统参数失败';
      throw err;
    } finally {
      isLoading.value = false;
    }
  }

  // 删除系统参数
  async function deleteSystemParameter(id: number) {
    isLoading.value = true;
    error.value = null;
    try {
      await del(`/api/v1/system/parameters/${id}`);
      // 从本地列表中移除
      systemParameters.value = systemParameters.value.filter(param => param.id !== id);
      if (currentParameter.value && currentParameter.value.id === id) {
        currentParameter.value = null;
      }
      return true;
    } catch (err: any) {
      error.value = err.message || '删除系统参数失败';
      throw err;
    } finally {
      isLoading.value = false;
    }
  }

  // 获取操作日志列表
  async function getOperationLogs(params: QueryParams = {}) {
    isLoading.value = true;
    error.value = null;
    try {
      const response = await get('/api/v1/system/logs', { params });
      operationLogs.value = response;
      totalCount.value = response.length;
      return response;
    } catch (err: any) {
      error.value = err.message || '获取操作日志列表失败';
      throw err;
    } finally {
      isLoading.value = false;
    }
  }

  // 获取系统状态
  async function getSystemStatus() {
    isLoading.value = true;
    error.value = null;
    try {
      const response = await get('/api/v1/system/status');
      return response;
    } catch (err: any) {
      error.value = err.message || '获取系统状态失败';
      throw err;
    } finally {
      isLoading.value = false;
    }
  }

  // 获取系统概览数据 (Dashboard用)
  async function getSystemOverview() {
    isLoading.value = true;
    error.value = null;
    try {
      // 调用后端API获取系统概览数据
      const response = await get('/api/v1/system/overview');
      return response;
    } catch (err: any) {
      error.value = err.message || '获取系统概览数据失败';
      console.error('获取系统概览数据失败:', err);
      throw err;
    } finally {
      isLoading.value = false;
    }
  }

  // 系统健康检查（无需认证）
  async function checkSystemHealth() {
    try {
      // 直接使用axios避免token验证
      const response = await get('/api/v1/system/health');
      return {
        isOnline: true,
        data: response
      };
    } catch (err: any) {
      console.error('系统健康检查失败:', err);
      return {
        isOnline: false,
        error: err.message || '系统不可用'
      };
    }
  }

  return {
    systemParameters,
    currentParameter,
    operationLogs,
    totalCount,
    isLoading,
    error,
    getSystemParameters,
    getSystemParameter,
    createSystemParameter,
    updateSystemParameter,
    deleteSystemParameter,
    getOperationLogs,
    getSystemStatus,
    getSystemOverview,
    checkSystemHealth
  };
}); 