import { defineStore } from 'pinia';
import { ref } from 'vue';
import { get, post, put, del } from '@/utils/request';

interface Attendance {
  id: number;
  employee_id: number;
  date: string;
  status_id: number;
  work_hours?: number;
  overtime_hours?: number;
  remarks?: string;
  created_at: string;
  updated_at?: string;
  employee?: any;
  status?: any;
  [key: string]: any;
}

interface AttendanceStatus {
  id: number;
  name: string;
  description?: string;
  is_deduction: boolean;
  deduction_value: number;
  created_at: string;
  updated_at?: string;
}

interface AttendanceCreateUpdate {
  employee_id: number;
  date: string;
  status_id: number;
  overtime_hours?: number;
  remarks?: string;
}

interface QueryParams {
  skip?: number;
  limit?: number;
  employee_id?: number;
  department_id?: number;
  start_date?: string;
  end_date?: string;
  status_id?: number;
}

export const useAttendanceStore = defineStore('attendance', () => {
  const attendances = ref<Attendance[]>([]);
  const currentAttendance = ref<Attendance | null>(null);
  const attendanceStatuses = ref<AttendanceStatus[]>([]);
  const totalCount = ref<number>(0);
  const isLoading = ref<boolean>(false);
  const error = ref<string | null>(null);

  // 获取考勤列表
  async function getAttendances(params: QueryParams = {}) {
    isLoading.value = true;
    error.value = null;
    try {
      const response: any = await get('/api/v1/attendance/', { params });
      attendances.value = response.items || response;
      totalCount.value = response.total || response.length;
      return response;
    } catch (err: any) {
      error.value = err.message || '获取考勤列表失败';
      throw err;
    } finally {
      isLoading.value = false;
    }
  }

  // 获取单个考勤记录
  async function getAttendance(id: number) {
    isLoading.value = true;
    error.value = null;
    try {
      const response = await get(`/api/v1/attendance/${id}`);
      currentAttendance.value = response;
      return response;
    } catch (err: any) {
      error.value = err.message || '获取考勤详情失败';
      throw err;
    } finally {
      isLoading.value = false;
    }
  }

  // 创建考勤记录
  async function createAttendance(attendanceData: AttendanceCreateUpdate) {
    isLoading.value = true;
    error.value = null;
    try {
      const response = await post('/api/v1/attendance/', attendanceData);
      // 重新获取考勤列表以更新状态
      await getAttendances();
      return response;
    } catch (err: any) {
      error.value = err.message || '创建考勤记录失败';
      throw err;
    } finally {
      isLoading.value = false;
    }
  }

  // 更新考勤记录
  async function updateAttendance(id: number, attendanceData: AttendanceCreateUpdate) {
    isLoading.value = true;
    error.value = null;
    try {
      const response = await put(`/api/v1/attendance/${id}`, attendanceData);
      // 更新本地数据
      const index = attendances.value.findIndex(att => att.id === id);
      if (index !== -1) {
        attendances.value[index] = { ...attendances.value[index], ...response };
      }
      if (currentAttendance.value && currentAttendance.value.id === id) {
        currentAttendance.value = { ...currentAttendance.value, ...response };
      }
      return response;
    } catch (err: any) {
      error.value = err.message || '更新考勤记录失败';
      throw err;
    } finally {
      isLoading.value = false;
    }
  }

  // 删除考勤记录
  async function deleteAttendance(id: number) {
    isLoading.value = true;
    error.value = null;
    try {
      await del(`/api/v1/attendance/${id}`);
      // 从本地列表中移除
      attendances.value = attendances.value.filter(att => att.id !== id);
      if (currentAttendance.value && currentAttendance.value.id === id) {
        currentAttendance.value = null;
      }
      return true;
    } catch (err: any) {
      error.value = err.message || '删除考勤记录失败';
      throw err;
    } finally {
      isLoading.value = false;
    }
  }

  // 获取员工考勤记录
  async function getEmployeeAttendances(employeeId: number, params: Omit<QueryParams, 'employee_id'> = {}) {
    return getAttendances({ ...params, employee_id: employeeId });
  }

  // 获取考勤状态列表
  async function getAttendanceStatuses() {
    isLoading.value = true;
    error.value = null;
    try {
      const response = await get('/api/v1/attendance/status');
      attendanceStatuses.value = response;
      return response;
    } catch (err: any) {
      error.value = err.message || '获取考勤状态列表失败';
      throw err;
    } finally {
      isLoading.value = false;
    }
  }

  // 批量导入考勤记录
  async function importAttendances(file: File) {
    isLoading.value = true;
    error.value = null;
    try {
      const formData = new FormData();
      formData.append('file', file);
      
      const response = await post('/api/v1/attendance/import', formData);
      // 重新获取考勤列表以更新状态
      await getAttendances();
      return response;
    } catch (err: any) {
      error.value = err.message || '导入考勤记录失败';
      throw err;
    } finally {
      isLoading.value = false;
    }
  }

  // 导出考勤记录
  async function exportAttendances(params: QueryParams = {}) {
    isLoading.value = true;
    error.value = null;
    try {
      const response = await get('/api/v1/attendance/export', { 
        params,
        responseType: 'blob'
      });
      return response;
    } catch (err: any) {
      error.value = err.message || '导出考勤记录失败';
      throw err;
    } finally {
      isLoading.value = false;
    }
  }

  return {
    attendances,
    currentAttendance,
    attendanceStatuses,
    totalCount,
    isLoading,
    error,
    getAttendances,
    getAttendance,
    createAttendance,
    updateAttendance,
    deleteAttendance,
    getEmployeeAttendances,
    getAttendanceStatuses,
    importAttendances,
    exportAttendances
  };
}); 