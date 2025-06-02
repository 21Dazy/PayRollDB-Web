import { defineStore } from 'pinia';
import { ref } from 'vue';
import { get, post, put, del } from '@/utils/request';

interface Position {
  id: number;
  name: string;
  description?: string;
  department_id: number;
  salary_range_min?: number;
  salary_range_max?: number;
  created_at: string;
  updated_at?: string;
  department?: any;
  [key: string]: any;
}

interface PositionCreateUpdate {
  name: string;
  description?: string;
  department_id: number;
  salary_range_min?: number;
  salary_range_max?: number;
}

interface QueryParams {
  skip?: number;
  limit?: number;
  keyword?: string;
  department_id?: number;
}

export const usePositionsStore = defineStore('positions', () => {
  const positions = ref<Position[]>([]);
  const currentPosition = ref<Position | null>(null);
  const totalCount = ref<number>(0);
  const isLoading = ref<boolean>(false);
  const error = ref<string | null>(null);

  // 获取职位列表
  async function getPositions(params: QueryParams = {}) {
    isLoading.value = true;
    error.value = null;
    try {
      const response: any = await get('/api/v1/positions/', { params });
      positions.value = response.items;
      totalCount.value = response.total;
      return response;
    } catch (err: any) {
      error.value = err.message || '获取职位列表失败';
      throw err;
    } finally {
      isLoading.value = false;
    }
  }

  // 获取单个职位
  async function getPosition(id: number) {
    isLoading.value = true;
    error.value = null;
    try {
      const response = await get(`/api/v1/positions/${id}`);
      currentPosition.value = response;
      return response;
    } catch (err: any) {
      error.value = err.message || '获取职位详情失败';
      throw err;
    } finally {
      isLoading.value = false;
    }
  }

  // 创建职位
  async function createPosition(positionData: PositionCreateUpdate) {
    isLoading.value = true;
    error.value = null;
    try {
      const response = await post('/api/v1/positions/', positionData);
      // 重新获取职位列表以更新状态
      await getPositions();
      return response;
    } catch (err: any) {
      error.value = err.message || '创建职位失败';
      throw err;
    } finally {
      isLoading.value = false;
    }
  }

  // 更新职位
  async function updatePosition(id: number, positionData: PositionCreateUpdate) {
    isLoading.value = true;
    error.value = null;
    try {
      const response = await put(`/api/v1/positions/${id}`, positionData);
      // 更新本地数据
      const index = positions.value.findIndex(pos => pos.id === id);
      if (index !== -1) {
        positions.value[index] = { ...positions.value[index], ...response };
      }
      if (currentPosition.value && currentPosition.value.id === id) {
        currentPosition.value = { ...currentPosition.value, ...response };
      }
      return response;
    } catch (err: any) {
      error.value = err.message || '更新职位失败';
      throw err;
    } finally {
      isLoading.value = false;
    }
  }

  // 删除职位
  async function deletePosition(id: number) {
    isLoading.value = true;
    error.value = null;
    try {
      await del(`/api/v1/positions/${id}`);
      // 从本地列表中移除
      positions.value = positions.value.filter(pos => pos.id !== id);
      if (currentPosition.value && currentPosition.value.id === id) {
        currentPosition.value = null;
      }
      return true;
    } catch (err: any) {
      error.value = err.message || '删除职位失败';
      throw err;
    } finally {
      isLoading.value = false;
    }
  }

  // 获取部门下的所有职位
  async function getPositionsByDepartment(departmentId: number) {
    return getPositions({ department_id: departmentId });
  }

  return {
    positions,
    currentPosition,
    totalCount,
    isLoading,
    error,
    getPositions,
    getPosition,
    createPosition,
    updatePosition,
    deletePosition,
    getPositionsByDepartment
  };
}); 