import { defineStore } from 'pinia';
import { ref } from 'vue';
import { get, post, put, del } from '@/utils/request';

interface Employee {
  id: number;
  name: string;
  department_id: number;
  position_id: number;
  base_salary: number;
  hire_date: string;
  phone: string;
  email?: string;
  address?: string;
  id_card: string;
  bank_name?: string;
  bank_account?: string;
  status: boolean;  // true为在职，false为离职
  created_at: string;
  updated_at?: string;
  department?: any;
  position?: any;
  [key: string]: any;
}

interface EmployeeCreateUpdate {
  name: string;
  department_id: number;
  position_id: number;
  base_salary: number;
  hire_date: string;
  phone: string;
  email?: string;
  address?: string;
  id_card: string;
  bank_name?: string;
  bank_account?: string;
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

  // 搜索员工
  async function searchEmployees(keyword: string, departmentId?: number) {
    isLoading.value = true;
    error.value = null;
    try {
      // 使用后端专门的搜索接口
      const queryParams = new URLSearchParams();
      
      if (keyword) {
        queryParams.append('keyword', keyword);
      }
      
      if (departmentId) {
        queryParams.append('department_id', departmentId.toString());
      }
      
      // 添加默认参数
      queryParams.append('skip', '0');
      queryParams.append('limit', '100');
      
      const url = `/api/v1/employees/search?${queryParams.toString()}`;
      console.log('搜索URL:', url);
      
      const response = await get(url);
      console.log('搜索结果原始数据:', response);
      
      // 确保返回的是数组
      if (!Array.isArray(response)) {
        console.error('搜索返回的不是数组:', response);
        return [];
      }
      
      // 确保每个员工对象都有必要的字段
      const processedResponse = response.map(emp => {
        // 确保employee_id字段存在
        if (!emp.employee_id) {
          emp.employee_id = String(emp.id);
        }
        
        // 确保department_name字段存在
        if (!emp.department_name && emp.department && typeof emp.department === 'object') {
          emp.department_name = emp.department.name || '';
        }
        
        // 确保position_name字段存在
        if (!emp.position_name && emp.position && typeof emp.position === 'object') {
          emp.position_name = emp.position.name || '';
        }
        
        return emp;
      });
      
      return processedResponse;
    } catch (err: any) {
      console.error('搜索员工失败:', err);
      error.value = err.message || '搜索员工失败';
      // 返回空数组避免页面错误
      return [];
    } finally {
      isLoading.value = false;
    }
  }

  // 获取单个员工
  async function getEmployee(id: number, forceRefresh: boolean = false) {
    isLoading.value = true;
    error.value = null;
    try {
      // 如果不需要强制刷新且当前已经有员工数据，则直接返回
      if (!forceRefresh && currentEmployee.value && currentEmployee.value.id === id) {
        return currentEmployee.value;
      }
      
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
      // 确保所有必要字段都已提供
      const requiredFields = [
        'name', 'department_id', 'position_id', 
        'phone', 'base_salary', 'hire_date', 'id_card'
      ];
      
      const missingFields = requiredFields.filter(field => {
        const value = employeeData[field as keyof EmployeeCreateUpdate];
        return value === undefined || value === null || value === '';
      });
      
      if (missingFields.length > 0) {
        throw new Error(`缺少必要字段: ${missingFields.join(', ')}`);
      }
      
      // 确保数值型字段为数值类型
      if (employeeData.base_salary !== undefined && typeof employeeData.base_salary !== 'number') {
        employeeData.base_salary = Number(employeeData.base_salary);
      }
      
      if (typeof employeeData.department_id !== 'number') {
        employeeData.department_id = Number(employeeData.department_id);
      }
      
      if (typeof employeeData.position_id !== 'number') {
        employeeData.position_id = Number(employeeData.position_id);
      }
      
      // 打印提交的数据
      console.log('创建员工: 提交数据', JSON.stringify(employeeData, null, 2));

      // 验证职位是否属于所选部门
      const validatePositionDepartment = async () => {
        const { department_id, position_id } = employeeData;
        try {
          // 获取职位详情
          const response = await get(`/api/v1/positions/${position_id}`);
          if (response && response.department_id !== department_id) {
            throw new Error(`所选职位不属于该部门，请重新选择`);
          }
          return true;
        } catch (err: any) {
          if (err.message.includes('所选职位不属于该部门')) {
            throw err;
          }
          // 如果是API错误，可能是因为职位接口问题，我们继续提交
          console.warn('验证职位部门关系时出错，将继续提交:', err);
          return true;
        }
      };

      // 执行验证
      await validatePositionDepartment();
      
      const response = await post('/api/v1/employees/', employeeData);
      console.log('创建员工: 成功响应', response);
      
      // 重新获取员工列表以更新状态
      await getEmployees();
      return response;
    } catch (err: any) {
      console.error('创建员工: 错误', err);
      if (err.response) {
        console.error('创建员工: 错误响应', {
          status: err.response.status,
          data: err.response.data
        });
        
        // 处理 422 错误
        if (err.response.status === 422) {
          const details = err.response.data.detail;
          if (Array.isArray(details)) {
            const validationErrors = details.map((detail: any) => 
              `${detail.loc.slice(1).join('.')}：${detail.msg}`
            ).join('; ');
            error.value = `数据验证失败: ${validationErrors}`;
          } else {
            error.value = `数据验证失败: ${JSON.stringify(err.response.data)}`;
          }
        } else {
          error.value = `创建员工失败: ${err.response.data.detail || err.message || '未知错误'}`;
        }
      } else {
        error.value = err.message || '创建员工失败';
      }
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
  async function getEmployeeSalaries(id: number, year?: number | null, month?: number | null) {
    isLoading.value = true;
    error.value = null;
    try {
      const params: any = {};
      if (year !== null && year !== undefined) params.year = year;
      if (month !== null && month !== undefined) params.month = month;
      
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
  async function exportEmployees(params: any = {}) {
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
    getEmployeeAttendance,
    importEmployees,
    exportEmployees,
    deleteEmployee,
    searchEmployees
  };
}); 