import { defineStore } from 'pinia';
import { ref } from 'vue';
import { get, post, put } from '@/utils/request';

// 员工薪资配置项类型定义
export interface SalaryConfigItem {
  item_id: number;
  value: number;
  base_item?: string | null;
  effective_date: string;
}

// 员工薪资项目类型定义（用于展示）
export interface EmployeeSalaryItem {
  id: number;
  item_id: number;
  item_name: string;
  type: 'addition' | 'deduction';
  is_percentage: boolean;
  value: number;
  base_item?: string | null;
  is_system: boolean;
}

// 员工薪资配置类型定义
export interface EmployeeSalaryConfig {
  employee_id: number;
  items: EmployeeSalaryItem[];
}

// 员工薪资配置保存请求类型
export interface EmployeeSalaryConfigSaveRequest {
  employee_id: number;
  items: SalaryConfigItem[];
}

export const useSalaryConfigStore = defineStore('salaryConfig', () => {
  // 状态
  const currentConfig = ref<EmployeeSalaryConfig | null>(null);
  const isLoading = ref(false);
  const error = ref<string | null>(null);

  // 获取员工薪资配置
  async function getEmployeeSalaryConfig(employeeId: number) {
    isLoading.value = true;
    error.value = null;
    
    try {
      const response = await get(`/api/v1/salaries/config/${employeeId}`);
      
      // 处理响应数据
      const config: EmployeeSalaryConfig = {
        employee_id: employeeId,
        items: response.items || []
      };
      
      currentConfig.value = config;
      return config;
    } catch (err: any) {
      console.error('获取员工薪资配置失败:', err);
      error.value = err.message || '获取员工薪资配置失败';
      
      // 如果没有配置，返回空配置
      const emptyConfig: EmployeeSalaryConfig = {
        employee_id: employeeId,
        items: []
      };
      
      currentConfig.value = emptyConfig;
      return emptyConfig;
    } finally {
      isLoading.value = false;
    }
  }

  // 保存员工薪资配置
  async function saveEmployeeSalaryConfig(employeeId: number, config: EmployeeSalaryConfigSaveRequest) {
    isLoading.value = true;
    error.value = null;
    
    try {
      const response = await put(`/api/v1/salaries/config/${employeeId}`, config);
      
      currentConfig.value = response;
      return response;
    } catch (err: any) {
      console.error('保存员工薪资配置失败:', err);
      error.value = err.message || '保存员工薪资配置失败';
      throw err;
    } finally {
      isLoading.value = false;
    }
  }

  // 批量生成薪资记录
  async function generateSalaryRecords(year: number, month: number, departmentId?: number) {
    isLoading.value = true;
    error.value = null;
    
    try {
      const params = {
        year,
        month,
        department_id: departmentId
      };
      
      const response = await post('/api/v1/salaries/generate', params);
      return response;
    } catch (err: any) {
      console.error('生成薪资记录失败:', err);
      error.value = err.message || '生成薪资记录失败';
      throw err;
    } finally {
      isLoading.value = false;
    }
  }

  return {
    currentConfig,
    isLoading,
    error,
    getEmployeeSalaryConfig,
    saveEmployeeSalaryConfig,
    generateSalaryRecords
  };
}); 