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
      // 这个接口实际上是一个自定义的接口，可能需要根据后端实际情况调整
      // 这里暂时使用模拟数据，因为后端可能没有这个接口
      // 实际项目中可以调用多个接口组合数据
      
      // 可以获取系统状态信息
      const status = await getSystemStatus();
      
      // 假设这是API的返回数据结构
      const mockData = {
        employee_count: status.total_employees || 0,
        total_salary: 850000,
        attendance_issues: 8,
        pending_approvals: 5,
        department_data: [
          { name: '研发部', value: 40 },
          { name: '市场部', value: 25 },
          { name: '销售部', value: 30 },
          { name: '行政部', value: 15 },
          { name: '财务部', value: 10 },
          { name: '人力资源部', value: 6 }
        ],
        salary_data: {
          months: ['1月', '2月', '3月', '4月', '5月', '6月'],
          basic: [320000, 320000, 320000, 320000, 320000, 320000],
          performance: [120000, 132000, 101000, 134000, 150000, 130000],
          bonus: [80000, 60000, 90000, 70000, 80000, 100000],
          allowance: [50000, 50000, 50000, 50000, 50000, 50000]
        }
      };
      
      return mockData;
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
    createSystemParameter,
    updateSystemParameter,
    deleteSystemParameter,
    getOperationLogs,
    getSystemStatus,
    getSystemOverview
  };
}); 