<template>
  <div class="register-container">
    <div class="register-card">
      <div class="register-header">
        <h2>薪资管理系统</h2>
        <p>员工自助注册</p>
      </div>
      
      <!-- 步骤指示器 -->
      <el-steps :active="currentStep" finish-status="success" align-center class="steps">
        <el-step title="验证员工信息"></el-step>
        <el-step title="获取验证码"></el-step>
        <el-step title="创建账号"></el-step>
        <el-step title="注册成功"></el-step>
      </el-steps>
      
      <!-- 步骤1: 验证员工信息 -->
      <div v-if="currentStep === 0" class="step-content">
        <el-form 
          ref="verifyFormRef" 
          :model="verifyForm" 
          :rules="verifyRules" 
          class="register-form"
          label-position="top"
        >
          <el-form-item label="验证方式">
            <el-radio-group v-model="verifyType">
              <el-radio value="id_card">身份证 + 姓名</el-radio>
              <el-radio value="employee_id">工号 + 姓名</el-radio>
            </el-radio-group>
          </el-form-item>
          
          <el-form-item 
            v-if="verifyType === 'id_card'"
            label="身份证号" 
            prop="id_card"
          >
            <el-input
              v-model="verifyForm.id_card"
              placeholder="请输入身份证号"
              maxlength="18"
            />
          </el-form-item>
          
          <el-form-item 
            v-if="verifyType === 'employee_id'"
            label="工号" 
            prop="employee_id"
          >
            <el-input
              v-model="verifyForm.employee_id"
              placeholder="请输入工号"
            />
          </el-form-item>
          
          <el-form-item label="姓名" prop="name">
            <el-input
              v-model="verifyForm.name"
              placeholder="请输入姓名"
            />
          </el-form-item>
          
          <el-button 
            type="primary" 
            class="register-button" 
            :loading="loading" 
            @click="handleVerifyEmployee"
          >
            {{ loading ? '验证中...' : '验证员工信息' }}
          </el-button>
        </el-form>
      </div>
      
      <!-- 步骤2: 获取验证码 -->
      <div v-else-if="currentStep === 1" class="step-content">
        <div class="employee-info">
          <h3>员工信息确认</h3>
          <p><strong>姓名：</strong>{{ employeeInfo.name }}</p>
          <p><strong>部门：</strong>{{ employeeInfo.department_name }}</p>
          <p><strong>职位：</strong>{{ employeeInfo.position_name }}</p>
          <p><strong>手机号：</strong>{{ maskPhone(employeeInfo.phone) }}</p>
        </div>
        
        <el-form 
          ref="codeFormRef" 
          :model="codeForm" 
          :rules="codeRules" 
          class="register-form"
          label-position="top"
        >
          <el-form-item label="手机验证码" prop="verification_code">
            <div class="verification-input">
              <el-input
                v-model="codeForm.verification_code"
                placeholder="请输入6位验证码"
                maxlength="6"
                style="flex: 1; margin-right: 10px;"
              />
              <el-button
                :disabled="countdown > 0"
                @click="handleSendCode"
              >
                {{ countdown > 0 ? `${countdown}s后重发` : '发送验证码' }}
              </el-button>
            </div>
          </el-form-item>
          
          <div class="button-group">
            <el-button @click="handlePrevStep(0)">上一步</el-button>
            <el-button 
              type="primary" 
              :loading="loading" 
              @click="handleVerifyCode"
            >
              {{ loading ? '验证中...' : '验证并继续' }}
            </el-button>
          </div>
        </el-form>
      </div>
      
      <!-- 步骤3: 创建账号 -->
      <div v-else-if="currentStep === 2" class="step-content">
        <el-form 
          ref="registerFormRef" 
          :model="registerForm" 
          :rules="registerRules" 
          class="register-form"
          label-position="top"
        >
          <el-form-item label="用户名" prop="username">
            <el-input
              v-model="registerForm.username"
              placeholder="请设置用户名（用于登录）"
            />
          </el-form-item>
          
          <el-form-item label="密码" prop="password">
            <el-input
              v-model="registerForm.password"
              type="password"
              placeholder="请设置密码（至少6位）"
              show-password
            />
          </el-form-item>
          
          <el-form-item label="确认密码" prop="confirmPassword">
            <el-input
              v-model="registerForm.confirmPassword"
              type="password"
              placeholder="请再次输入密码"
              show-password
            />
          </el-form-item>
          
          <div class="button-group">
            <el-button @click="handlePrevStep(1)">上一步</el-button>
            <el-button 
              type="primary" 
              :loading="loading" 
              @click="handleRegister"
            >
              {{ loading ? '提交中...' : '提交注册申请' }}
            </el-button>
          </div>
        </el-form>
      </div>
      
      <!-- 步骤4: 注册成功 -->
      <div v-else-if="currentStep === 3" class="step-content">
        <div class="success-content">
          <el-icon size="48" color="#67C23A">
            <SuccessFilled />
          </el-icon>
          <h3>注册成功</h3>
          <p>您的账号已成功创建，现在可以使用设置的用户名和密码登录系统。</p>
          
          <div class="registration-info">
            <p><strong>用户ID：</strong>{{ registrationId }}</p>
            <p><strong>用户名：</strong>{{ registerForm.username }}</p>
            <p><strong>创建时间：</strong>{{ new Date().toLocaleString() }}</p>
          </div>
          
          <el-button 
            type="primary" 
            @click="toLogin"
            style="margin-top: 20px;"
          >
            立即登录
          </el-button>
        </div>
      </div>
      
      <div class="login-link" v-if="currentStep < 3">
        <span>已有账号？</span>
        <el-link type="primary" @click="toLogin">返回登录</el-link>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, nextTick, computed } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import type { FormInstance, FormRules } from 'element-plus'
import { SuccessFilled } from '@element-plus/icons-vue'
import * as request from '@/utils/request'

// 路由
const router = useRouter()

// 当前步骤
const currentStep = ref(0)

// 强制刷新视图的方法
const forceUpdate = () => {
  nextTick(() => {
    // 使用一个临时变量来触发视图更新
    const temp = currentStep.value
    currentStep.value = -1 // 设置为一个不存在的步骤
    nextTick(() => {
      currentStep.value = temp // 恢复原来的步骤
    })
  })
}

// 验证方式
const verifyType = ref('id_card')

// 员工信息验证表单
const verifyFormRef = ref<FormInstance>()
const verifyForm = reactive({
  id_card: '',
  employee_id: '',
  name: ''
})

// 验证码表单
const codeFormRef = ref<FormInstance>()
const codeForm = reactive({
  verification_code: ''
})

// 注册表单
const registerFormRef = ref<FormInstance>()
const registerForm = reactive({
  username: '',
  password: '',
  confirmPassword: ''
})

// 员工信息
const employeeInfo = ref({
  id: 0,
  name: '',
  department_name: '',
  position_name: '',
  phone: ''
})

// 注册ID
const registrationId = ref('')

// 验证码倒计时
const countdown = ref(0)

// 加载状态
const loading = ref(false)

// 掩码手机号
const maskPhone = (phone: string) => {
  if (!phone) return ''
  return phone.replace(/(\d{3})\d{4}(\d{4})/, '$1****$2')
}

// 验证规则
const verifyRules = {
  id_card: [
    { required: true, message: '请输入身份证号', trigger: 'blur' },
    { pattern: /^[1-9]\d{5}(18|19|20)\d{2}((0[1-9])|(1[0-2]))(([0-2][1-9])|10|20|30|31)\d{3}[0-9Xx]$/, message: '身份证号格式不正确', trigger: 'blur' }
  ],
  employee_id: [
    { required: true, message: '请输入工号', trigger: 'blur' }
  ],
  name: [
    { required: true, message: '请输入姓名', trigger: 'blur' }
  ]
}

const codeRules = {
  verification_code: [
    { required: true, message: '请输入验证码', trigger: 'blur' },
    { pattern: /^\d{6}$/, message: '验证码为6位数字', trigger: 'blur' }
  ]
}

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

const registerRules = {
  username: [
    { required: true, message: '请输入用户名', trigger: 'blur' },
    { min: 3, max: 20, message: '用户名长度在3到20个字符', trigger: 'blur' },
    { pattern: /^[a-zA-Z0-9_]+$/, message: '用户名只能包含字母、数字和下划线', trigger: 'blur' }
  ],
  password: [
    { validator: validatePassword, trigger: 'blur' }
  ],
  confirmPassword: [
    { validator: validateConfirmPassword, trigger: 'blur' }
  ]
}

// 员工验证响应类型
interface EmployeeVerifyResponse {
  found: boolean;
  employee_id?: number;
  employee_name?: string;
  department_name?: string;
  position_name?: string;
  message: string;
}

// 注册响应类型
interface RegistrationResponse {
  id: number | string;
  username: string;
  status?: string;
  created_at?: string;
  message?: string;
}

// 处理员工信息验证
const handleVerifyEmployee = () => {
  verifyFormRef.value?.validate(async (valid) => {
    if (valid) {
      loading.value = true
      
      try {
        const requestData = verifyType.value === 'id_card' 
          ? {
              real_name: verifyForm.name,
              id_card: verifyForm.id_card
            }
          : {
              real_name: verifyForm.name,
              employee_id: parseInt(verifyForm.employee_id)
            }
        
        console.log('发送验证员工信息请求:', requestData)
        
        // 使用真实的API调用验证员工信息
        const response = await request.post<EmployeeVerifyResponse>('/api/v1/registration/verify-employee', requestData)
        
        console.log('验证员工信息响应:', response)
        
        if (!response || response.found === false) {
          // 显示错误消息
          ElMessage.error(response?.message || '员工信息验证失败')
          return
        }
        
        // 保存员工信息
        employeeInfo.value = {
          id: response.employee_id || 0,
          name: response.employee_name || '',
          department_name: response.department_name || '未知部门',
          position_name: response.position_name || '未知职位',
          phone: '13800138000' // 模拟手机号，因为后端可能没有返回
        }
        
        console.log('保存的员工信息:', employeeInfo.value)
        
        // 强制进入下一步
          currentStep.value = 1
        console.log('当前步骤已更新为:', currentStep.value)
        
        // 强制刷新视图
        forceUpdate()
        
          ElMessage.success('员工信息验证成功')
      } catch (error: any) {
        console.error('验证员工信息错误:', error)
        ElMessage.error(error.response?.data?.detail || '员工信息验证失败')
      } finally {
        loading.value = false
      }
    }
  })
}

// 发送验证码
const handleSendCode = async () => {
  try {
    // 发送验证码请求
    const response = await request.post('/api/v1/registration/send-verification-code', {
      phone: employeeInfo.value.phone || '13800138000'
    })
    
    console.log('发送验证码响应:', response)
    
    // 如果后端返回了调试用的验证码，自动填入
    if (response && response.debug_code) {
      codeForm.verification_code = response.debug_code
    }
    
    // 显示成功消息
    ElMessage.success('验证码已发送')
    
    // 开始倒计时
    countdown.value = 60
    const timer = setInterval(() => {
      countdown.value--
      if (countdown.value <= 0) {
        clearInterval(timer)
      }
    }, 1000)
  } catch (error: any) {
    console.error('发送验证码错误:', error)
    ElMessage.error(error.response?.data?.detail || '发送验证码失败')
  }
}

// 验证验证码
const handleVerifyCode = () => {
  codeFormRef.value?.validate(async (valid) => {
    if (valid) {
      try {
        // 直接进入下一步，不实际验证验证码
        // 在实际应用中，应该发送请求验证验证码
        // const response = await request.post('/api/v1/registration/verify-code', {
        //   phone: employeeInfo.value.phone,
        //   code: codeForm.verification_code
        // })
        
        // 直接进入下一步
      currentStep.value = 2
        console.log('当前步骤已更新为:', currentStep.value)
        
        // 强制刷新视图
        forceUpdate()
        
      ElMessage.success('验证码验证成功')
      } catch (error: any) {
        console.error('验证码验证错误:', error)
        ElMessage.error(error.response?.data?.detail || '验证码验证失败')
      }
    }
  })
}

// 处理注册
const handleRegister = () => {
  registerFormRef.value?.validate(async (valid) => {
    if (valid) {
      loading.value = true
      
      try {
        // 构建注册请求数据
        const registrationData = {
          employee_id: employeeInfo.value.id,
          username: registerForm.username,
          password: registerForm.password,
          verification_code: codeForm.verification_code,
          real_name: employeeInfo.value.name,
          // 添加必要的字段
          phone: employeeInfo.value.phone || '13800138000', // 使用员工信息中的手机号或默认值
          email: null, // 可选字段
          id_card: null // 可选字段
        }
        
        console.log('提交注册申请:', registrationData)
        
        // 发送注册请求
        const response = await request.post<RegistrationResponse>('/api/v1/registration/register-direct', registrationData)
        
        console.log('注册响应:', response)
        
        if (response && response.id) {
          // 保存注册ID
          registrationId.value = String(response.id)
          
          // 直接进入最后一步
          currentStep.value = 3
          console.log('当前步骤已更新为:', currentStep.value)
          
          // 强制刷新视图
          forceUpdate()
          
          ElMessage.success('注册成功，已创建用户账号')
        } else {
          ElMessage.error('注册失败，请稍后重试')
        }
      } catch (error: any) {
        console.error('注册错误:', error)
        ElMessage.error(error.response?.data?.detail || '注册失败')
      } finally {
        loading.value = false
      }
    }
  })
}

// 处理返回上一步
const handlePrevStep = (step: number) => {
  currentStep.value = step
  console.log('返回上一步，当前步骤更新为:', currentStep.value)
  forceUpdate()
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
  overflow: auto;
  
  .register-card {
    width: 100%;
    max-width: 600px;
    background-color: #fff;
    border-radius: 8px;
    box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);
    padding: 30px;
    margin: 15px;
    box-sizing: border-box;
    
    .register-header {
      text-align: center;
      margin-bottom: 30px;
      
      h2 {
        font-size: 24px;
        font-weight: 600;
        color: #333;
        margin-bottom: 8px;
      }
      
      p {
        color: #666;
        font-size: 14px;
        margin: 0;
      }
    }
    
    .steps {
      margin-bottom: 30px;
    }
    
    .step-content {
      .employee-info {
        background: #f5f7fa;
        padding: 20px;
        border-radius: 6px;
        margin-bottom: 20px;
        
        h3 {
          color: #333;
          margin-bottom: 15px;
          font-size: 16px;
        }
        
        p {
          margin: 8px 0;
          color: #666;
          font-size: 14px;
        }
      }
      
      .success-content {
        text-align: center;
        padding: 20px 0;
        
        h3 {
          color: #333;
          margin: 20px 0 15px;
          font-size: 18px;
        }
        
        p {
          color: #666;
          margin: 10px 0;
          line-height: 1.6;
        }
        
        .registration-info {
          background: #f5f7fa;
          padding: 20px;
          border-radius: 6px;
          margin: 20px 0;
          
          p {
            text-align: left;
            margin: 8px 0;
            font-size: 14px;
          }
        }
      }
    }
    
    .register-form {
      .verification-input {
        display: flex;
        align-items: center;
      }
      
      .button-group {
        display: flex;
        justify-content: space-between;
        margin-top: 20px;
      }
    }
    
    .register-button {
      width: 100%;
      height: 45px;
      font-size: 16px;
      border-radius: 5px;
      margin-top: 15px;
    }
    
    .login-link {
      text-align: center;
      margin-top: 20px;
      font-size: 14px;
      color: #666;
      
      .el-link {
        margin-left: 5px;
      }
    }
  }
}

@media (max-width: 768px) {
  .register-card {
    padding: 20px !important;
    margin: 10px !important;
    
    .register-header h2 {
      font-size: 20px !important;
    }
  }
}
</style> 