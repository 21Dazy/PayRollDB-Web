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
  status: boolean;  // true为在职，false为离职
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
  status?: boolean;
}

interface EmployeeLeaveRequest {
  leave_date: string;
}

interface QueryParams {
  skip?: number;
  limit?: number;
  name?: string;
  department_id?: number;
  position_id?: number;
  status?: boolean;
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
      const response = await get('/api/v1/employees/', { params });
      employees.value = response;
      totalCount.value = response.length;
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

  // 设置员工离职
  async function setEmployeeLeave(id: number, leaveData: EmployeeLeaveRequest) {
    isLoading.value = true;
    error.value = null;
    try {
      const response = await put(`/api/v1/employees/${id}/leave`, leaveData);
      // 更新本地数据
      const index = employees.value.findIndex(emp => emp.id === id);
      if (index !== -1) {
        employees.value[index] = { ...employees.value[index], ...response, status: false };
      }
      if (currentEmployee.value && currentEmployee.value.id === id) {
        currentEmployee.value = { ...currentEmployee.value, ...response, status: false };
      }
      return response;
    } catch (err: any) {
      error.value = err.message || '设置员工离职失败';
      throw err;
    } finally {
      isLoading.value = false;
    }
  }

  // 获取员工工资记录
  async function getEmployeeSalaries(id: number, year?: number, month?: number) {
    isLoading.value = true;
    error.value = null;
    try {
      const params: any = {};
      if (year) params.year = year;
      if (month) params.month = month;
      
      const response = await get(`/api/v1/employees/${id}/salaries`, { params });
      return response;
    } catch (err: any) {
      error.value = err.message || '获取员工工资记录失败';
      throw err;
    } finally {
      isLoading.value = false;
    }
  }

  // 获取员工考勤记录
  async function getEmployeeAttendance(id: number, startDate?: string, endDate?: string) {
    isLoading.value = true;
    error.value = null;
    try {
      const params: any = {};
      if (startDate) params.start_date = startDate;
      if (endDate) params.end_date = endDate;
      
      const response = await get(`/api/v1/employees/${id}/attendance`, { params });
      return response;
    } catch (err: any) {
      error.value = err.message || '获取员工考勤记录失败';
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
    setEmployeeLeave,
    getEmployeeSalaries,
    getEmployeeAttendance
  };
}); 