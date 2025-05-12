<template>
  <div class="salary-list">
    <div class="page-header">
      <h2>薪资列表</h2>
      <div class="page-actions">
        <el-button type="primary" :icon="Plus" @click="handleCalculate">薪资核算</el-button>
        <el-button :icon="Download" @click="handleExport">导出报表</el-button>
      </div>
    </div>
    
    <div class="search-bar">
      <el-form :inline="true" :model="searchForm" class="search-form">
        <el-form-item label="年份">
          <el-select v-model="searchForm.year" placeholder="请选择年份" clearable>
            <el-option
              v-for="item in yearOptions"
              :key="item.value"
              :label="item.label"
              :value="item.value"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="月份">
          <el-select v-model="searchForm.month" placeholder="请选择月份" clearable>
            <el-option
              v-for="item in monthOptions"
              :key="item.value"
              :label="item.label"
              :value="item.value"
            />
          </el-select>
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
        <el-form-item label="姓名/工号">
          <el-input v-model="searchForm.keyword" placeholder="请输入姓名或工号" clearable />
        </el-form-item>
        <el-form-item label="状态">
          <el-select v-model="searchForm.status" placeholder="请选择状态" clearable>
            <el-option label="待发放" value="pending" />
            <el-option label="已发放" value="paid" />
          </el-select>
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
        <el-table-column prop="year" label="年份" width="80" />
        <el-table-column prop="month" label="月份" width="80" />
        <el-table-column prop="employeeId" label="工号" width="100" />
        <el-table-column prop="employeeName" label="姓名" width="100" />
        <el-table-column prop="departmentName" label="部门" width="100" />
        <el-table-column prop="baseSalary" label="基本工资" width="120">
          <template #default="{ row }">
            {{ formatCurrency(row.baseSalary) }}
          </template>
        </el-table-column>
        <el-table-column prop="bonus" label="奖金" width="100">
          <template #default="{ row }">
            {{ formatCurrency(row.bonus) }}
          </template>
        </el-table-column>
        <el-table-column prop="deduction" label="扣款" width="100">
          <template #default="{ row }">
            {{ formatCurrency(row.deduction) }}
          </template>
        </el-table-column>
        <el-table-column prop="socialSecurity" label="社保公积金" width="120">
          <template #default="{ row }">
            {{ formatCurrency(row.socialSecurity) }}
          </template>
        </el-table-column>
        <el-table-column prop="netSalary" label="实发工资" width="120">
          <template #default="{ row }">
            {{ formatCurrency(row.netSalary) }}
          </template>
        </el-table-column>
        <el-table-column prop="status" label="状态" width="100">
          <template #default="{ row }">
            <el-tag :type="row.status === 'paid' ? 'success' : 'warning'">
              {{ row.status === 'paid' ? '已发放' : '待发放' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="paymentDate" label="发放日期" width="180" />
        <el-table-column fixed="right" label="操作" width="200">
          <template #default="{ row }">
            <el-button link type="primary" size="small" @click="handleDetail(row)">详情</el-button>
            <el-button 
              link 
              type="primary" 
              size="small" 
              @click="handlePay(row)"
              v-if="row.status === 'pending'"
            >
              发放
            </el-button>
            <el-button 
              link 
              type="danger" 
              size="small" 
              @click="handleDelete(row)"
              v-if="row.status === 'pending'"
            >
              删除
            </el-button>
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
import { Plus, Search, Refresh, Download } from '@element-plus/icons-vue'

const router = useRouter()

// 年份选项
const currentYear = new Date().getFullYear()
const yearOptions = ref([
  { value: currentYear, label: `${currentYear}年` },
  { value: currentYear - 1, label: `${currentYear - 1}年` },
  { value: currentYear - 2, label: `${currentYear - 2}年` }
])

// 月份选项
const monthOptions = ref(Array.from({ length: 12 }, (_, i) => ({
  value: i + 1,
  label: `${i + 1}月`
})))

// 部门选项
const departmentOptions = ref([
  { value: '1', label: '研发部' },
  { value: '2', label: '市场部' },
  { value: '3', label: '销售部' },
  { value: '4', label: '财务部' },
  { value: '5', label: '人事部' }
])

// 搜索表单
const searchForm = reactive({
  year: currentYear,
  month: new Date().getMonth() + 1,
  departmentId: '',
  keyword: '',
  status: ''
})

// 表格数据
const tableData = ref([])

// 分页
const currentPage = ref(1)
const pageSize = ref(10)
const total = ref(0)

// 加载状态
const loading = ref(false)

// 获取薪资列表数据
const fetchData = () => {
  loading.value = true
  
  // 这里应该是实际的API调用
  // 使用Mock数据来模拟
  setTimeout(() => {
    // 模拟API返回数据
    const mockData = []
    for (let i = 0; i < 10; i++) {
      const baseSalary = Math.floor(Math.random() * 12000) + 8000
      const bonus = Math.floor(Math.random() * 4000)
      const deduction = Math.floor(Math.random() * 1000)
      const socialSecurity = Math.floor(baseSalary * 0.2)
      const netSalary = baseSalary + bonus - deduction - socialSecurity
      
      mockData.push({
        id: i + 1,
        year: searchForm.year,
        month: searchForm.month,
        employeeId: `EMP${1000 + i}`,
        employeeName: ['张三', '李四', '王五', '赵六', '钱七'][i % 5],
        departmentName: ['研发部', '市场部', '销售部', '财务部', '人事部'][i % 5],
        baseSalary,
        bonus,
        deduction,
        socialSecurity,
        netSalary,
        status: i % 3 === 0 ? 'pending' : 'paid',
        paymentDate: i % 3 === 0 ? '' : `${searchForm.year}-${String(searchForm.month).padStart(2, '0')}-15 10:00:00`
      })
    }
    
    tableData.value = mockData
    total.value = 56 // 模拟总数
    loading.value = false
  }, 500)
}

// 格式化货币
const formatCurrency = (value) => {
  return `¥${Number(value).toFixed(2)}`
}

// 处理查询
const handleSearch = () => {
  currentPage.value = 1
  fetchData()
}

// 处理重置
const handleReset = () => {
  searchForm.year = currentYear
  searchForm.month = new Date().getMonth() + 1
  searchForm.departmentId = ''
  searchForm.keyword = ''
  searchForm.status = ''
  handleSearch()
}

// 处理分页大小改变
const handleSizeChange = (val) => {
  pageSize.value = val
  fetchData()
}

// 处理页码改变
const handleCurrentChange = (val) => {
  currentPage.value = val
  fetchData()
}

// 查看详情
const handleDetail = (row) => {
  router.push(`/salary/detail/${row.id}`)
}

// 薪资发放
const handlePay = (row) => {
  ElMessageBox.confirm(
    `确定要发放 ${row.employeeName} ${row.year}年${row.month}月的工资吗？`,
    '发放确认',
    {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning',
    }
  ).then(() => {
    // 实际应该调用API
    row.status = 'paid'
    row.paymentDate = new Date().toLocaleString('zh-CN')
    ElMessage.success(`已成功发放 ${row.employeeName} 的工资`)
  }).catch(() => {
    ElMessage.info('已取消发放')
  })
}

// 删除薪资记录
const handleDelete = (row) => {
  ElMessageBox.confirm(
    `确定要删除 ${row.employeeName} ${row.year}年${row.month}月的工资记录吗？`,
    '删除确认',
    {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning',
    }
  ).then(() => {
    // 实际应该调用API
    const index = tableData.value.findIndex(item => item.id === row.id)
    if (index !== -1) {
      tableData.value.splice(index, 1)
      total.value--
      ElMessage.success(`已删除 ${row.employeeName} 的工资记录`)
    }
  }).catch(() => {
    ElMessage.info('已取消删除')
  })
}

// 薪资核算
const handleCalculate = () => {
  ElMessageBox.confirm(
    `确定要为 ${searchForm.year}年${searchForm.month}月 进行薪资核算吗？`,
    '薪资核算',
    {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning',
    }
  ).then(() => {
    ElMessage.success(`${searchForm.year}年${searchForm.month}月薪资核算完成`)
    fetchData()
  }).catch(() => {
    ElMessage.info('已取消薪资核算')
  })
}

// 导出报表
const handleExport = () => {
  ElMessage.success('薪资报表导出成功')
}

onMounted(() => {
  fetchData()
})
</script>

<style scoped lang="scss">
.salary-list {
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