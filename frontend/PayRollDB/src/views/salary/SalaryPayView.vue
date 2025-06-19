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
          <el-select v-model="filterForm.departmentId" placeholder="请选择部门" clearable @change="$forceUpdate()" class="custom-select">
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
        <el-table-column prop="overtimePay" label="加班费" width="100">
          <template #default="{ row }">
            {{ formatCurrency(row.overtimePay) }}
          </template>
        </el-table-column>
        <el-table-column prop="bonus" label="奖金" width="100">
          <template #default="{ row }">
            {{ formatCurrency(row.bonus) }}
          </template>
        </el-table-column>
        <el-table-column prop="performanceBonus" label="绩效奖金" width="100">
          <template #default="{ row }">
            {{ formatCurrency(row.performanceBonus) }}
          </template>
        </el-table-column>
        <el-table-column prop="attendanceBonus" label="全勤奖" width="100">
          <template #default="{ row }">
            {{ formatCurrency(row.attendanceBonus) }}
          </template>
        </el-table-column>
        <el-table-column prop="transportationAllowance" label="交通补贴" width="100">
          <template #default="{ row }">
            {{ formatCurrency(row.transportationAllowance) }}
          </template>
        </el-table-column>
        <el-table-column prop="mealAllowance" label="餐补" width="100">
          <template #default="{ row }">
            {{ formatCurrency(row.mealAllowance) }}
          </template>
        </el-table-column>
        <el-table-column prop="deduction" label="扣款" width="100">
          <template #default="{ row }">
            {{ formatCurrency(row.deduction) }}
          </template>
        </el-table-column>
        <el-table-column prop="lateDeduction" label="迟到扣款" width="100">
          <template #default="{ row }">
            {{ formatCurrency(row.lateDeduction) }}
          </template>
        </el-table-column>
        <el-table-column prop="absenceDeduction" label="缺勤扣款" width="100">
          <template #default="{ row }">
            {{ formatCurrency(row.absenceDeduction) }}
          </template>
        </el-table-column>
        <el-table-column prop="socialSecurity" label="社保公积金" width="120">
          <template #default="{ row }">
            {{ formatCurrency(row.socialSecurity) }}
          </template>
        </el-table-column>
        <el-table-column prop="personalTax" label="个税" width="100">
          <template #default="{ row }">
            {{ formatCurrency(row.personalTax) }}
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
import { useSalariesStore, type SalaryRecord } from '@/stores/salaries'
import { useDepartmentsStore } from '@/stores/departments'

const salariesStore = useSalariesStore()
const departmentsStore = useDepartmentsStore()

// 部门选项
const departmentOptions = computed(() => {
  return departmentsStore.departments.map(dept => ({
    value: dept.id,
    label: dept.name
  }))
})

// 筛选表单
const filterForm = reactive({
  yearMonth: new Date().toISOString().slice(0, 7), // 当前年月 YYYY-MM
  departmentId: ''
})

// 表格数据
const tableData = computed<SalaryRecord[]>(() => {
  return salariesStore.salaryRecords.filter(record => record.status === 'pending')
})

// 选中的行
const selectedRows = ref<SalaryRecord[]>([])

// 加载状态
const loading = computed(() => salariesStore.isLoading)

// 处理选择变更
const handleSelectionChange = (rows: SalaryRecord[]) => {
  selectedRows.value = rows
}

// 获取薪资数据
const fetchData = async () => {
  const [year, month] = filterForm.yearMonth.split('-')
  
  try {
    // 构建查询参数
    const params = {
      year: Number(year),
      month: Number(month),
      department_id: filterForm.departmentId ? Number(filterForm.departmentId) : undefined,
      status: 'pending' // 只获取待发放的薪资记录
    }
    
    // 调用store方法获取数据
    await salariesStore.getSalaryRecordsForDisplay(params)
  } catch (error) {
    console.error('获取薪资数据失败:', error)
    ElMessage.error('获取薪资数据失败')
  }
}

// 格式化货币
const formatCurrency = (value: number | undefined | null): string => {
  if (value === undefined || value === null) return '¥0.00'
  return `¥${Number(value).toFixed(2)}`
}

// 掩码银行账号
const maskBankAccount = (account: string | undefined): string => {
  if (!account) return ''
  return account.replace(/^(\d{6})(\d+)(\d{4})$/, '$1****$3')
}

// 处理筛选
const handleFilter = () => {
  fetchData()
}

// 处理单个发放
const handlePay = (row: SalaryRecord) => {
  ElMessageBox.confirm(
    `确定要向 ${row.employeeName} 发放工资 ${formatCurrency(row.netSalary)} 吗？`,
    '工资发放确认',
    {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning',
    }
  ).then(async () => {
    try {
      await salariesStore.paySalary(row.id)
      ElMessage.success(`已成功向 ${row.employeeName} 发放工资`)
      updatePaymentSummary()
      // 重新获取待发放数据
      fetchData()
    } catch (error) {
      console.error('发放工资失败:', error)
      ElMessage.error('发放工资失败')
    }
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
  
  // 计算总金额时确保处理undefined的情况
  const totalAmount = pendingRows.reduce((sum, row) => {
    const netSalary = row.netSalary || 0;
    return sum + netSalary;
  }, 0)
  
  ElMessageBox.confirm(
    `确定要向 ${pendingRows.length} 名员工发放工资，总计 ${formatCurrency(totalAmount)} 吗？`,
    '批量发放确认',
    {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning',
    }
  ).then(async () => {
    try {
      // 调用批量发放API
      const recordIds = pendingRows.map(row => row.id)
      await salariesStore.batchPaySalaries(recordIds)
      
      ElMessage.success(`已成功向 ${pendingRows.length} 名员工发放工资`)
      // 更新摘要信息
      updatePaymentSummary()
      // 重新获取待发放数据
      fetchData()
    } catch (error) {
      console.error('批量发放工资失败:', error)
      ElMessage.error('批量发放工资失败')
    }
  }).catch(() => {
    ElMessage.info('已取消发放')
  })
}

// 薪资发放摘要
const paymentSummary = reactive({
  yearMonth: '',
  employeeCount: 0,
  totalAmount: 0,
  status: 'pending' as 'pending' | 'paid'
})

// 更新薪资发放摘要
const updatePaymentSummary = () => {
  const [year, month] = filterForm.yearMonth.split('-')
  paymentSummary.yearMonth = `${year}年${month}月`
  paymentSummary.employeeCount = tableData.value.length
  
  // 计算总金额时确保处理undefined的情况
  paymentSummary.totalAmount = tableData.value.reduce((sum, row) => {
    const netSalary = row.netSalary || 0;
    return sum + netSalary;
  }, 0)
  
  // 如果所有记录都已发放，则状态为已发放
  const pendingCount = salariesStore.salaryRecords.filter(row => 
    row.status === 'pending' && 
    row.year === Number(year) && 
    row.month === Number(month)
  ).length
  
  paymentSummary.status = pendingCount === 0 ? 'paid' : 'pending'
}

// 初始化
onMounted(async () => {
  try {
    // 获取部门数据
    await departmentsStore.getDepartments()
    // 获取薪资数据
    await fetchData()
    // 更新薪资发放摘要
    updatePaymentSummary()
  } catch (error) {
    console.error('初始化数据失败:', error)
  }
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
    
    .custom-select {
      min-width: 120px;
      width: 100%;
    }
    
    :deep(.el-select) {
      width: 120px;
    }
    
    :deep(.el-select .el-input__wrapper) {
      width: 100%;
    }
    
    :deep(.el-select .el-input__inner) {
      width: 100%;
    }
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