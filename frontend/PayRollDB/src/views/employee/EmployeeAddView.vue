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
              <el-form-item label="姓名" prop="name">
                <el-input v-model="form.name" placeholder="请输入姓名" />
              </el-form-item>
            </el-col>
            <el-col :span="12">
              <el-form-item label="身份证号" prop="idCard">
                <el-input v-model="form.idCard" placeholder="请输入身份证号" />
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
        </el-card>
      </el-form>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted, watch } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, type FormInstance } from 'element-plus'
import { useEmployeesStore } from '@/stores/employees'
import { useDepartmentsStore } from '@/stores/departments'
import { usePositionsStore } from '@/stores/positions'
import { useAuthStore } from '@/stores/auth'

// 路由和Store
const router = useRouter()
const employeesStore = useEmployeesStore()
const departmentsStore = useDepartmentsStore()
const positionsStore = usePositionsStore()
const authStore = useAuthStore()

// 状态定义
const loading = ref(false)
const formRef = ref<FormInstance | null>(null)

// 表单数据
const form = reactive({
  name: '',
  departmentId: '',
  positionId: '',
  hireDate: '',
  status: 1,
  baseSalary: 0,
  phone: '',
  email: '',
  address: '',
  bankName: '',
  bankAccount: '',
  idCard: ''
})

// 计算属性
const departmentOptions = computed(() => {
  return (departmentsStore.departments || []).map(dept => ({
    value: dept.id,
    label: dept.name
  }))
})

const positionOptions = computed(() => {
  if (!positionsStore.positions || positionsStore.positions.length === 0) {
    console.log('职位数据未加载')
    return []
  }
  
  if (!form.departmentId) {
    console.log('未选择部门')
    return []
  }
  
  const filtered = positionsStore.positions
    .filter(pos => pos.department_id === parseInt(form.departmentId))
    .map(pos => ({
      value: pos.id,
      label: pos.name
    }))
  
  console.log(`部门${form.departmentId}的职位选项:`, filtered)
  return filtered
})

// 表单验证规则
const rules = {
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
    { type: 'email', message: '请输入正确的邮箱地址', trigger: 'blur' }
  ],
  idCard: [
    { required: true, message: '请输入身份证号', trigger: 'blur' }
  ]
}

// 监听器
watch(() => form.departmentId, (newVal, oldVal) => {
  if (newVal !== oldVal) {
    form.positionId = ''
  }
})

// 方法
const goBack = () => {
  router.go(-1)
}

const formatDate = (date: any) => {
  if (date && typeof date.toISOString === 'function') {
    return date.toISOString().split('T')[0]
  }
  return undefined
}

const handleSubmit = async () => {
  if (!formRef.value) {
    console.error('表单引用不存在')
    return
  }
  
  // 打印用户和Token信息，用于调试
  console.log('当前Token:', localStorage.getItem('token'))
  console.log('当前用户信息:', localStorage.getItem('user'))
  
  await formRef.value.validate(async (valid) => {
    if (valid) {
      loading.value = true
      
      try {
        // 准备要发送的数据，确保字段名与后端模型一致
        const employeeData = {
          name: form.name,
          id_card: form.idCard,
          department_id: parseInt(form.departmentId),
          position_id: parseInt(form.positionId),
          hire_date: formatDate(form.hireDate),
          base_salary: Number(form.baseSalary),
          phone: form.phone,
          email: form.email || '',
          address: form.address || '',
          bank_name: form.bankName || '',
          bank_account: form.bankAccount || '',
          status: form.status === 1
        }
        
        console.log('提交的员工数据:', employeeData)
        
        // 调用 store 中的创建员工方法
        await employeesStore.createEmployee(employeeData)
        
        ElMessage.success('员工添加成功')
        router.push('/employee/list')
      } catch (error: any) {
        console.error('添加员工失败:', error)
        
        // 详细处理错误响应
        if (error.response) {
          console.error('错误响应:', error.response)
          console.error('错误状态码:', error.response.status)
          console.error('错误数据:', error.response.data)
          
          // 针对422错误提供更详细的反馈
          if (error.response.status === 422) {
            const errorDetails = error.response.data.detail || []
            if (Array.isArray(errorDetails)) {
              const errorMessages = errorDetails.map((err: any) => {
                return `${err.loc.join('.')}：${err.msg}`
              }).join('\n')
              ElMessage.error(`提交数据验证失败:\n${errorMessages}`)
            } else {
              ElMessage.error(`提交数据验证失败: ${JSON.stringify(error.response.data)}`)
            }
          } else {
            ElMessage.error(`添加失败: ${error.message || '未知错误'} (${error.response.status})`)
          }
        } else {
          ElMessage.error(`添加失败: ${error.message || '未知错误'}`)
        }
      } finally {
        loading.value = false
      }
    }
  })
}

// 确保首次加载时数据存在
const initializeStores = () => {
  if (!positionsStore.positions) {
    positionsStore.positions = []
  }

  if (!departmentsStore.departments) {
    departmentsStore.departments = []
  }
}

// 生命周期钩子
onMounted(async () => {
  console.log('组件开始挂载')
  try {
    loading.value = true
    
    // 刷新用户信息，确保token有效
    await authStore.refreshUserInfo()
    console.log('当前用户信息:', authStore.user)
    
    // 确保存储区已初始化
    initializeStores()
    
    // 获取部门和职位数据
    await Promise.all([
      departmentsStore.getDepartments(),
      positionsStore.getPositions()
    ])
    
    console.log('数据加载完成:', {
      departments: departmentsStore.departments,
      positions: positionsStore.positions
    })
  } catch (error: any) {
    console.error('数据加载失败:', error)
    ElMessage.error(`数据加载失败: ${error.message || '未知错误'}`)
  } finally {
    loading.value = false
  }
})
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