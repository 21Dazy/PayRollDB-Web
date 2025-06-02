import { defineStore } from 'pinia';
import { ref } from 'vue';
import { get, post, put, del } from '@/utils/request';

interface SocialSecurityConfig {
  id: number;
  name: string;
  pension_rate: number;
  medical_rate: number;
  unemployment_rate: number;
  injury_rate: number;
  maternity_rate: number;
  housing_fund_rate: number;
  is_default: boolean;
  created_at: string;
  updated_at?: string;
  [key: string]: any;
}

interface SocialSecurityConfigCreateUpdate {
  name: string;
  pension_rate: number;
  medical_rate: number;
  unemployment_rate: number;
  injury_rate: number;
  maternity_rate: number;
  housing_fund_rate: number;
  is_default?: boolean;
}

interface EmployeeSocialSecurity {
  id: number;
  employee_id: number;
  config_id: number;
  base_number: number;
  housing_fund_base: number;
  effective_date: string;
  created_at: string;
  updated_at?: string;
  employee?: any;
  config?: SocialSecurityConfig;
  [key: string]: any;
}

interface EmployeeSocialSecurityCreateUpdate {
  employee_id: number;
  config_id: number;
  base_number: number;
  housing_fund_base: number;
  effective_date: string;
}

interface QueryParams {
  skip?: number;
  limit?: number;
  employee_id?: number;
  keyword?: string;
}

export const useSocialSecurityStore = defineStore('socialSecurity', () => {
  const configs = ref<SocialSecurityConfig[]>([]);
  const currentConfig = ref<SocialSecurityConfig | null>(null);
  const employeeSocialSecurities = ref<EmployeeSocialSecurity[]>([]);
  const currentEmployeeSocialSecurity = ref<EmployeeSocialSecurity | null>(null);
  const totalCount = ref<number>(0);
  const isLoading = ref<boolean>(false);
  const error = ref<string | null>(null);

  // 获取社保配置列表
  async function getConfigs(params: QueryParams = {}) {
    isLoading.value = true;
    error.value = null;
    try {
      const response: any = await get('/api/v1/social-security/configs', { params });
      configs.value = response.items;
      totalCount.value = response.total;
      return response;
    } catch (err: any) {
      error.value = err.message || '获取社保配置列表失败';
      throw err;
    } finally {
      isLoading.value = false;
    }
  }

  // 获取单个社保配置
  async function getConfig(id: number) {
    isLoading.value = true;
    error.value = null;
    try {
      const response = await get(`/api/v1/social-security/configs/${id}`);
      currentConfig.value = response;
      return response;
    } catch (err: any) {
      error.value = err.message || '获取社保配置详情失败';
      throw err;
    } finally {
      isLoading.value = false;
    }
  }

  // 创建社保配置
  async function createConfig(configData: SocialSecurityConfigCreateUpdate) {
    isLoading.value = true;
    error.value = null;
    try {
      const response = await post('/api/v1/social-security/configs', configData);
      // 重新获取社保配置列表以更新状态
      await getConfigs();
      return response;
    } catch (err: any) {
      error.value = err.message || '创建社保配置失败';
      throw err;
    } finally {
      isLoading.value = false;
    }
  }

  // 更新社保配置
  async function updateConfig(id: number, configData: SocialSecurityConfigCreateUpdate) {
    isLoading.value = true;
    error.value = null;
    try {
      const response = await put(`/api/v1/social-security/configs/${id}`, configData);
      // 更新本地数据
      const index = configs.value.findIndex(config => config.id === id);
      if (index !== -1) {
        configs.value[index] = { ...configs.value[index], ...response };
      }
      if (currentConfig.value && currentConfig.value.id === id) {
        currentConfig.value = { ...currentConfig.value, ...response };
      }
      return response;
    } catch (err: any) {
      error.value = err.message || '更新社保配置失败';
      throw err;
    } finally {
      isLoading.value = false;
    }
  }

  // 删除社保配置
  async function deleteConfig(id: number) {
    isLoading.value = true;
    error.value = null;
    try {
      await del(`/api/v1/social-security/configs/${id}`);
      // 从本地列表中移除
      configs.value = configs.value.filter(config => config.id !== id);
      if (currentConfig.value && currentConfig.value.id === id) {
        currentConfig.value = null;
      }
      return true;
    } catch (err: any) {
      error.value = err.message || '删除社保配置失败';
      throw err;
    } finally {
      isLoading.value = false;
    }
  }

  // 获取员工社保列表
  async function getEmployeeSocialSecurities(params: QueryParams = {}) {
    isLoading.value = true;
    error.value = null;
    try {
      const response: any = await get('/api/v1/social-security/employee-configs', { params });
      employeeSocialSecurities.value = response.items;
      totalCount.value = response.total;
      return response;
    } catch (err: any) {
      error.value = err.message || '获取员工社保列表失败';
      throw err;
    } finally {
      isLoading.value = false;
    }
  }

  // 获取单个员工社保配置
  async function getEmployeeSocialSecurity(id: number) {
    isLoading.value = true;
    error.value = null;
    try {
      const response = await get(`/api/v1/social-security/employee-configs/${id}`);
      currentEmployeeSocialSecurity.value = response;
      return response;
    } catch (err: any) {
      error.value = err.message || '获取员工社保详情失败';
      throw err;
    } finally {
      isLoading.value = false;
    }
  }

  // 获取员工的社保配置
  async function getEmployeeSocialSecurityByEmployee(employeeId: number) {
    isLoading.value = true;
    error.value = null;
    try {
      const response = await get(`/api/v1/social-security/employee/${employeeId}`);
      currentEmployeeSocialSecurity.value = response;
      return response;
    } catch (err: any) {
      error.value = err.message || '获取员工社保详情失败';
      throw err;
    } finally {
      isLoading.value = false;
    }
  }

  // 创建员工社保配置
  async function createEmployeeSocialSecurity(data: EmployeeSocialSecurityCreateUpdate) {
    isLoading.value = true;
    error.value = null;
    try {
      const response = await post('/api/v1/social-security/employee-configs', data);
      // 重新获取员工社保列表以更新状态
      await getEmployeeSocialSecurities();
      return response;
    } catch (err: any) {
      error.value = err.message || '创建员工社保配置失败';
      throw err;
    } finally {
      isLoading.value = false;
    }
  }

  // 更新员工社保配置
  async function updateEmployeeSocialSecurity(id: number, data: EmployeeSocialSecurityCreateUpdate) {
    isLoading.value = true;
    error.value = null;
    try {
      const response = await put(`/api/v1/social-security/employee-configs/${id}`, data);
      // 更新本地数据
      const index = employeeSocialSecurities.value.findIndex(config => config.id === id);
      if (index !== -1) {
        employeeSocialSecurities.value[index] = { ...employeeSocialSecurities.value[index], ...response };
      }
      if (currentEmployeeSocialSecurity.value && currentEmployeeSocialSecurity.value.id === id) {
        currentEmployeeSocialSecurity.value = { ...currentEmployeeSocialSecurity.value, ...response };
      }
      return response;
    } catch (err: any) {
      error.value = err.message || '更新员工社保配置失败';
      throw err;
    } finally {
      isLoading.value = false;
    }
  }

  // 删除员工社保配置
  async function deleteEmployeeSocialSecurity(id: number) {
    isLoading.value = true;
    error.value = null;
    try {
      await del(`/api/v1/social-security/employee-configs/${id}`);
      // 从本地列表中移除
      employeeSocialSecurities.value = employeeSocialSecurities.value.filter(config => config.id !== id);
      if (currentEmployeeSocialSecurity.value && currentEmployeeSocialSecurity.value.id === id) {
        currentEmployeeSocialSecurity.value = null;
      }
      return true;
    } catch (err: any) {
      error.value = err.message || '删除员工社保配置失败';
      throw err;
    } finally {
      isLoading.value = false;
    }
  }

  // 批量设置员工社保
  async function batchSetEmployeeSocialSecurity(data: any) {
    isLoading.value = true;
    error.value = null;
    try {
      const response = await post('/api/v1/social-security/batch-set', data);
      // 重新获取员工社保列表以更新状态
      await getEmployeeSocialSecurities();
      return response;
    } catch (err: any) {
      error.value = err.message || '批量设置员工社保失败';
      throw err;
    } finally {
      isLoading.value = false;
    }
  }

  return {
    configs,
    currentConfig,
    employeeSocialSecurities,
    currentEmployeeSocialSecurity,
    totalCount,
    isLoading,
    error,
    getConfigs,
    getConfig,
    createConfig,
    updateConfig,
    deleteConfig,
    getEmployeeSocialSecurities,
    getEmployeeSocialSecurity,
    getEmployeeSocialSecurityByEmployee,
    createEmployeeSocialSecurity,
    updateEmployeeSocialSecurity,
    deleteEmployeeSocialSecurity,
    batchSetEmployeeSocialSecurity
  };
}); 