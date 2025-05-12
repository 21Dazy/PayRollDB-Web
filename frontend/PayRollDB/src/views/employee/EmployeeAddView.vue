<template>
  <div class="employee-add">
    <div class="page-header">
      <h2>添加员工</h2>
      <div class="page-actions">
        <el-button @click="goBack">返回</el-button>
        <el-button type="primary" @click="handleSubmit" :loading="loading">保存</el-button>
      </div>
    </div>
    
    <div class="form-container">
      <el-form 
        ref="formRef" 
        :model="form" 
        :rules="rules" 
        label-width="100px"
        label-position="right"
      >
        <el-card shadow="hover" class="form-card">
          <template #header>
            <div class="card-header">
              <span>基本信息</span>
            </div>
          </template>
          
          <el-row :gutter="20">
            <el-col :span="12">
              <el-form-item label="工号" prop="employeeId">
                <el-input v-model="form.employeeId" placeholder="请输入工号" />
              </el-form-item>
            </el-col>
            <el-col :span="12">
              <el-form-item label="姓名" prop="name">
                <el-input v-model="form.name" placeholder="请输入姓名" />
              </el-form-item>
            </el-col>
          </el-row>
          
          <el-row :gutter="20">
            <el-col :span="12">
              <el-form-item label="部门" prop="departmentId">
                <el-select v-model="form.departmentId" placeholder="请选择部门" style="width: 100%">
                  <el-option
                    v-for="item in departmentOptions"
                    :key="item.value"
                    :label="item.label"
                    :value="item.value"
                  />
                </el-select>
              </el-form-item>
            </el-col>
            <el-col :span="12">
              <el-form-item label="职位" prop="positionId">
                <el-select v-model="form.positionId" placeholder="请选择职位" style="width: 100%">
                  <el-option
                    v-for="item in positionOptions"
                    :key="item.value"
                    :label="item.label"
                    :value="item.value"
                  />
                </el-select>
              </el-form-item>
            </el-col>
          </el-row>
          
          <el-row :gutter="20">
            <el-col :span="12">
              <el-form-item label="入职日期" prop="hireDate">
                <el-date-picker
                  v-model="form.hireDate"
                  type="date"
                  placeholder="请选择入职日期"
                  style="width: 100%"
                />
              </el-form-item>
            </el-col>
            <el-col :span="12">
              <el-form-item label="状态" prop="status">
                <el-select v-model="form.status" placeholder="请选择状态" style="width: 100%">
                  <el-option label="在职" :value="1" />
                  <el-option label="离职" :value="0" />
                </el-select>
              </el-form-item>
            </el-col>
          </el-row>
        </el-card>
        
        <el-card shadow="hover" class="form-card">
          <template #header>
            <div class="card-header">
              <span>薪资信息</span>
            </div>
          </template>
          
          <el-row :gutter="20">
            <el-col :span="12">
              <el-form-item label="基本工资" prop="baseSalary">
                <el-input-number
                  v-model="form.baseSalary"
                  :min="0"
                  :precision="2"
                  :step="1000"
                  style="width: 100%"
                />
              </el-form-item>
            </el-col>
            <el-col :span="12">
              <el-form-item label="绩效基数" prop="performanceBase">
                <el-input-number
                  v-model="form.performanceBase"
                  :min="0"
                  :precision="2"
                  :step="500"
                  style="width: 100%"
                />
              </el-form-item>
            </el-col>
          </el-row>
        </el-card>
        
        <el-card shadow="hover" class="form-card">
          <template #header>
            <div class="card-header">
              <span>联系信息</span>
            </div>
          </template>
          
          <el-row :gutter="20">
            <el-col :span="12">
              <el-form-item label="手机号码" prop="phone">
                <el-input v-model="form.phone" placeholder="请输入手机号码" />
              </el-form-item>
            </el-col>
            <el-col :span="12">
              <el-form-item label="电子邮箱" prop="email">
                <el-input v-model="form.email" placeholder="请输入电子邮箱" />
              </el-form-item>
            </el-col>
          </el-row>
          
          <el-form-item label="联系地址" prop="address">
            <el-input v-model="form.address" placeholder="请输入联系地址" />
          </el-form-item>
        </el-card>
        
        <el-card shadow="hover" class="form-card">
          <template #header>
            <div class="card-header">
              <span>银行信息</span>
            </div>
          </template>
          
          <el-row :gutter="20">
            <el-col :span="12">
              <el-form-item label="开户银行" prop="bankName">
                <el-input v-model="form.bankName" placeholder="请输入开户银行" />
              </el-form-item>
            </el-col>
            <el-col :span="12">
              <el-form-item label="银行账号" prop="bankAccount">
                <el-input v-model="form.bankAccount" placeholder="请输入银行账号" />
              </el-form-item>
            </el-col>
          </el-row>
          
          <el-row :gutter="20">
            <el-col :span="12">
              <el-form-item label="开户支行" prop="bankBranch">
                <el-input v-model="form.bankBranch" placeholder="请输入开户支行" />
              </el-form-item>
            </el-col>
            <el-col :span="12">
              <el-form-item label="账户名" prop="bankAccountName">
                <el-input v-model="form.bankAccountName" placeholder="请输入账户名" />
              </el-form-item>
            </el-col>
          </el-row>
        </el-card>
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

// 表单引用
const formRef = ref<FormInstance>()

// 部门选项
const departmentOptions = ref([
  { value: '1', label: '研发部' },
  { value: '2', label: '市场部' },
  { value: '3', label: '销售部' },
  { value: '4', label: '财务部' },
  { value: '5', label: '人事部' }
])

// 职位选项
const positionOptions = ref([
  { value: '1', label: '总监' },
  { value: '2', label: '经理' },
  { value: '3', label: '主管' },
  { value: '4', label: '工程师' },
  { value: '5', label: '专员' }
])

// 表单数据
const form = reactive({
  employeeId: '',
  name: '',
  departmentId: '',
  positionId: '',
  hireDate: '',
  status: 1,
  baseSalary: 0,
  performanceBase: 0,
  phone: '',
  email: '',
  address: '',
  bankName: '',
  bankAccount: '',
  bankBranch: '',
  bankAccountName: ''
})

// 表单验证规则
const rules = {
  employeeId: [
    { required: true, message: '请输入工号', trigger: 'blur' }
  ],
  name: [
    { required: true, message: '请输入姓名', trigger: 'blur' }
  ],
  departmentId: [
    { required: true, message: '请选择部门', trigger: 'change' }
  ],
  positionId: [
    { required: true, message: '请选择职位', trigger: 'change' }
  ],
  hireDate: [
    { required: true, message: '请选择入职日期', trigger: 'change' }
  ],
  status: [
    { required: true, message: '请选择状态', trigger: 'change' }
  ],
  baseSalary: [
    { required: true, message: '请输入基本工资', trigger: 'blur' }
  ],
  phone: [
    { required: true, message: '请输入手机号码', trigger: 'blur' },
    { pattern: /^1[3-9]\d{9}$/, message: '请输入正确的手机号码', trigger: 'blur' }
  ],
  email: [
    { required: true, message: '请输入电子邮箱', trigger: 'blur' },
    { type: 'email', message: '请输入正确的邮箱地址', trigger: 'blur' }
  ]
}

// 加载状态
const loading = ref(false)

// 返回
const goBack = () => {
  router.go(-1)
}

// 提交表单
const handleSubmit = () => {
  formRef.value?.validate((valid) => {
    if (valid) {
      loading.value = true
      
      // 模拟提交
      setTimeout(() => {
        loading.value = false
        ElMessage.success('添加成功')
        router.push('/employee/list')
      }, 1500)
    }
  })
}
</script>

<style scoped lang="scss">
.employee-add {
  .page-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 20px;
    
    h2 {
      font-size: 20px;
      font-weight: 600;
      margin: 0;
    }
    
    .page-actions {
      display: flex;
      gap: 10px;
    }
  }
  
  .form-container {
    .form-card {
      margin-bottom: 20px;
      
      .card-header {
        font-weight: bold;
      }
    }
  }
}
</style> 