import { defineStore } from 'pinia';
import { ref } from 'vue';
import { post, get } from '@/utils/request';

interface LoginResponse {
  access_token: string;
  user: any;
}

export const useAuthStore = defineStore('auth', () => {
  const token = ref<string | null>(localStorage.getItem('token'));
  const user = ref<any>(JSON.parse(localStorage.getItem('user') || 'null'));
  const isAuthenticated = ref<boolean>(!!token.value);
  const isLoading = ref<boolean>(false);
  const error = ref<string | null>(null);

  // 登录
  async function login(username: string, password: string) {
    isLoading.value = true;
    error.value = null;
    try {
      const response = await post('/api/v1/auth/login/access-token', {
        username,
        password
      });
      
      token.value = response.access_token;
      user.value = response.user;
      isAuthenticated.value = true;
      
      // 保存到本地存储
      localStorage.setItem('token', response.access_token);
      localStorage.setItem('user', JSON.stringify(response.user));
      
      return response;
    } catch (err: any) {
      error.value = err.message || '登录失败';
      throw err;
    } finally {
      isLoading.value = false;
    }
  }

  // 登出
  function logout() {
    token.value = null;
    user.value = null;
    isAuthenticated.value = false;
    localStorage.removeItem('token');
    localStorage.removeItem('user');
  }

  // 获取当前用户信息
  async function getCurrentUser() {
    if (!token.value) return null;
    
    isLoading.value = true;
    try {
      const response = await get('/api/v1/users/me');
      user.value = response;
      localStorage.setItem('user', JSON.stringify(response));
      return response;
    } catch (err: any) {
      error.value = err.message || '获取用户信息失败';
      throw err;
    } finally {
      isLoading.value = false;
    }
  }

  return {
    token,
    user,
    isAuthenticated,
    isLoading,
    error,
    login,
    logout,
    getCurrentUser
  };
}); 