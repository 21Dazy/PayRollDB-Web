<template>
  <div class="login-container">
    <div class="login-card">
      <div class="login-header">
        <h2>薪资管理系统</h2>
        <p>欢迎使用薪资管理系统，请登录</p>
      </div>
      
      <div class="login-tabs">
        <el-tabs v-model="activeTab" type="card">
          <el-tab-pane label="员工登录" name="employee"></el-tab-pane>
          <el-tab-pane label="管理员登录" name="admin"></el-tab-pane>
        </el-tabs>
      </div>
      
      <el-form 
        ref="loginFormRef" 
        :model="loginForm" 
        :rules="loginRules" 
        class="login-form"
      >
        <el-form-item prop="username">
          <el-input
            v-model="loginForm.username"
            placeholder="请输入职工号"
            :prefix-icon="User"
          />
        </el-form-item>
        
        <el-form-item prop="password">
          <el-input
            v-model="loginForm.password"
            type="password"
            placeholder="请输入密码"
            :prefix-icon="Lock"
            show-password
            @keyup.enter="handleLogin"
          />
        </el-form-item>
        
        <el-form-item class="login-action">
          <el-checkbox v-model="rememberMe">记住我</el-checkbox>
          <el-link type="primary">忘记密码?</el-link>
        </el-form-item>
        
        <el-button 
          type="primary" 
          class="login-button" 
          :loading="authStore.isLoading" 
          @click="handleLogin"
        >
          {{ authStore.isLoading ? '登录中...' : '登 录' }}
        </el-button>
        
        <div class="register-link" v-if="activeTab === 'admin'">
          <span>还没有账号？</span>
          <el-link type="primary" @click="toRegister">立即注册</el-link>
        </div>
      </el-form>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import type { FormInstance } from 'element-plus'
import { User, Lock } from '@element-plus/icons-vue'
import { useAuthStore } from '@/stores/auth'

// 路由
const router = useRouter()

// 认证状态管理
const authStore = useAuthStore()

// 登录表单
const loginFormRef = ref<FormInstance>()
const loginForm = reactive({
  username: '',
  password: ''
})

// 表单验证规则
const loginRules = {
  username: [
    { required: true, message: '请输入职工号', trigger: 'blur' },
  ],
  password: [
    { required: true, message: '请输入密码', trigger: 'blur' },
    { min: 6, message: '密码长度不能小于6位', trigger: 'blur' }
  ]
}

// 记住我
const rememberMe = ref(false)

// 当前激活的标签页
const activeTab = ref('employee')

// 处理登录
const handleLogin = () => {
  loginFormRef.value?.validate(async (valid) => {
    if (valid) {
      try {
        await authStore.login(loginForm.username, loginForm.password)
        ElMessage.success('登录成功')
        
        // 如果记住我，可以在这里处理额外的本地存储
        if (rememberMe.value) {
          localStorage.setItem('remember_username', loginForm.username)
        } else {
          localStorage.removeItem('remember_username')
        }
        
        // 跳转到首页
        router.push('/dashboard')
      } catch (error: any) {
        ElMessage.error(error.message || '登录失败，请检查用户名和密码')
      }
    }
  })
}

// 跳转到注册页
const toRegister = () => {
  router.push('/register')
}
</script>

<style scoped lang="scss">
.login-container {
  height: 100vh;
  width: 100vw;
  display: flex;
  justify-content: center;
  align-items: center;
  background: linear-gradient(135deg, #3a8ffe 0%, #1989fa 100%);
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  margin: 0;
  padding: 0;
  overflow: hidden;
  
  .login-card {
    width: 100%;
    max-width: 450px;
    background-color: #fff;
    border-radius: 8px;
    box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);
    padding: 25px 20px;
    margin: 0 15px;
    box-sizing: border-box;
    
    .login-header {
      text-align: center;
      margin-bottom: 20px;
      
      h2 {
        font-size: 22px;
        font-weight: 600;
        color: #333;
        margin-bottom: 8px;
      }
      
      p {
        font-size: 14px;
        color: #999;
        margin: 0;
      }
    }
    
    .login-tabs {
      margin-bottom: 20px;
      
      :deep(.el-tabs__header) {
        margin-bottom: 15px;
      }
    }
    
    .login-form {
      .login-action {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 10px;
      }
      
      .login-button {
        width: 100%;
        height: 40px;
        font-size: 16px;
      }
      
      .register-link {
        margin-top: 15px;
        text-align: center;
        font-size: 14px;
        color: #999;
      }
    }
  }
}

@media screen and (max-width: 768px) {
  .login-container {
    .login-card {
      width: 90%;
      padding: 20px 15px;
    }
  }
}

@media screen and (max-width: 480px) {
  .login-container {
    .login-card {
      width: 100%;
      margin: 0 10px;
      padding: 20px 15px;
      
      .login-header {
        h2 {
          font-size: 20px;
        }
        
        p {
          font-size: 13px;
        }
      }
      
      .login-form {
        .login-button {
          height: 38px;
          font-size: 15px;
        }
      }
    }
  }
}
</style> 