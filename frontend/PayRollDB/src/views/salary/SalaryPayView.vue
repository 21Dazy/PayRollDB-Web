<template>
  <div class="salary-pay">
    <div class="page-header">
      <h2>薪资发放</h2>
      <div class="page-actions">
        <el-button type="primary" :icon="Check" @click="handlePayAll" :loading="loading">批量发放</el-button>
      </div>
    </div>
    
    <div class="filter-bar">
      <el-form :inline="true" :model="filterForm">
        <el-form-item label="发放年月">
          <el-date-picker
            v-model="filterForm.yearMonth"
            type="month"
            placeholder="选择年月"
            format="YYYY年MM月"
            value-format="YYYY-MM"
          />
        </el-form-item>
        <el-form-item label="部门">
          <el-select v-model="filterForm.departmentId" placeholder="请选择部门" clearable>
            <el-option
              v-for="item in departmentOptions"
              :key="item.value"
              :label="item.label"
              :value="item.value"
            />
          </el-select>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" :icon="Search" @click="handleFilter">筛选</el-button>
        </el-form-item>
      </el-form>
    </div>
    
    <div class="summary-card">
      <el-card shadow="hover">
        <template #header>
          <div class="card-header">
            <span>薪资发放摘要</span>
          </div>
        </template>
        <el-descriptions :column="4" border>
          <el-descriptions-item label="发放年月">{{ paymentSummary.yearMonth }}</el-descriptions-item>
          <el-descriptions-item label="发放人数">{{ paymentSummary.employeeCount }}人</el-descriptions-item>
          <el-descriptions-item label="总计金额">{{ formatCurrency(paymentSummary.totalAmount) }}</el-descriptions-item>
          <el-descriptions-item label="状态">
            <el-tag :type="paymentSummary.status === 'pending' ? 'warning' : 'success'">
              {{ paymentSummary.status === 'pending' ? '未发放' : '已发放' }}
            </el-tag>
          </el-descriptions-item>
        </el-descriptions>
      </el-card>
    </div>
    
    <div class="data-table">
      <el-table
        :data="tableData"
        style="width: 100%"
        border
        stripe
        v-loading="loading"
        @selection-change="handleSelectionChange"
      >
        <el-table-column type="selection" width="55" />
        <el-table-column prop="employeeId" label="工号" width="100" />
        <el-table-column prop="employeeName" label="姓名" width="100" />
        <el-table-column prop="departmentName" label="部门" width="100" />
        <el-table-column prop="bankName" label="开户银行" width="120" />
        <el-table-column prop="bankAccount" label="银行账号" width="180">
          <template #default="{ row }">
            {{ maskBankAccount(row.bankAccount) }}
          </template>
        </el-table-column>
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
        <el-table-column label="操作" width="120">
          <template #default="{ row }">
            <el-button 
              link 
              type="primary" 
              size="small" 
              @click="handlePay(row)"
              :disabled="row.status === 'paid'"
            >
              发放
            </el-button>
          </template>
        </el-table-column>
      </el-table>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Check, Search } from '@element-plus/icons-vue'

// 部门选项
const departmentOptions = ref([
  { value: '1', label: '研发部' },
  { value: '2', label: '市场部' },
  { value: '3', label: '销售部' },
  { value: '4', label: '财务部' },
  { value: '5', label: '人事部' }
])

// 筛选表单
const filterForm = reactive({
  yearMonth: new Date().toISOString().slice(0, 7), // 当前年月 YYYY-MM
  departmentId: ''
})

// 表格数据
const tableData = ref([])

// 选中的行
const selectedRows = ref([])

// 加载状态
const loading = ref(false)

// 处理选择变更
const handleSelectionChange = (rows) => {
  selectedRows.value = rows
}

// 模拟获取数据
const fetchData = () => {
  loading.value = true
  
  setTimeout(() => {
    // 模拟API返回数据
    const mockData = []
    const [year, month] = filterForm.yearMonth.split('-')
    
    for (let i = 0; i < 10; i++) {
      const baseSalary = Math.floor(Math.random() * 12000) + 8000
      const bonus = Math.floor(Math.random() * 4000)
      const deduction = Math.floor(Math.random() * 1000)
      const netSalary = baseSalary + bonus - deduction
      
      mockData.push({
        id: i + 1,
        employeeId: `EMP${1000 + i}`,
        employeeName: ['张三', '李四', '王五', '赵六', '钱七'][i % 5],
        departmentName: ['研发部', '市场部', '销售部', '财务部', '人事部'][i % 5],
        departmentId: (i % 5 + 1).toString(),
        bankName: ['中国银行', '工商银行', '建设银行', '农业银行', '招商银行'][i % 5],
        bankAccount: `622202${Math.floor(10000000000000 + Math.random() * 90000000000000)}`,
        baseSalary,
        bonus,
        deduction,
        netSalary,
        status: i % 3 === 0 ? 'pending' : 'paid'
      })
    }
    
    // 根据部门筛选
    if (filterForm.departmentId) {
      tableData.value = mockData.filter(item => item.departmentId === filterForm.departmentId)
    } else {
      tableData.value = mockData
    }
    
    loading.value = false
  }, 500)
}

// 格式化货币
const formatCurrency = (value) => {
  return `¥${Number(value).toFixed(2)}`
}

// 掩码银行账号
const maskBankAccount = (account) => {
  if (!account) return ''
  return account.replace(/^(\d{6})(\d+)(\d{4})$/, '$1****$3')
}

// 处理筛选
const handleFilter = () => {
  fetchData()
}

// 处理单个发放
const handlePay = (row) => {
  ElMessageBox.confirm(
    `确定要向 ${row.employeeName} 发放工资 ${formatCurrency(row.netSalary)} 吗？`,
    '工资发放确认',
    {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning',
    }
  ).then(() => {
    // 实际项目中应该调用API
    row.status = 'paid'
    ElMessage.success(`已成功向 ${row.employeeName} 发放工资`)
    updatePaymentSummary()
  }).catch(() => {
    ElMessage.info('已取消发放')
  })
}

// 处理批量发放
const handlePayAll = () => {
  const pendingRows = selectedRows.value.filter(row => row.status === 'pending')
  
  if (pendingRows.length === 0) {
    ElMessage.warning('没有选中待发放的工资记录')
    return
  }
  
  const totalAmount = pendingRows.reduce((sum, row) => sum + row.netSalary, 0)
  
  ElMessageBox.confirm(
    `确定要向 ${pendingRows.length} 名员工发放工资，总计 ${formatCurrency(totalAmount)} 吗？`,
    '批量发放确认',
    {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning',
    }
  ).then(() => {
    loading.value = true
    
    // 实际项目中应该调用API
    setTimeout(() => {
      pendingRows.forEach(row => {
        row.status = 'paid'
      })
      
      loading.value = false
      ElMessage.success(`已成功向 ${pendingRows.length} 名员工发放工资`)
      updatePaymentSummary()
    }, 1000)
  }).catch(() => {
    ElMessage.info('已取消发放')
  })
}

// 薪资发放摘要
const paymentSummary = reactive({
  yearMonth: '',
  employeeCount: 0,
  totalAmount: 0,
  status: 'pending'
})

// 更新薪资发放摘要
const updatePaymentSummary = () => {
  const [year, month] = filterForm.yearMonth.split('-')
  paymentSummary.yearMonth = `${year}年${month}月`
  paymentSummary.employeeCount = tableData.value.length
  paymentSummary.totalAmount = tableData.value.reduce((sum, row) => sum + row.netSalary, 0)
  
  // 如果所有记录都已发放，则状态为已发放
  const allPaid = tableData.value.every(row => row.status === 'paid')
  paymentSummary.status = allPaid ? 'paid' : 'pending'
}

onMounted(() => {
  fetchData()
  updatePaymentSummary()
})
</script>

<style scoped lang="scss">
.salary-pay {
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
  
  .filter-bar {
    margin-bottom: 20px;
    background-color: #fff;
    padding: 20px;
    border-radius: 4px;
    box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.04);
  }
  
  .summary-card {
    margin-bottom: 20px;
    
    .card-header {
      font-weight: bold;
    }
  }
  
  .data-table {
    background-color: #fff;
    padding: 20px;
    border-radius: 4px;
    box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.04);
    margin-bottom: 20px;
  }
}
</style> 