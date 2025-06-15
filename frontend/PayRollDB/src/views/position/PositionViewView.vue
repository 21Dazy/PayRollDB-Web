<template>
  <div class="position-view">
    <div class="page-header">
      <h2>职位详情</h2>
      <div class="page-actions">
        <el-button @click="goBack">返回</el-button>
        <el-button type="primary" @click="handleEdit">编辑</el-button>
      </div>
    </div>
    
    <div class="detail-container" v-loading="loading">
      <el-card shadow="hover" class="detail-card">
        <template #header>
          <div class="card-header">
            <span>基本信息</span>
          </div>
        </template>
        
        <el-descriptions :column="2" border>
          <el-descriptions-item label="职位编号">{{ position.id }}</el-descriptions-item>
          <el-descriptions-item label="职位名称">{{ position.name }}</el-descriptions-item>
          <el-descriptions-item label="所属部门">{{ position.departmentName }}</el-descriptions-item>
          <el-descriptions-item label="员工数量">{{ employeeCount }}</el-descriptions-item>
          <el-descriptions-item label="薪资范围">{{ salaryRange }}</el-descriptions-item>
          <el-descriptions-item label="创建时间">{{ formatDate(position.created_at) }}</el-descriptions-item>
          <el-descriptions-item label="更新时间">{{ formatDate(position.updated_at) }}</el-descriptions-item>
          <el-descriptions-item label="职位描述" :span="2">{{ position.description || '暂无描述' }}</el-descriptions-item>
        </el-descriptions>
      </el-card>
      
      <el-card shadow="hover" class="detail-card">
        <template #header>
          <div class="card-header">
            <span>员工列表</span>
          </div>
        </template>
        
        <el-table
          :data="employees"
          style="width: 100%"
          v-loading="employeesLoading"
        >
          <el-table-column prop="id" label="工号" width="100" />
          <el-table-column prop="name" label="姓名" width="120" />
          <el-table-column prop="departmentName" label="部门" width="120" />
          <el-table-column prop="phone" label="联系电话" width="150" />
          <el-table-column prop="entryDate" label="入职日期" width="120" />
          <el-table-column prop="status" label="状态" width="100">
            <template #default="{ row }">
              <el-tag :type="row.status ? 'success' : 'danger'">
                {{ row.status ? '在职' : '离职' }}
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column label="操作" width="120">
            <template #default="{ row }">
              <el-button link type="primary" size="small" @click="viewEmployee(row)">查看</el-button>
            </template>
          </el-table-column>
        </el-table>
      </el-card>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted, computed } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { ElMessage } from 'element-plus'
import { usePositionsStore } from '@/stores/positions'
import { useEmployeesStore } from '@/stores/employees'
import { useDepartmentsStore } from '@/stores/departments'

// 路由
const router = useRouter()
const route = useRoute()

// Store
const positionsStore = usePositionsStore()
const employeesStore = useEmployeesStore()
const departmentsStore = useDepartmentsStore()

// 职位数据
const position = reactive({
  id: '',
  name: '',
  description: '',
  department_id: '',
  departmentName: '',
  salary_range_min: undefined,
  salary_range_max: undefined,
  created_at: '',
  updated_at: ''
})

// 员工数据
const employees = ref([])
const employeeCount = ref(0)

// 薪资范围格式化
const salaryRange = computed(() => {
  const min = position.salary_range_min
  const max = position.salary_range_max
  
  if (!min && !max) return '-'
  if (min && !max) return `¥${min.toFixed(2)} 以上`
  if (!min && max) return `¥${max.toFixed(2)} 以下`
  return `¥${min.toFixed(2)} ~ ¥${max.toFixed(2)}`
})

// 加载状态
const loading = ref(false)
const employeesLoading = ref(false)

// 格式化日期
const formatDate = (dateStr: string) => {
  if (!dateStr) return '-'
  const date = new Date(dateStr)
  return date.toLocaleString('zh-CN', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit'
  })
}

// 返回
const goBack = () => {
  router.go(-1)
}

// 编辑
const handleEdit = () => {
  router.push(`/position/edit/${position.id}`)
}

// 查看员工
const viewEmployee = (employee) => {
  router.push(`/employee/view/${employee.id}`)
}

// 获取职位数据
const fetchPosition = async () => {
  loading.value = true
  
  try {
    const id = parseInt(route.params.id as string)
    
    // 获取部门数据
    await departmentsStore.getDepartments()
    
    // 获取职位数据
    const positionData = await positionsStore.getPosition(id)
    
    // 填充数据
    Object.assign(position, positionData)
    
    // 获取部门名称
    const department = departmentsStore.departments.find(d => d.id === position.department_id)
    position.departmentName = department ? department.name : '-'
  } catch (error: any) {
    ElMessage.error(`获取职位数据失败: ${error.message || '未知错误'}`)
  } finally {
    loading.value = false
  }
}

// 获取职位员工
const fetchPositionEmployees = async () => {
  employeesLoading.value = true
  
  try {
    const id = parseInt(route.params.id as string)
    
    // 获取职位员工列表
    const response = await employeesStore.getEmployees({ position_id: id })
    
    // 格式化员工数据
    employees.value = response.map(emp => ({
      id: emp.id,
      name: emp.name,
      departmentName: emp.department?.name || '-',
      phone: emp.phone,
      entryDate: emp.entry_date,
      status: emp.status
    }))
    
    employeeCount.value = employees.value.length
  } catch (error: any) {
    ElMessage.error(`获取职位员工失败: ${error.message || '未知错误'}`)
  } finally {
    employeesLoading.value = false
  }
}

// 初始化
onMounted(async () => {
  await fetchPosition()
  await fetchPositionEmployees()
})
</script>

<style scoped lang="scss">
.position-view {
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
  
  .detail-container {
    .detail-card {
      margin-bottom: 20px;
      
      .card-header {
        font-weight: bold;
      }
    }
  }
}
</style> 