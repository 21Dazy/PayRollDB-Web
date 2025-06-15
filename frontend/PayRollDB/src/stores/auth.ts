import { defineStore } from 'pinia';
import { ref } from 'vue';
import { post, get } from '@/utils/request';
import axios from 'axios';

interface LoginResponse {
  access_token: string;
  token_type: string;
}

// 创建加密函数，用于简单加密存储的密码
function simpleEncrypt(text: string): string {
  return btoa(text); // 简单的Base64编码
}

// 解密函数
function simpleDecrypt(encryptedText: string): string {
  return atob(encryptedText); // Base64解码
}

export const useAuthStore = defineStore('auth', () => {
  const token = ref<string | null>(localStorage.getItem('token'));
  const user = ref<any>(JSON.parse(localStorage.getItem('user') || 'null'));
  const isAuthenticated = ref<boolean>(!!token.value);
  const isLoading = ref<boolean>(false);
  const error = ref<string | null>(null);
  const lastUsername = ref<string | null>(localStorage.getItem('lastUsername'));
  const lastPassword = ref<string | null>(localStorage.getItem('lastEncryptedPassword') ? 
    simpleDecrypt(localStorage.getItem('lastEncryptedPassword') || '') : null);

  // 登录
  async function login(username: string, password: string, rememberCredentials: boolean = true) {
    isLoading.value = true;
    error.value = null;
    try {
      // 使用 URLSearchParams 而不是 FormData，符合 OAuth2 的 application/x-www-form-urlencoded 格式
      const formData = new URLSearchParams();
      formData.append('username', username);
      formData.append('password', password);
      
      const response = await post('/api/v1/auth/login', formData.toString(), {
        headers: {
          'Content-Type': 'application/x-www-form-urlencoded'
        }
      });
      
      token.value = response.access_token;
      isAuthenticated.value = true;
      
      // 保存到本地存储
      localStorage.setItem('token', response.access_token);
      
      // 记住用户名和密码（如果选择记住）
      if (rememberCredentials) {
        localStorage.setItem('lastUsername', username);
        localStorage.setItem('lastEncryptedPassword', simpleEncrypt(password));
        lastUsername.value = username;
        lastPassword.value = password;
      }
      
      // 获取用户信息
      await getCurrentUser();
      
      return response;
    } catch (err: any) {
      error.value = err.message || '登录失败';
      throw err;
    } finally {
      isLoading.value = false;
    }
  }

  // 自动重新登录
  async function autoRelogin() {
    if (lastUsername.value && lastPassword.value) {
      try {
        console.log('尝试自动重新登录...');
        await login(lastUsername.value, lastPassword.value);
        return true;
      } catch (err) {
        console.error('自动重新登录失败:', err);
        return false;
      }
    }
    return false;
  }

  // 登出
  function logout() {
    token.value = null;
    user.value = null;
    isAuthenticated.value = false;
    localStorage.removeItem('token');
    localStorage.removeItem('user');
    // 不清除记住的凭据，以便下次可以自动登录
  }

  // 完全清除所有凭据（包括记住的用户名和密码）
  function clearAllCredentials() {
    logout();
    localStorage.removeItem('lastUsername');
    localStorage.removeItem('lastEncryptedPassword');
    lastUsername.value = null;
    lastPassword.value = null;
  }

  // 获取当前用户信息
  async function getCurrentUser() {
    if (!token.value) return null;
    
    isLoading.value = true;
    try {
      const response = await get('/api/v1/auth/me');
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

  // 刷新用户信息和Token
  async function refreshUserInfo() {
    isLoading.value = true;
    error.value = null;
    try {
      // 首先检查token是否存在
      if (!token.value) {
        error.value = '未登录，无法刷新用户信息';
        return false;
      }
      
      console.log('正在刷新用户信息...');
      // 获取用户信息
      const response = await get('/api/v1/auth/me');
      user.value = response;
      localStorage.setItem('user', JSON.stringify(response));
      console.log('用户信息刷新成功:', response);
      return true;
    } catch (err: any) {
      console.error('刷新用户信息失败:', err);
      error.value = err.message || '刷新用户信息失败';
      
      // 如果是401错误，尝试自动重新登录
      if (err.response && err.response.status === 401) {
        console.log('Token无效，尝试自动重新登录');
        return await autoRelogin();
      }
      return false;
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
    getCurrentUser,
    autoRelogin,
    clearAllCredentials,
    lastUsername,
    refreshUserInfo
  };
}); 