import { defineStore } from 'pinia';
import { ref } from 'vue';
import { get, post, put, del } from '@/utils/request';

interface User {
  id: number;
  username: string;
  employee_id?: number;
  role: string;
  is_active: boolean;
  created_at: string;
  last_login?: string;
  [key: string]: any;
}

interface UserCreateUpdate {
  username?: string;
  password?: string;
  employee_id?: number;
  role?: string;
  is_active?: boolean;
}

interface UserPasswordUpdate {
  current_password: string;
  new_password: string;
}

interface QueryParams {
  skip?: number;
  limit?: number;
  role?: string;
  is_active?: boolean;
}

export const useUsersStore = defineStore('users', () => {
  const users = ref<User[]>([]);
  const currentUser = ref<User | null>(null);
  const totalCount = ref<number>(0);
  const isLoading = ref<boolean>(false);
  const error = ref<string | null>(null);

  // 获取用户列表
  async function getUsers(params: QueryParams = {}) {
    isLoading.value = true;
    error.value = null;
    try {
      const response = await get('/api/v1/users/', { params });
      users.value = response;
      totalCount.value = response.length;
      return response;
    } catch (err: any) {
      error.value = err.message || '获取用户列表失败';
      throw err;
    } finally {
      isLoading.value = false;
    }
  }

  // 获取单个用户
  async function getUser(id: number) {
    isLoading.value = true;
    error.value = null;
    try {
      const response = await get(`/api/v1/users/${id}`);
      currentUser.value = response;
      return response;
    } catch (err: any) {
      error.value = err.message || '获取用户详情失败';
      throw err;
    } finally {
      isLoading.value = false;
    }
  }

  // 创建用户
  async function createUser(userData: UserCreateUpdate) {
    isLoading.value = true;
    error.value = null;
    try {
      const response = await post('/api/v1/users/', userData);
      // 重新获取用户列表以更新状态
      await getUsers();
      return response;
    } catch (err: any) {
      error.value = err.message || '创建用户失败';
      throw err;
    } finally {
      isLoading.value = false;
    }
  }

  // 更新用户
  async function updateUser(id: number, userData: UserCreateUpdate) {
    isLoading.value = true;
    error.value = null;
    try {
      const response = await put(`/api/v1/users/${id}`, userData);
      // 更新本地数据
      const index = users.value.findIndex(user => user.id === id);
      if (index !== -1) {
        users.value[index] = { ...users.value[index], ...response };
      }
      if (currentUser.value && currentUser.value.id === id) {
        currentUser.value = { ...currentUser.value, ...response };
      }
      return response;
    } catch (err: any) {
      error.value = err.message || '更新用户失败';
      throw err;
    } finally {
      isLoading.value = false;
    }
  }

  // 删除用户
  async function deleteUser(id: number) {
    isLoading.value = true;
    error.value = null;
    try {
      await del(`/api/v1/users/${id}`);
      // 从本地列表中移除
      users.value = users.value.filter(user => user.id !== id);
      if (currentUser.value && currentUser.value.id === id) {
        currentUser.value = null;
      }
      return true;
    } catch (err: any) {
      error.value = err.message || '删除用户失败';
      throw err;
    } finally {
      isLoading.value = false;
    }
  }

  // 修改密码
  async function changePassword(userId: number, passwordData: UserPasswordUpdate) {
    isLoading.value = true;
    error.value = null;
    try {
      await post(`/api/v1/users/${userId}/change-password`, passwordData);
      return true;
    } catch (err: any) {
      error.value = err.message || '修改密码失败';
      throw err;
    } finally {
      isLoading.value = false;
    }
  }

  return {
    users,
    currentUser,
    totalCount,
    isLoading,
    error,
    getUsers,
    getUser,
    createUser,
    updateUser,
    deleteUser,
    changePassword
  };
}); 