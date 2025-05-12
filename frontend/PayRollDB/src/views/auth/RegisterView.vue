<template>
  <div class="register-container">
    <div class="register-card">
      <div class="register-header">
        <h2>薪资管理系统</h2>
        <p>管理员注册</p>
      </div>
      
      <el-form 
        ref="registerFormRef" 
        :model="registerForm" 
        :rules="registerRules" 
        class="register-form"
        label-position="top"
      >
        <el-form-item label="职工号" prop="employeeId">
          <el-input
            v-model="registerForm.employeeId"
            placeholder="请输入职工号"
          />
        </el-form-item>
        
        <el-form-item label="姓名" prop="name">
          <el-input
            v-model="registerForm.name"
            placeholder="请输入姓名"
          />
        </el-form-item>
        
        <el-form-item label="密码" prop="password">
          <el-input
            v-model="registerForm.password"
            type="password"
            placeholder="请输入密码"
            show-password
          />
        </el-form-item>
        
        <el-form-item label="确认密码" prop="confirmPassword">
          <el-input
            v-model="registerForm.confirmPassword"
            type="password"
            placeholder="请确认密码"
            show-password
          />
        </el-form-item>
        
        <el-form-item label="用户角色" prop="role">
          <el-select v-model="registerForm.role" placeholder="请选择角色" style="width: 100%">
            <el-option label="管理员" value="admin" />
            <el-option label="员工" value="employee" />
          </el-select>
        </el-form-item>
        
        <el-button 
          type="primary" 
          class="register-button" 
          :loading="loading" 
          @click="handleRegister"
        >
          {{ loading ? '注册中...' : '注 册' }}
        </el-button>
        
        <div class="login-link">
          <span>已有账号？</span>
          <el-link type="primary" @click="toLogin">返回登录</el-link>
        </div>
      </el-form>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, FormInstance } from 'element-plus'

// 路由
const router = useRouter()

// 注册表单
const registerFormRef = ref<FormInstance>()
const registerForm = reactive({
  employeeId: '',
  name: '',
  password: '',
  confirmPassword: '',
  role: 'admin'
})

// 自定义密码验证规则
const validatePassword = (rule: any, value: string, callback: any) => {
  if (value === '') {
    callback(new Error('请输入密码'))
  } else if (value.length < 6) {
    callback(new Error('密码长度不能小于6位'))
  } else {
    if (registerForm.confirmPassword !== '') {
      registerFormRef.value?.validateField('confirmPassword')
    }
    callback()
  }
}

// 自定义确认密码验证规则
const validateConfirmPassword = (rule: any, value: string, callback: any) => {
  if (value === '') {
    callback(new Error('请再次输入密码'))
  } else if (value !== registerForm.password) {
    callback(new Error('两次输入密码不一致'))
  } else {
    callback()
  }
}

// 表单验证规则
const registerRules = {
  employeeId: [
    { required: true, message: '请输入职工号', trigger: 'blur' },
  ],
  name: [
    { required: true, message: '请输入姓名', trigger: 'blur' },
  ],
  password: [
    { validator: validatePassword, trigger: 'blur' }
  ],
  confirmPassword: [
    { validator: validateConfirmPassword, trigger: 'blur' }
  ],
  role: [
    { required: true, message: '请选择角色', trigger: 'change' }
  ]
}

// 注册加载状态
const loading = ref(false)

// 处理注册
const handleRegister = () => {
  registerFormRef.value?.validate((valid) => {
    if (valid) {
      loading.value = true
      
      // 模拟注册请求
      setTimeout(() => {
        loading.value = false
        
        // 模拟注册成功
        ElMessage.success('注册成功，请登录')
        
        // 跳转到登录页面
        router.push('/login')
      }, 1500)
    }
  })
}

// 跳转到登录页
const toLogin = () => {
  router.push('/login')
}
</script>

<style scoped lang="scss">
.register-container {
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
  
  .register-card {
    width: 100%;
    max-width: 450px;
    background-color: #fff;
    border-radius: 8px;
    box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);
    padding: 25px 20px;
    margin: 0 15px;
    box-sizing: border-box;
    
    .register-header {
      text-align: center;
      margin-bottom: 20px;
      
      h2 {
        font-size: 22px;
        font-weight: 600;
        color: #333;
        margin-bottom: 8px;
      }
      
      p {
        font-size: 16px;
        color: #666;
        margin: 0;
      }
    }
    
    .register-form {
      .register-button {
        width: 100%;
        height: 40px;
        font-size: 16px;
        margin-top: 10px;
      }
      
      .login-link {
        margin-top: 15px;
        text-align: center;
        font-size: 14px;
        color: #999;
      }
    }
  }
}

@media screen and (max-width: 768px) {
  .register-container {
    .register-card {
      width: 90%;
      padding: 20px 15px;
    }
  }
}

@media screen and (max-width: 480px) {
  .register-container {
    .register-card {
      width: 100%;
      margin: 0 10px;
      padding: 20px 15px;
      
      .register-header {
        h2 {
          font-size: 20px;
        }
        
        p {
          font-size: 14px;
        }
      }
      
      .register-form {
        .register-button {
          height: 38px;
          font-size: 15px;
        }
      }
    }
  }
}
</style> 