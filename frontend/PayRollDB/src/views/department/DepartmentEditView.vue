<template>
  <div class="department-edit">
    <div class="page-header">
      <h2>编辑部门</h2>
      <div class="page-actions">
        <el-button @click="goBack">返回</el-button>
        <el-button type="primary" @click="handleSubmit" :loading="loading">保存</el-button>
      </div>
    </div>
    
    <div class="form-container" v-loading="formLoading">
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
              <span>部门信息</span>
            </div>
          </template>
          
          <el-form-item label="部门编号">
            <el-input v-model="departmentId" disabled />
          </el-form-item>
          
          <el-form-item label="部门名称" prop="name">
            <el-input v-model="form.name" placeholder="请输入部门名称" />
          </el-form-item>
          
          <el-form-item label="部门描述" prop="description">
            <el-input
              v-model="form.description"
              type="textarea"
              :rows="3"
              placeholder="请输入部门描述"
            />
          </el-form-item>
        </el-card>
      </el-form>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { ElMessage, type FormInstance } from 'element-plus'
import { useDepartmentsStore } from '@/stores/departments'

// 路由
const router = useRouter()
const route = useRoute()

// 部门ID
const departmentId = ref('')

// Store
const departmentsStore = useDepartmentsStore()

// 表单引用
const formRef = ref<FormInstance>()

// 表单数据
const form = reactive({
  name: '',
  description: ''
})

// 表单验证规则
const rules = {
  name: [
    { required: true, message: '请输入部门名称', trigger: 'blur' }
  ]
}

// 加载状态
const loading = ref(false)
const formLoading = ref(false)

// 返回
const goBack = () => {
  router.go(-1)
}

// 获取部门数据
const fetchDepartment = async () => {
  formLoading.value = true
  
  try {
    const id = parseInt(route.params.id as string)
    departmentId.value = id.toString()
    
    const departmentData = await departmentsStore.getDepartment(id)
    
    // 填充表单
    form.name = departmentData.name
    form.description = departmentData.description || ''
  } catch (error: any) {
    ElMessage.error(`获取部门数据失败: ${error.message || '未知错误'}`)
  } finally {
    formLoading.value = false
  }
}

// 提交表单
const handleSubmit = async () => {
  if (!formRef.value) return
  
  await formRef.value.validate(async (valid) => {
    if (valid) {
      loading.value = true
      
      try {
        const id = parseInt(route.params.id as string)
        
        // 准备要发送的数据
        const departmentData = {
          name: form.name,
          description: form.description
        }
        
        // 调用 store 中的更新部门方法
        await departmentsStore.updateDepartment(id, departmentData)
        
        ElMessage.success('部门更新成功')
        router.push('/department/list')
      } catch (error: any) {
        ElMessage.error(`更新失败: ${error.message || '未知错误'}`)
      } finally {
        loading.value = false
      }
    }
  })
}

// 初始化
onMounted(() => {
  fetchDepartment()
})
</script>

<style scoped lang="scss">
.department-edit {
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