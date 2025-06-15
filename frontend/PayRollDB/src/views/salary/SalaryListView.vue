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
          <el-select v-model="searchForm.year" placeholder="请选择年份" clearable @change="$forceUpdate()" class="custom-select">
            <el-option
              v-for="item in yearOptions"
              :key="item.value"
              :label="item.label"
              :value="item.value"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="月份">
          <el-select v-model="searchForm.month" placeholder="请选择月份" clearable @change="$forceUpdate()" class="custom-select">
            <el-option
              v-for="item in monthOptions"
              :key="item.value"
              :label="item.label"
              :value="item.value"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="部门">
          <el-select v-model="searchForm.departmentId" placeholder="请选择部门" clearable @change="$forceUpdate()" class="custom-select">
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
          <el-select v-model="searchForm.status" placeholder="请选择状态" clearable @change="$forceUpdate()" class="custom-select">
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
        <el-table-column prop="paymentDate" label="发放日期" width="180">
          <template #default="{ row }">
            {{ formatPaymentDate(row.paymentDate) }}
          </template>
        </el-table-column>
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
import { ref, reactive, onMounted, computed } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus, Search, Refresh, Download } from '@element-plus/icons-vue'
import { useSalariesStore, type SalaryRecord } from '@/stores/salaries'
import { useDepartmentsStore } from '@/stores/departments'


const router = useRouter()
const salariesStore = useSalariesStore()
const departmentsStore = useDepartmentsStore()

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
const departmentOptions = computed(() => {
  return departmentsStore.departments.map(dept => ({
    value: dept.id,
    label: dept.name
  }))
})

// 搜索表单
const searchForm = reactive({
  year: currentYear,
  month: new Date().getMonth() + 1,
  departmentId: '',
  keyword: '',
  status: ''
})

// 表格数据
const tableData = computed(() => salariesStore.salaryRecords)

// 分页
const currentPage = ref(1)
const pageSize = ref(10)
const total = computed(() => salariesStore.totalCount)

// 加载状态
const loading = computed(() => salariesStore.isLoading)

// 获取薪资列表数据
const fetchData = async () => {
  try {
    // 构建查询参数
    const params = {
      year: searchForm.year,
      month: searchForm.month,
      department_id: searchForm.departmentId ? Number(searchForm.departmentId) : undefined,
      keyword: searchForm.keyword || undefined,
      status: searchForm.status || undefined,
      skip: (currentPage.value - 1) * pageSize.value,
      limit: pageSize.value
    };
    
    // 输出参数以便调试
    console.log('查询参数:', params);
    
    // 调用store方法获取数据
    await salariesStore.getSalaryRecordsForDisplay(params);
  } catch (error) {
    console.error('获取薪资数据失败:', error);
    ElMessage.error('获取薪资数据失败');
  }
}

// 格式化货币
const formatCurrency = (value: number | undefined | null): string => {
  if (value === undefined || value === null) return '¥0.00';
  return `¥${Number(value).toFixed(2)}`;
}

// 格式化发放日期
const formatPaymentDate = (dateString: string | null | undefined): string => {
  if (!dateString) return '-';
  
  try {
    const date = new Date(dateString);
    if (isNaN(date.getTime())) return '-';
    
    return date.toLocaleDateString('zh-CN', {
      year: 'numeric',
      month: '2-digit',
      day: '2-digit',
      hour: '2-digit',
      minute: '2-digit'
    });
  } catch (error) {
    console.error('日期格式化错误:', error);
    return '-';
  }
}

// 处理查询
const handleSearch = () => {
  currentPage.value = 1;
  fetchData();
}

// 处理重置
const handleReset = () => {
  searchForm.year = currentYear;
  searchForm.month = new Date().getMonth() + 1;
  searchForm.departmentId = '';
  searchForm.keyword = '';
  searchForm.status = '';
  handleSearch();
}

// 处理分页大小改变
const handleSizeChange = (val: number) => {
  pageSize.value = val;
  fetchData();
}

// 处理页码改变
const handleCurrentChange = (val: number) => {
  currentPage.value = val;
  fetchData();
}

// 查看详情
const handleDetail = (row: SalaryRecord) => {
  router.push(`/salary/detail/${row.id}`);
}

// 薪资发放
const handlePay = (row: SalaryRecord) => {
  ElMessageBox.confirm(
    `确定要发放 ${row.employeeName} ${row.year}年${row.month}月的工资吗？`,
    '发放确认',
    {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning',
    }
  ).then(async () => {
    try {
      await salariesStore.paySalary(row.id);
      ElMessage.success(`已成功发放 ${row.employeeName} 的工资`);
    } catch (error) {
      console.error('发放工资失败:', error);
      ElMessage.error('发放工资失败');
    }
  }).catch(() => {
    ElMessage.info('已取消发放');
  });
}

// 删除薪资记录
const handleDelete = (row: SalaryRecord) => {
  ElMessageBox.confirm(
    `确定要删除 ${row.employeeName} ${row.year}年${row.month}月的工资记录吗？`,
    '删除确认',
    {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning',
    }
  ).then(async () => {
    try {
      await salariesStore.deleteSalaryRecord(row.id);
      ElMessage.success(`已删除 ${row.employeeName} 的工资记录`);
    } catch (error) {
      console.error('删除工资记录失败:', error);
      ElMessage.error('删除工资记录失败');
    }
  }).catch(() => {
    ElMessage.info('已取消删除');
  });
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
  ).then(async () => {
    try {
      await salariesStore.generateSalaryRecords(
        searchForm.year, 
        searchForm.month, 
        searchForm.departmentId ? Number(searchForm.departmentId) : undefined
      );
      ElMessage.success(`${searchForm.year}年${searchForm.month}月薪资核算完成`);
      fetchData();
    } catch (error) {
      console.error('薪资核算失败:', error);
      ElMessage.error('薪资核算失败');
    }
  }).catch(() => {
    ElMessage.info('已取消薪资核算');
  });
}

// 导出报表
const handleExport = async () => {
  try {
    const params = {
      year: searchForm.year,
      month: searchForm.month,
      department_id: searchForm.departmentId ? Number(searchForm.departmentId) : undefined,
      keyword: searchForm.keyword || undefined,
      status: searchForm.status || undefined
    };
    
    const response = await salariesStore.exportSalaryRecords(params);
    
    // 处理二进制文件下载
    const blob = new Blob([response], { type: 'application/vnd.ms-excel' });
    const link = document.createElement('a');
    link.href = URL.createObjectURL(blob);
    link.download = `薪资报表_${searchForm.year}年${searchForm.month}月.xlsx`;
    link.click();
    URL.revokeObjectURL(link.href);
    
    ElMessage.success('薪资报表导出成功');
  } catch (error) {
    console.error('导出报表失败:', error);
    ElMessage.error('导出报表失败');
  }
}

// 初始化
onMounted(async () => {
  try {
    // 获取部门数据
    await departmentsStore.getDepartments();
    // 获取薪资数据
    await fetchData();
  } catch (error) {
    console.error('初始化数据失败:', error);
  }
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