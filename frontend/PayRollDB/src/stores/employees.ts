import { defineStore } from 'pinia';
import { ref } from 'vue';
import { get, post, put, del } from '@/utils/request';

interface Employee {
  id: number;
  name: string;
  gender: string;
  id_card: string;
  phone: string;
  address?: string;
  entry_date: string;
  departure_date?: string | null;
  department_id: number;
  position_id: number;
  bank_name?: string;
  bank_account?: string;
  basic_salary: number;
  status: string;
  created_at: string;
  updated_at?: string;
  department?: any;
  position?: any;
  [key: string]: any;
}

interface EmployeeCreateUpdate {
  name: string;
  gender: string;
  id_card: string;
  phone: string;
  address?: string;
  entry_date: string;
  departure_date?: string | null;
  department_id: number;
  position_id: number;
  bank_name?: string;
  bank_account?: string;
  basic_salary: number;
  status?: string;
}

interface QueryParams {
  skip?: number;
  limit?: number;
  keyword?: string;
  department_id?: number;
  position_id?: number;
  status?: string;
}

export const useEmployeesStore = defineStore('employees', () => {
  const employees = ref<Employee[]>([]);
  const currentEmployee = ref<Employee | null>(null);
  const totalCount = ref<number>(0);
  const isLoading = ref<boolean>(false);
  const error = ref<string | null>(null);

  // 获取员工列表
  async function getEmployees(params: QueryParams = {}) {
    isLoading.value = true;
    error.value = null;
    try {
      const response: any = await get('/api/v1/employees/', { params });
      employees.value = response.items;
      totalCount.value = response.total;
      return response;
    } catch (err: any) {
      error.value = err.message || '获取员工列表失败';
      throw err;
    } finally {
      isLoading.value = false;
    }
  }

  // 获取单个员工
  async function getEmployee(id: number) {
    isLoading.value = true;
    error.value = null;
    try {
      const response = await get(`/api/v1/employees/${id}`);
      currentEmployee.value = response;
      return response;
    } catch (err: any) {
      error.value = err.message || '获取员工详情失败';
      throw err;
    } finally {
      isLoading.value = false;
    }
  }

  // 创建员工
  async function createEmployee(employeeData: EmployeeCreateUpdate) {
    isLoading.value = true;
    error.value = null;
    try {
      const response = await post('/api/v1/employees/', employeeData);
      // 重新获取员工列表以更新状态
      await getEmployees();
      return response;
    } catch (err: any) {
      error.value = err.message || '创建员工失败';
      throw err;
    } finally {
      isLoading.value = false;
    }
  }

  // 更新员工
  async function updateEmployee(id: number, employeeData: EmployeeCreateUpdate) {
    isLoading.value = true;
    error.value = null;
    try {
      const response = await put(`/api/v1/employees/${id}`, employeeData);
      // 更新本地数据
      const index = employees.value.findIndex(emp => emp.id === id);
      if (index !== -1) {
        employees.value[index] = { ...employees.value[index], ...response };
      }
      if (currentEmployee.value && currentEmployee.value.id === id) {
        currentEmployee.value = { ...currentEmployee.value, ...response };
      }
      return response;
    } catch (err: any) {
      error.value = err.message || '更新员工失败';
      throw err;
    } finally {
      isLoading.value = false;
    }
  }

  // 删除员工
  async function deleteEmployee(id: number) {
    isLoading.value = true;
    error.value = null;
    try {
      await del(`/api/v1/employees/${id}`);
      // 从本地列表中移除
      employees.value = employees.value.filter(emp => emp.id !== id);
      if (currentEmployee.value && currentEmployee.value.id === id) {
        currentEmployee.value = null;
      }
      return true;
    } catch (err: any) {
      error.value = err.message || '删除员工失败';
      throw err;
    } finally {
      isLoading.value = false;
    }
  }

  // 获取部门下的所有员工
  async function getEmployeesByDepartment(departmentId: number) {
    return getEmployees({ department_id: departmentId });
  }

  // 导入员工数据
  async function importEmployees(file: File) {
    isLoading.value = true;
    error.value = null;
    try {
      const formData = new FormData();
      formData.append('file', file);
      
      const response = await post('/api/v1/employees/import', formData, {
        headers: {
          'Content-Type': 'multipart/form-data'
        }
      });
      // 重新获取员工列表以更新状态
      await getEmployees();
      return response;
    } catch (err: any) {
      error.value = err.message || '导入员工数据失败';
      throw err;
    } finally {
      isLoading.value = false;
    }
  }

  // 导出员工数据
  async function exportEmployees(params: QueryParams = {}) {
    isLoading.value = true;
    error.value = null;
    try {
      const response = await get('/api/v1/employees/export', { 
        params,
        responseType: 'blob'
      });
      return response;
    } catch (err: any) {
      error.value = err.message || '导出员工数据失败';
      throw err;
    } finally {
      isLoading.value = false;
    }
  }

  return {
    employees,
    currentEmployee,
    totalCount,
    isLoading,
    error,
    getEmployees,
    getEmployee,
    createEmployee,
    updateEmployee,
    deleteEmployee,
    getEmployeesByDepartment,
    importEmployees,
    exportEmployees
  };
}); 