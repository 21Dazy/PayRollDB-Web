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
  keyword?: string;
  start_date?: string;
  end_date?: string;
  operation_type?: string;
  user_id?: number;
}

export const useSystemStore = defineStore('system', () => {
  const systemParameters = ref<SystemParameter[]>([]);
  const currentParameter = ref<SystemParameter | null>(null);
  const operationLogs = ref<OperationLog[]>([]);
  const totalCount = ref<number>(0);
  const isLoading = ref<boolean>(false);
  const error = ref<string | null>(null);

  // 获取系统参数列表
  async function getSystemParameters(params: Omit<QueryParams, 'start_date' | 'end_date' | 'operation_type' | 'user_id'> = {}) {
    isLoading.value = true;
    error.value = null;
    try {
      const response: any = await get('/api/v1/system/parameters', { params });
      systemParameters.value = response.items;
      totalCount.value = response.total;
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

  // 根据参数键获取系统参数
  async function getSystemParameterByKey(key: string) {
    isLoading.value = true;
    error.value = null;
    try {
      const response = await get(`/api/v1/system/parameters/key/${key}`);
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
      const response: any = await get('/api/v1/system/logs', { params });
      operationLogs.value = response.items;
      totalCount.value = response.total;
      return response;
    } catch (err: any) {
      error.value = err.message || '获取操作日志列表失败';
      throw err;
    } finally {
      isLoading.value = false;
    }
  }

  // 获取数据库备份列表
  async function getDatabaseBackups() {
    isLoading.value = true;
    error.value = null;
    try {
      const response = await get('/api/v1/system/database/backups');
      return response;
    } catch (err: any) {
      error.value = err.message || '获取数据库备份列表失败';
      throw err;
    } finally {
      isLoading.value = false;
    }
  }

  // 创建数据库备份
  async function createDatabaseBackup() {
    isLoading.value = true;
    error.value = null;
    try {
      const response = await post('/api/v1/system/database/backup');
      return response;
    } catch (err: any) {
      error.value = err.message || '创建数据库备份失败';
      throw err;
    } finally {
      isLoading.value = false;
    }
  }

  // 恢复数据库
  async function restoreDatabaseBackup(fileName: string) {
    isLoading.value = true;
    error.value = null;
    try {
      const response = await post('/api/v1/system/database/restore', { file_name: fileName });
      return response;
    } catch (err: any) {
      error.value = err.message || '恢复数据库失败';
      throw err;
    } finally {
      isLoading.value = false;
    }
  }

  // 获取系统概览数据
  async function getSystemOverview() {
    isLoading.value = true;
    error.value = null;
    try {
      const response = await get('/api/v1/system/overview');
      return response;
    } catch (err: any) {
      error.value = err.message || '获取系统概览数据失败';
      throw err;
    } finally {
      isLoading.value = false;
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
    getSystemParameterByKey,
    createSystemParameter,
    updateSystemParameter,
    deleteSystemParameter,
    getOperationLogs,
    getDatabaseBackups,
    createDatabaseBackup,
    restoreDatabaseBackup,
    getSystemOverview
  };
}); 