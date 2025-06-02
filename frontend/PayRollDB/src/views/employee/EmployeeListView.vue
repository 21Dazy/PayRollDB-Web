<template>
  <div class="employee-list">
    <div class="page-header">
      <h2>员工列表</h2>
      <div class="page-actions">
        <el-button type="primary" :icon="Plus" @click="handleAdd">添加员工</el-button>
        <el-button :icon="Upload" @click="handleImport">批量导入</el-button>
        <el-button :icon="Download" @click="handleExport">批量导出</el-button>
      </div>
    </div>
    
    <div class="search-bar">
      <el-form :inline="true" :model="searchForm" class="search-form">
        <el-form-item label="关键词">
          <el-input v-model="searchForm.keyword" placeholder="工号/姓名/电话" clearable />
        </el-form-item>
        <el-form-item label="部门">
          <el-select v-model="searchForm.department_id" placeholder="请选择部门" clearable>
            <el-option
              v-for="item in departmentOptions"
              :key="item.value"
              :label="item.label"
              :value="item.value"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="职位">
          <el-select v-model="searchForm.position_id" placeholder="请选择职位" clearable>
            <el-option
              v-for="item in positionOptions"
              :key="item.value"
              :label="item.label"
              :value="item.value"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="状态">
          <el-select v-model="searchForm.status" placeholder="请选择状态" clearable>
            <el-option value="active" label="在职" />
            <el-option value="inactive" label="离职" />
          </el-select>
        </el-form-item>
        <el-form-item label="入职日期">
          <el-date-picker
            v-model="searchForm.hireDateRange"
            type="daterange"
            range-separator="至"
            start-placeholder="开始日期"
            end-placeholder="结束日期"
          />
        </el-form-item>
        <el-form-item>
          <el-button type="primary" :icon="Search" @click="handleSearch">查询</el-button>
          <el-button :icon="Refresh" @click="handleReset">重置</el-button>
        </el-form-item>
      </el-form>
    </div>
    
    <div class="data-table">
      <el-table
        :data="tableData"
        style="width: 100%"
        border
        stripe
        v-loading="loading"
      >
        <el-table-column type="selection" width="55" />
        <el-table-column prop="employeeId" label="工号" width="100" />
        <el-table-column prop="name" label="姓名" width="120" />
        <el-table-column prop="departmentName" label="部门" width="120" />
        <el-table-column prop="positionName" label="职位" width="120" />
        <el-table-column prop="baseSalary" label="基本工资" width="120">
          <template #default="{ row }">
            {{ formatCurrency(row.baseSalary) }}
          </template>
        </el-table-column>
        <el-table-column prop="hireDate" label="入职日期" width="120" />
        <el-table-column prop="phone" label="联系电话" width="150" />
        <el-table-column prop="status" label="状态" width="100">
          <template #default="{ row }">
            <el-tag :type="row.status === 1 ? 'success' : 'danger'">
              {{ row.status === 1 ? '在职' : '离职' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column fixed="right" label="操作" width="220">
          <template #default="{ row }">
            <el-button link type="primary" size="small" @click="handleView(row)">查看</el-button>
            <el-button link type="primary" size="small" @click="handleEdit(row)">编辑</el-button>
            <el-button link type="danger" size="small" @click="handleDelete(row)">删除</el-button>
            <el-button link type="warning" size="small" @click="handleSalary(row)">工资</el-button>
          </template>
        </el-table-column>
      </el-table>
    </div>
    
    <div class="pagination">
      <el-pagination
        v-model:current-page="currentPage"
        v-model:page-size="pageSize"
        :page-sizes="[10, 20, 50, 100]"
        layout="total, sizes, prev, pager, next, jumper"
        :total="total"
        @size-change="handleSizeChange"
        @current-change="handleCurrentChange"
      />
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted, computed, watch } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus, Search, Refresh, Upload, Download } from '@element-plus/icons-vue'
import { useEmployeesStore } from '@/stores/employees'
import { useDepartmentsStore } from '@/stores/departments'
import { usePositionsStore } from '@/stores/positions'

const router = useRouter()

// 引入stores
const employeesStore = useEmployeesStore()
const departmentsStore = useDepartmentsStore()
const positionsStore = usePositionsStore()

// 搜索表单
const searchForm = reactive({
  keyword: '',
  department_id: '',
  position_id: '',
  status: '',
  hireDateRange: []
})

// 部门选项
const departmentOptions = computed(() => {
  return departmentsStore.departments.map(dept => ({
    value: dept.id,
    label: dept.name
  }))
})

// 职位选项
const positionOptions = computed(() => {
  return positionsStore.positions.map(pos => ({
    value: pos.id,
    label: pos.name
  }))
})

// 表格数据
const tableData = computed(() => {
  return employeesStore.employees.map(emp => ({
    id: emp.id,
    employeeId: emp.id.toString().padStart(4, '0'),
    name: emp.name,
    departmentName: emp.department?.name || '-',
    positionName: emp.position?.name || '-',
    baseSalary: emp.basic_salary,
    hireDate: emp.entry_date,
    phone: emp.phone,
    status: emp.status === 'active' ? 1 : 0
  }))
})

// 分页
const currentPage = ref(1)
const pageSize = ref(10)
const total = computed(() => employeesStore.totalCount)

// 加载状态
const loading = computed(() => employeesStore.isLoading)

// 获取员工列表数据
const fetchData = () => {
  const params: any = {
    skip: (currentPage.value - 1) * pageSize.value,
    limit: pageSize.value
  }
  
  // 添加搜索条件
  if (searchForm.keyword) {
    params.keyword = searchForm.keyword
  }
  
  if (searchForm.department_id) {
    params.department_id = searchForm.department_id
  }
  
  if (searchForm.position_id) {
    params.position_id = searchForm.position_id
  }
  
  if (searchForm.status) {
    params.status = searchForm.status
  }
  
  // 入职日期范围
  if (searchForm.hireDateRange && searchForm.hireDateRange.length === 2) {
    const [start, end] = searchForm.hireDateRange
    if (start && end) {
      params.entry_date_start = start.toISOString().split('T')[0]
      params.entry_date_end = end.toISOString().split('T')[0]
    }
  }
  
  employeesStore.getEmployees(params)
}

// 处理查询
const handleSearch = () => {
  currentPage.value = 1
  fetchData()
}

// 处理重置
const handleReset = () => {
  searchForm.keyword = ''
  searchForm.department_id = ''
  searchForm.position_id = ''
  searchForm.status = ''
  searchForm.hireDateRange = []
  handleSearch()
}

// 处理分页大小改变
const handleSizeChange = (val: number) => {
  pageSize.value = val
  fetchData()
}

// 处理页码改变
const handleCurrentChange = (val: number) => {
  currentPage.value = val
  fetchData()
}

// 格式化货币
const formatCurrency = (value: number) => {
  return `¥${value.toFixed(2)}`
}

// 添加员工
const handleAdd = () => {
  router.push('/employee/add')
}

// 导入员工
const handleImport = () => {
  // 创建文件输入元素
  const input = document.createElement('input')
  input.type = 'file'
  input.accept = '.xlsx,.xls,.csv'
  
  // 文件选择事件
  input.onchange = async (event) => {
    const target = event.target as HTMLInputElement
    if (target.files && target.files.length > 0) {
      const file = target.files[0]
      
      try {
        await employeesStore.importEmployees(file)
        ElMessage.success('员工数据导入成功')
        fetchData() // 重新加载数据
      } catch (error: any) {
        ElMessage.error(`导入失败: ${error.message || '未知错误'}`)
      }
    }
  }
  
  // 触发文件选择
  input.click()
}

// 导出员工
const handleExport = async () => {
  try {
    const params: any = {}
    
    // 添加搜索条件
    if (searchForm.keyword) {
      params.keyword = searchForm.keyword
    }
    
    if (searchForm.department_id) {
      params.department_id = searchForm.department_id
    }
    
    if (searchForm.position_id) {
      params.position_id = searchForm.position_id
    }
    
    if (searchForm.status) {
      params.status = searchForm.status
    }
    
    // 入职日期范围
    if (searchForm.hireDateRange && searchForm.hireDateRange.length === 2) {
      const [start, end] = searchForm.hireDateRange
      if (start && end) {
        params.entry_date_start = start.toISOString().split('T')[0]
        params.entry_date_end = end.toISOString().split('T')[0]
      }
    }
    
    const blob = await employeesStore.exportEmployees(params)
    
    // 创建下载链接
    const url = window.URL.createObjectURL(blob)
    const link = document.createElement('a')
    link.href = url
    link.download = `员工数据_${new Date().toISOString().split('T')[0]}.xlsx`
    link.click()
    
    // 清理
    window.URL.revokeObjectURL(url)
    
  } catch (error: any) {
    ElMessage.error(`导出失败: ${error.message || '未知错误'}`)
  }
}

// 查看员工
const handleView = (row) => {
  router.push(`/employee/view/${row.id}`)
}

// 编辑员工
const handleEdit = (row) => {
  router.push(`/employee/edit/${row.id}`)
}

// 删除员工
const handleDelete = (row) => {
  ElMessageBox.confirm(
    `确定要删除员工 ${row.name} 吗？`,
    '删除确认',
    {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning',
    }
  ).then(async () => {
    try {
      await employeesStore.deleteEmployee(row.id)
      ElMessage.success('删除成功')
      fetchData() // 重新加载数据
    } catch (error: any) {
      ElMessage.error(`删除失败: ${error.message || '未知错误'}`)
    }
  }).catch(() => {
    // 取消操作
  })
}

// 工资详情
const handleSalary = (row) => {
  router.push(`/salary/employee/${row.id}`)
}

// 初始化
onMounted(async () => {
  // 获取部门和职位数据
  await Promise.all([
    departmentsStore.getDepartments(),
    positionsStore.getPositions()
  ])
  
  // 获取员工数据
  fetchData()
})

// 监听页面大小变化
watch([currentPage, pageSize], () => {
  fetchData()
})
</script>

<style scoped lang="scss">
.employee-list {
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
  
  .search-bar {
    margin-bottom: 20px;
    background-color: #fff;
    padding: 20px;
    border-radius: 4px;
    box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.04);
  }
  
  .data-table {
    background-color: #fff;
    padding: 20px;
    border-radius: 4px;
    box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.04);
    margin-bottom: 20px;
  }
  
  .pagination {
    display: flex;
    justify-content: flex-end;
    margin-top: 20px;
  }
}
</style> 