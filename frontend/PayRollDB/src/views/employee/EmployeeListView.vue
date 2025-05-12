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
        <el-form-item label="工号">
          <el-input v-model="searchForm.employeeId" placeholder="请输入工号" clearable />
        </el-form-item>
        <el-form-item label="姓名">
          <el-input v-model="searchForm.name" placeholder="请输入姓名" clearable />
        </el-form-item>
        <el-form-item label="部门">
          <el-select v-model="searchForm.departmentId" placeholder="请选择部门" clearable>
            <el-option
              v-for="item in departmentOptions"
              :key="item.value"
              :label="item.label"
              :value="item.value"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="职位">
          <el-select v-model="searchForm.positionId" placeholder="请选择职位" clearable>
            <el-option
              v-for="item in positionOptions"
              :key="item.value"
              :label="item.label"
              :value="item.value"
            />
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
import { ref, reactive, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus, Search, Refresh, Upload, Download } from '@element-plus/icons-vue'

const router = useRouter()

// 搜索表单
const searchForm = reactive({
  employeeId: '',
  name: '',
  departmentId: '',
  positionId: '',
  hireDateRange: []
})

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

// 表格数据
const tableData = ref([
  {
    id: 1,
    employeeId: 'EMP001',
    name: '张三',
    departmentName: '研发部',
    positionName: '工程师',
    baseSalary: 15000,
    hireDate: '2020-01-01',
    phone: '13800138000',
    status: 1
  },
  {
    id: 2,
    employeeId: 'EMP002',
    name: '李四',
    departmentName: '市场部',
    positionName: '经理',
    baseSalary: 18000,
    hireDate: '2019-05-10',
    phone: '13800138001',
    status: 1
  },
  {
    id: 3,
    employeeId: 'EMP003',
    name: '王五',
    departmentName: '销售部',
    positionName: '专员',
    baseSalary: 12000,
    hireDate: '2021-03-15',
    phone: '13800138002',
    status: 0
  }
])

// 分页
const currentPage = ref(1)
const pageSize = ref(10)
const total = ref(100)

// 加载状态
const loading = ref(false)

// 获取员工列表数据
const fetchData = () => {
  loading.value = true
  
  // 这里使用了模拟数据，实际项目中会调用API
  setTimeout(() => {
    loading.value = false
    // 假设这里是API返回的结果
  }, 500)
}

// 处理查询
const handleSearch = () => {
  currentPage.value = 1
  fetchData()
}

// 处理重置
const handleReset = () => {
  Object.keys(searchForm).forEach(key => {
    searchForm[key] = ''
  })
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
  ElMessage.info('导入功能待实现')
}

// 导出员工
const handleExport = () => {
  ElMessage.info('导出功能待实现')
}

// 查看员工
const handleView = (row) => {
  ElMessage.info(`查看员工：${row.name}`)
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
  ).then(() => {
    ElMessage.success(`删除成功：${row.name}`)
    fetchData()
  }).catch(() => {
    ElMessage.info('已取消删除')
  })
}

// 查看员工工资
const handleSalary = (row) => {
  router.push(`/salary/detail/${row.id}`)
}

onMounted(() => {
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