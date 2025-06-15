import { defineStore } from 'pinia';
import { ref } from 'vue';
import { get, post, put, del } from '@/utils/request';

// 薪资项目类型定义
export interface SalaryItem {
  id: number;
  name: string;
  type: 'addition' | 'deduction';
  is_percentage: boolean;
  is_system: boolean;
  created_at?: string;
  updated_at?: string;
}

export const useSalaryItemsStore = defineStore('salaryItems', () => {
  // 状态
  const salaryItems = ref<SalaryItem[]>([]);
  const isLoading = ref(false);
  const error = ref<string | null>(null);

  // 获取薪资项目列表
  async function getSalaryItems(type?: string) {
    isLoading.value = true;
    error.value = null;
    
    try {
      const params = type ? { type } : {};
      const response = await get('/api/v1/salaries/items', { params });
      
      if (Array.isArray(response)) {
        salaryItems.value = response;
      } else {
        console.error('无效的薪资项目数据格式:', response);
        salaryItems.value = [];
      }
      
      return salaryItems.value;
    } catch (err: any) {
      console.error('获取薪资项目失败:', err);
      error.value = err.message || '获取薪资项目失败';
      throw err;
    } finally {
      isLoading.value = false;
    }
  }

  // 创建薪资项目
  async function createSalaryItem(itemData: Partial<SalaryItem>) {
    isLoading.value = true;
    error.value = null;
    
    try {
      const response = await post('/api/v1/salaries/items', itemData);
      
      // 更新本地状态
      salaryItems.value.push(response);
      
      return response;
    } catch (err: any) {
      console.error('创建薪资项目失败:', err);
      error.value = err.message || '创建薪资项目失败';
      throw err;
    } finally {
      isLoading.value = false;
    }
  }

  // 更新薪资项目
  async function updateSalaryItem(id: number, itemData: Partial<SalaryItem>) {
    isLoading.value = true;
    error.value = null;
    
    try {
      const response = await put(`/api/v1/salaries/items/${id}`, itemData);
      
      // 更新本地状态
      const index = salaryItems.value.findIndex(item => item.id === id);
      if (index !== -1) {
        salaryItems.value[index] = { ...salaryItems.value[index], ...response };
      }
      
      return response;
    } catch (err: any) {
      console.error('更新薪资项目失败:', err);
      error.value = err.message || '更新薪资项目失败';
      throw err;
    } finally {
      isLoading.value = false;
    }
  }

  // 删除薪资项目
  async function deleteSalaryItem(id: number) {
    isLoading.value = true;
    error.value = null;
    
    try {
      await del(`/api/v1/salaries/items/${id}`);
      
      // 更新本地状态
      salaryItems.value = salaryItems.value.filter(item => item.id !== id);
      
      return true;
    } catch (err: any) {
      console.error('删除薪资项目失败:', err);
      error.value = err.message || '删除薪资项目失败';
      throw err;
    } finally {
      isLoading.value = false;
    }
  }

  return {
    salaryItems,
    isLoading,
    error,
    getSalaryItems,
    createSalaryItem,
    updateSalaryItem,
    deleteSalaryItem
  };
}); 