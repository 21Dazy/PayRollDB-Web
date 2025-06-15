<template>
  <div class="position-add">
    <div class="page-header">
      <h2>添加职位</h2>
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
              <span>职位信息</span>
            </div>
          </template>
          
          <el-form-item label="职位名称" prop="name">
            <el-input v-model="form.name" placeholder="请输入职位名称" />
          </el-form-item>
          
          <el-form-item label="所属部门" prop="departmentId">
            <el-select v-model="form.departmentId" placeholder="请选择部门" style="width: 100%">
              <el-option
                v-for="item in departmentOptions"
                :key="item.value"
                :label="item.label"
                :value="item.value"
              />
            </el-select>
          </el-form-item>
          
          <el-form-item label="薪资范围">
            <el-row :gutter="10">
              <el-col :span="11">
                <el-form-item prop="salaryRangeMin">
                  <el-input-number
                    v-model="form.salaryRangeMin"
                    :min="0"
                    :precision="2"
                    :step="1000"
                    style="width: 100%"
                    placeholder="最低薪资"
                  />
                </el-form-item>
              </el-col>
              <el-col :span="2" class="text-center">
                <span>至</span>
              </el-col>
              <el-col :span="11">
                <el-form-item prop="salaryRangeMax">
                  <el-input-number
                    v-model="form.salaryRangeMax"
                    :min="0"
                    :precision="2"
                    :step="1000"
                    style="width: 100%"
                    placeholder="最高薪资"
                  />
                </el-form-item>
              </el-col>
            </el-row>
          </el-form-item>
          
          <el-form-item label="职位描述" prop="description">
            <el-input
              v-model="form.description"
              type="textarea"
              :rows="3"
              placeholder="请输入职位描述"
            />
          </el-form-item>
        </el-card>
      </el-form>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted, computed } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, type FormInstance } from 'element-plus'
import { usePositionsStore } from '@/stores/positions'
import { useDepartmentsStore } from '@/stores/departments'

// 路由
const router = useRouter()

// Store
const positionsStore = usePositionsStore()
const departmentsStore = useDepartmentsStore()

// 表单引用
const formRef = ref<FormInstance>()

// 部门选项
const departmentOptions = computed(() => {
  return (departmentsStore.departments || []).map(dept => ({
    value: dept.id,
    label: dept.name
  }))
})

// 表单数据
const form = reactive({
  name: '',
  departmentId: '',
  salaryRangeMin: undefined,
  salaryRangeMax: undefined,
  description: ''
})

// 表单验证规则
const rules = {
  name: [
    { required: true, message: '请输入职位名称', trigger: 'blur' }
  ],
  departmentId: [
    { required: true, message: '请选择所属部门', trigger: 'change' }
  ],
  salaryRangeMax: [
    { 
      validator: (rule, value, callback) => {
        if (form.salaryRangeMin !== undefined && value !== undefined && value < form.salaryRangeMin) {
          callback(new Error('最高薪资不能低于最低薪资'))
        } else {
          callback()
        }
      }, 
      trigger: 'change' 
    }
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
        const positionData = {
          name: form.name,
          department_id: parseInt(form.departmentId),
          description: form.description || undefined
        }
        
        // 调用 store 中的创建职位方法
        await positionsStore.createPosition(positionData)
        
        ElMessage.success('职位添加成功')
        router.push('/position/list')
      } catch (error: any) {
        ElMessage.error(`添加失败: ${error.message || '未知错误'}`)
      } finally {
        loading.value = false
      }
    }
  })
}

// 初始化
onMounted(async () => {
  try {
    await departmentsStore.getDepartments()
  } catch (error: any) {
    ElMessage.error(`获取部门数据失败: ${error.message || '未知错误'}`)
  }
})
</script>

<style scoped lang="scss">
.position-add {
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
  
  .text-center {
    display: flex;
    justify-content: center;
    align-items: center;
    height: 32px;
  }
}
</style> 