<template>
  <div class="department-add">
    <div class="page-header">
      <h2>添加部门</h2>
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
              <span>部门信息</span>
            </div>
          </template>
          
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
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, type FormInstance } from 'element-plus'
import { useDepartmentsStore } from '@/stores/departments'

// 路由
const router = useRouter()

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

// 返回
const goBack = () => {
  router.go(-1)
}

// 提交表单
const handleSubmit = async () => {
  if (!formRef.value) return
  
  await formRef.value.validate(async (valid) => {
    if (valid) {
      loading.value = true
      
      try {
        // 准备要发送的数据
        const departmentData = {
          name: form.name,
          description: form.description
        }
        
        // 调用 store 中的创建部门方法
        await departmentsStore.createDepartment(departmentData)
        
        ElMessage.success('部门添加成功')
        router.push('/department/list')
      } catch (error: any) {
        ElMessage.error(`添加失败: ${error.message || '未知错误'}`)
      } finally {
        loading.value = false
      }
    }
  })
}
</script>

<style scoped lang="scss">
.department-add {
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