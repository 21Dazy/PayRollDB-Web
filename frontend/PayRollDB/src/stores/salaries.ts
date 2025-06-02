import { defineStore } from 'pinia';
import { ref } from 'vue';
import { get, post, put, del } from '@/utils/request';

interface SalaryItem {
  id: number;
  name: string;
  code: string;
  type: string; // 加项、减项
  is_social_security: boolean;
  is_tax: boolean;
  description?: string;
  created_at: string;
  updated_at?: string;
  [key: string]: any;
}

interface SalaryItemCreateUpdate {
  name: string;
  code: string;
  type: string;
  is_social_security: boolean;
  is_tax: boolean;
  description?: string;
}

interface SalaryRecord {
  id: number;
  employee_id: number;
  year: number;
  month: number;
  basic_salary: number;
  attendance_deduction: number;
  before_tax: number;
  tax: number;
  after_tax: number;
  social_security_personal: number;
  social_security_company: number;
  housing_fund_personal: number;
  housing_fund_company: number;
  status: string;
  created_at: string;
  updated_at?: string;
  employee?: any;
  details?: SalaryDetail[];
  [key: string]: any;
}

interface SalaryDetail {
  id: number;
  salary_record_id: number;
  salary_item_id: number;
  amount: number;
  created_at: string;
  updated_at?: string;
  salary_item?: SalaryItem;
  [key: string]: any;
}

interface SalaryRecordCreateUpdate {
  employee_id: number;
  year: number;
  month: number;
  details: Array<{
    salary_item_id: number;
    amount: number;
  }>;
}

interface QueryParams {
  skip?: number;
  limit?: number;
  employee_id?: number;
  department_id?: number;
  year?: number;
  month?: number;
  status?: string;
  keyword?: string;
}

export const useSalariesStore = defineStore('salaries', () => {
  const salaryItems = ref<SalaryItem[]>([]);
  const currentSalaryItem = ref<SalaryItem | null>(null);
  const salaryRecords = ref<SalaryRecord[]>([]);
  const currentSalaryRecord = ref<SalaryRecord | null>(null);
  const totalCount = ref<number>(0);
  const isLoading = ref<boolean>(false);
  const error = ref<string | null>(null);

  // 获取工资项目列表
  async function getSalaryItems(params: Omit<QueryParams, 'employee_id' | 'department_id' | 'year' | 'month'> = {}) {
    isLoading.value = true;
    error.value = null;
    try {
      const response: any = await get('/api/v1/salaries/items', { params });
      salaryItems.value = response.items;
      totalCount.value = response.total;
      return response;
    } catch (err: any) {
      error.value = err.message || '获取工资项目列表失败';
      throw err;
    } finally {
      isLoading.value = false;
    }
  }

  // 获取单个工资项目
  async function getSalaryItem(id: number) {
    isLoading.value = true;
    error.value = null;
    try {
      const response = await get(`/api/v1/salaries/items/${id}`);
      currentSalaryItem.value = response;
      return response;
    } catch (err: any) {
      error.value = err.message || '获取工资项目详情失败';
      throw err;
    } finally {
      isLoading.value = false;
    }
  }

  // 创建工资项目
  async function createSalaryItem(itemData: SalaryItemCreateUpdate) {
    isLoading.value = true;
    error.value = null;
    try {
      const response = await post('/api/v1/salaries/items', itemData);
      // 重新获取工资项目列表以更新状态
      await getSalaryItems();
      return response;
    } catch (err: any) {
      error.value = err.message || '创建工资项目失败';
      throw err;
    } finally {
      isLoading.value = false;
    }
  }

  // 更新工资项目
  async function updateSalaryItem(id: number, itemData: SalaryItemCreateUpdate) {
    isLoading.value = true;
    error.value = null;
    try {
      const response = await put(`/api/v1/salaries/items/${id}`, itemData);
      // 更新本地数据
      const index = salaryItems.value.findIndex(item => item.id === id);
      if (index !== -1) {
        salaryItems.value[index] = { ...salaryItems.value[index], ...response };
      }
      if (currentSalaryItem.value && currentSalaryItem.value.id === id) {
        currentSalaryItem.value = { ...currentSalaryItem.value, ...response };
      }
      return response;
    } catch (err: any) {
      error.value = err.message || '更新工资项目失败';
      throw err;
    } finally {
      isLoading.value = false;
    }
  }

  // 删除工资项目
  async function deleteSalaryItem(id: number) {
    isLoading.value = true;
    error.value = null;
    try {
      await del(`/api/v1/salaries/items/${id}`);
      // 从本地列表中移除
      salaryItems.value = salaryItems.value.filter(item => item.id !== id);
      if (currentSalaryItem.value && currentSalaryItem.value.id === id) {
        currentSalaryItem.value = null;
      }
      return true;
    } catch (err: any) {
      error.value = err.message || '删除工资项目失败';
      throw err;
    } finally {
      isLoading.value = false;
    }
  }

  // 获取工资记录列表
  async function getSalaryRecords(params: QueryParams = {}) {
    isLoading.value = true;
    error.value = null;
    try {
      const response: any = await get('/api/v1/salaries/records', { params });
      salaryRecords.value = response.items;
      totalCount.value = response.total;
      return response;
    } catch (err: any) {
      error.value = err.message || '获取工资记录列表失败';
      throw err;
    } finally {
      isLoading.value = false;
    }
  }

  // 获取单个工资记录
  async function getSalaryRecord(id: number) {
    isLoading.value = true;
    error.value = null;
    try {
      const response = await get(`/api/v1/salaries/records/${id}`);
      currentSalaryRecord.value = response;
      return response;
    } catch (err: any) {
      error.value = err.message || '获取工资记录详情失败';
      throw err;
    } finally {
      isLoading.value = false;
    }
  }

  // 创建工资记录
  async function createSalaryRecord(recordData: SalaryRecordCreateUpdate) {
    isLoading.value = true;
    error.value = null;
    try {
      const response = await post('/api/v1/salaries/records', recordData);
      // 重新获取工资记录列表以更新状态
      await getSalaryRecords({ year: recordData.year, month: recordData.month });
      return response;
    } catch (err: any) {
      error.value = err.message || '创建工资记录失败';
      throw err;
    } finally {
      isLoading.value = false;
    }
  }

  // 更新工资记录
  async function updateSalaryRecord(id: number, recordData: Partial<SalaryRecordCreateUpdate>) {
    isLoading.value = true;
    error.value = null;
    try {
      const response = await put(`/api/v1/salaries/records/${id}`, recordData);
      // 更新本地数据
      const index = salaryRecords.value.findIndex(record => record.id === id);
      if (index !== -1) {
        salaryRecords.value[index] = { ...salaryRecords.value[index], ...response };
      }
      if (currentSalaryRecord.value && currentSalaryRecord.value.id === id) {
        currentSalaryRecord.value = { ...currentSalaryRecord.value, ...response };
      }
      return response;
    } catch (err: any) {
      error.value = err.message || '更新工资记录失败';
      throw err;
    } finally {
      isLoading.value = false;
    }
  }

  // 删除工资记录
  async function deleteSalaryRecord(id: number) {
    isLoading.value = true;
    error.value = null;
    try {
      await del(`/api/v1/salaries/records/${id}`);
      // 从本地列表中移除
      salaryRecords.value = salaryRecords.value.filter(record => record.id !== id);
      if (currentSalaryRecord.value && currentSalaryRecord.value.id === id) {
        currentSalaryRecord.value = null;
      }
      return true;
    } catch (err: any) {
      error.value = err.message || '删除工资记录失败';
      throw err;
    } finally {
      isLoading.value = false;
    }
  }

  // 生成工资单
  async function generateSalaryRecords(year: number, month: number, departmentId?: number) {
    isLoading.value = true;
    error.value = null;
    try {
      const params: any = { year, month };
      if (departmentId) {
        params.department_id = departmentId;
      }
      const response = await post('/api/v1/salaries/generate', params);
      // 重新获取工资记录列表以更新状态
      await getSalaryRecords({ year, month });
      return response;
    } catch (err: any) {
      error.value = err.message || '生成工资单失败';
      throw err;
    } finally {
      isLoading.value = false;
    }
  }

  // 批量审核工资单
  async function approveSalaryRecords(ids: number[]) {
    isLoading.value = true;
    error.value = null;
    try {
      const response = await post('/api/v1/salaries/approve', { ids });
      // 更新本地数据
      for (const id of ids) {
        const index = salaryRecords.value.findIndex(record => record.id === id);
        if (index !== -1) {
          salaryRecords.value[index].status = 'approved';
        }
      }
      return response;
    } catch (err: any) {
      error.value = err.message || '批量审核工资单失败';
      throw err;
    } finally {
      isLoading.value = false;
    }
  }

  // 发放工资
  async function paySalaryRecords(ids: number[]) {
    isLoading.value = true;
    error.value = null;
    try {
      const response = await post('/api/v1/salaries/pay', { ids });
      // 更新本地数据
      for (const id of ids) {
        const index = salaryRecords.value.findIndex(record => record.id === id);
        if (index !== -1) {
          salaryRecords.value[index].status = 'paid';
        }
      }
      return response;
    } catch (err: any) {
      error.value = err.message || '发放工资失败';
      throw err;
    } finally {
      isLoading.value = false;
    }
  }

  // 导出工资单
  async function exportSalaryRecords(params: QueryParams = {}) {
    isLoading.value = true;
    error.value = null;
    try {
      const response = await get('/api/v1/salaries/export', { 
        params,
        responseType: 'blob'
      });
      return response;
    } catch (err: any) {
      error.value = err.message || '导出工资单失败';
      throw err;
    } finally {
      isLoading.value = false;
    }
  }

  // 获取工资汇总报表
  async function getSalarySummary(year: number, month: number) {
    isLoading.value = true;
    error.value = null;
    try {
      const response = await get('/api/v1/salaries/summary', { 
        params: { year, month }
      });
      return response;
    } catch (err: any) {
      error.value = err.message || '获取工资汇总报表失败';
      throw err;
    } finally {
      isLoading.value = false;
    }
  }

  return {
    salaryItems,
    currentSalaryItem,
    salaryRecords,
    currentSalaryRecord,
    totalCount,
    isLoading,
    error,
    getSalaryItems,
    getSalaryItem,
    createSalaryItem,
    updateSalaryItem,
    deleteSalaryItem,
    getSalaryRecords,
    getSalaryRecord,
    createSalaryRecord,
    updateSalaryRecord,
    deleteSalaryRecord,
    generateSalaryRecords,
    approveSalaryRecords,
    paySalaryRecords,
    exportSalaryRecords,
    getSalarySummary
  };
}); 