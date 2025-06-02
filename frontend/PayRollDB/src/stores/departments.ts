import { defineStore } from 'pinia';
import { ref } from 'vue';
import { get, post, put, del } from '@/utils/request';

interface Department {
  id: number;
  name: string;
  description?: string;
  created_at: string;
  updated_at?: string;
  [key: string]: any;
}

interface DepartmentWithCount extends Department {
  employee_count: number;
}

interface DepartmentCreateUpdate {
  name: string;
  description?: string;
}

interface QueryParams {
  skip?: number;
  limit?: number;
}

export const useDepartmentsStore = defineStore('departments', () => {
  const departments = ref<Department[]>([]);
  const departmentsWithCount = ref<DepartmentWithCount[]>([]);
  const currentDepartment = ref<Department | null>(null);
  const totalCount = ref<number>(0);
  const isLoading = ref<boolean>(false);
  const error = ref<string | null>(null);

  // 获取部门列表
  async function getDepartments(params: QueryParams = {}) {
    isLoading.value = true;
    error.value = null;
    try {
      const response = await get('/api/v1/departments/', { params });
      departments.value = response;
      totalCount.value = response.length;
      return response;
    } catch (err: any) {
      error.value = err.message || '获取部门列表失败';
      throw err;
    } finally {
      isLoading.value = false;
    }
  }

  // 获取部门列表(带员工数量)
  async function getDepartmentsWithEmployeeCount() {
    isLoading.value = true;
    error.value = null;
    try {
      const response = await get('/api/v1/departments/with-employee-count');
      departmentsWithCount.value = response;
      return response;
    } catch (err: any) {
      error.value = err.message || '获取部门和员工数量失败';
      throw err;
    } finally {
      isLoading.value = false;
    }
  }

  // 获取单个部门
  async function getDepartment(id: number) {
    isLoading.value = true;
    error.value = null;
    try {
      const response = await get(`/api/v1/departments/${id}`);
      currentDepartment.value = response;
      return response;
    } catch (err: any) {
      error.value = err.message || '获取部门详情失败';
      throw err;
    } finally {
      isLoading.value = false;
    }
  }

  // 创建部门
  async function createDepartment(departmentData: DepartmentCreateUpdate) {
    isLoading.value = true;
    error.value = null;
    try {
      const response = await post('/api/v1/departments/', departmentData);
      // 重新获取部门列表以更新状态
      await getDepartments();
      return response;
    } catch (err: any) {
      error.value = err.message || '创建部门失败';
      throw err;
    } finally {
      isLoading.value = false;
    }
  }

  // 更新部门
  async function updateDepartment(id: number, departmentData: DepartmentCreateUpdate) {
    isLoading.value = true;
    error.value = null;
    try {
      const response = await put(`/api/v1/departments/${id}`, departmentData);
      // 更新本地数据
      const index = departments.value.findIndex(dept => dept.id === id);
      if (index !== -1) {
        departments.value[index] = { ...departments.value[index], ...response };
      }
      if (currentDepartment.value && currentDepartment.value.id === id) {
        currentDepartment.value = { ...currentDepartment.value, ...response };
      }
      return response;
    } catch (err: any) {
      error.value = err.message || '更新部门失败';
      throw err;
    } finally {
      isLoading.value = false;
    }
  }

  // 删除部门
  async function deleteDepartment(id: number) {
    isLoading.value = true;
    error.value = null;
    try {
      await del(`/api/v1/departments/${id}`);
      // 从本地列表中移除
      departments.value = departments.value.filter(dept => dept.id !== id);
      if (currentDepartment.value && currentDepartment.value.id === id) {
        currentDepartment.value = null;
      }
      return true;
    } catch (err: any) {
      error.value = err.message || '删除部门失败';
      throw err;
    } finally {
      isLoading.value = false;
    }
  }

  return {
    departments,
    departmentsWithCount,
    currentDepartment,
    totalCount,
    isLoading,
    error,
    getDepartments,
    getDepartmentsWithEmployeeCount,
    getDepartment,
    createDepartment,
    updateDepartment,
    deleteDepartment
  };
}); 