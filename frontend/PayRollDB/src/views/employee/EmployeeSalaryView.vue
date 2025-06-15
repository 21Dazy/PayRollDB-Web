<template>
  <div class="employee-salary">
    <div class="page-header">
      <h2>员工工资明细</h2>
      <div class="page-actions">
        <el-button @click="goBack">返回</el-button>
      </div>
    </div>
    
    <div v-loading="employeeLoading">
      <!-- 员工基本信息卡片 -->
      <el-card shadow="hover" class="info-card" v-if="employeeInfo">
        <template #header>
          <div class="card-header">
            <span>员工基本信息</span>
          </div>
        </template>
        
        <el-descriptions :column="3" border>
          <el-descriptions-item label="工号">
            {{ String(employeeInfo.id).padStart(4, '0') }}
          </el-descriptions-item>
          <el-descriptions-item label="姓名">
            {{ employeeInfo.name }}
          </el-descriptions-item>
          <el-descriptions-item label="部门">
            {{ employeeInfo.department?.name || '-' }}
          </el-descriptions-item>
          <el-descriptions-item label="职位">
            {{ employeeInfo.position?.name || '-' }}
          </el-descriptions-item>
          <el-descriptions-item label="入职日期">
            {{ employeeInfo.hire_date || '-' }}
          </el-descriptions-item>
          <el-descriptions-item label="状态">
            <el-tag :type="employeeInfo.status ? 'success' : 'danger'">
              {{ employeeInfo.status ? '在职' : '离职' }}
            </el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="基本工资">
            {{ formatCurrency(employeeInfo.base_salary) }}
          </el-descriptions-item>
        </el-descriptions>
      </el-card>
      
      <!-- 工资筛选 -->
      <el-card shadow="hover" class="filter-card">
        <template #header>
          <div class="card-header">
            <span>查询条件</span>
          </div>
        </template>
        
        <el-form :inline="true" :model="searchForm">
          <el-form-item label="年份">
            <el-select v-model="searchForm.year" placeholder="选择年份" clearable>
              <el-option
                v-for="year in yearOptions"
                :key="year"
                :label="year + '年'"
                :value="year"
              />
            </el-select>
          </el-form-item>
          <el-form-item label="月份">
            <el-select v-model="searchForm.month" placeholder="选择月份" clearable>
              <el-option
                v-for="month in 12"
                :key="month"
                :label="`${month}月`"
                :value="month"
              />
            </el-select>
          </el-form-item>
          <el-form-item>
            <el-button type="primary" @click="fetchSalaries">查询</el-button>
            <el-button @click="resetSearch">重置</el-button>
          </el-form-item>
        </el-form>
      </el-card>
      
      <!-- 工资列表 -->
      <el-card shadow="hover" class="salary-card" v-loading="salaryLoading">
        <template #header>
          <div class="card-header">
            <span>工资明细记录</span>
            <el-button type="primary" size="small" @click="exportSalary">
              导出明细
            </el-button>
          </div>
        </template>
        
        <el-table
          :data="salaryRecords"
          style="width: 100%"
          border
          stripe
          v-if="salaryRecords.length > 0"
        >
          <el-table-column prop="year_month" label="发放期间" width="120">
            <template #default="{ row }">
              {{ row.year }}年{{ row.month }}月
            </template>
          </el-table-column>
          <el-table-column prop="payment_date" label="发放日期" width="120" />
          <el-table-column prop="base_salary" label="基本工资" width="120">
            <template #default="{ row }">
              {{ formatCurrency(row.base_salary) }}
            </template>
          </el-table-column>
          <el-table-column prop="performance" label="绩效工资" width="120">
            <template #default="{ row }">
              {{ formatCurrency(row.performance) }}
            </template>
          </el-table-column>
          <el-table-column prop="overtime_pay" label="加班费" width="120">
            <template #default="{ row }">
              {{ formatCurrency(row.overtime_pay) }}
            </template>
          </el-table-column>
          <el-table-column prop="bonus" label="奖金" width="120">
            <template #default="{ row }">
              {{ formatCurrency(row.bonus) }}
            </template>
          </el-table-column>
          <el-table-column prop="social_security" label="社保" width="120">
            <template #default="{ row }">
              {{ formatCurrency(row.social_security) }}
            </template>
          </el-table-column>
          <el-table-column prop="housing_fund" label="公积金" width="120">
            <template #default="{ row }">
              {{ formatCurrency(row.housing_fund) }}
            </template>
          </el-table-column>
          <el-table-column prop="tax" label="个税" width="120">
            <template #default="{ row }">
              {{ formatCurrency(row.tax) }}
            </template>
          </el-table-column>
          <el-table-column prop="attendance_deduction" label="考勤扣款" width="120">
            <template #default="{ row }">
              {{ formatCurrency(row.attendance_deduction) }}
            </template>
          </el-table-column>
          <el-table-column prop="other_deduction" label="其他扣款" width="120">
            <template #default="{ row }">
              {{ formatCurrency(row.other_deduction) }}
            </template>
          </el-table-column>
          <el-table-column prop="net_salary" label="实发工资" width="120">
            <template #default="{ row }">
              <span class="net-salary">{{ formatCurrency(row.net_salary) }}</span>
            </template>
          </el-table-column>
          <el-table-column prop="status" label="状态" width="100">
            <template #default="{ row }">
              <el-tag :type="row.status === 'paid' ? 'success' : 'warning'">
                {{ row.status === 'paid' ? '已发放' : '未发放' }}
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column label="操作" width="150" fixed="right">
            <template #default="{ row }">
              <el-button link type="primary" size="small" @click="viewSalaryDetail(row)">
                查看
              </el-button>
              <el-button link type="primary" size="small" @click="printSalary(row)">
                打印
              </el-button>
            </template>
          </el-table-column>
        </el-table>
        
        <div class="empty-tip" v-else>
          <el-empty description="暂无工资记录" />
        </div>
      </el-card>
    </div>
    
    <!-- 工资条详情弹窗 -->
    <el-dialog
      v-model="salaryDetailVisible"
      title="工资条详情"
      width="700px"
    >
      <div class="salary-slip" v-if="currentSalary">
        <h3 class="slip-title">{{ currentSalary.year }}年{{ currentSalary.month }}月 工资条</h3>
        
        <el-descriptions :column="2" border>
          <el-descriptions-item label="员工姓名">
            {{ employeeInfo?.name }}
          </el-descriptions-item>
          <el-descriptions-item label="员工工号">
            {{ employeeInfo?.id ? String(employeeInfo.id).padStart(4, '0') : '' }}
          </el-descriptions-item>
          <el-descriptions-item label="部门">
            {{ employeeInfo?.department?.name }}
          </el-descriptions-item>
          <el-descriptions-item label="职位">
            {{ employeeInfo?.position?.name }}
          </el-descriptions-item>
          <el-descriptions-item label="发放日期">
            {{ currentSalary.payment_date }}
          </el-descriptions-item>
          <el-descriptions-item label="工资期间">
            {{ currentSalary.year }}年{{ currentSalary.month }}月
          </el-descriptions-item>
        </el-descriptions>
        
        <h4 class="section-title">收入项目</h4>
        <el-descriptions :column="3" border>
          <el-descriptions-item label="基本工资">
            {{ formatCurrency(currentSalary.base_salary) }}
          </el-descriptions-item>
          <el-descriptions-item label="绩效工资">
            {{ formatCurrency(currentSalary.performance) }}
          </el-descriptions-item>
          <el-descriptions-item label="加班费">
            {{ formatCurrency(currentSalary.overtime_pay) }}
          </el-descriptions-item>
          <el-descriptions-item label="奖金">
            {{ formatCurrency(currentSalary.bonus) }}
          </el-descriptions-item>
          <el-descriptions-item label="其他补贴">
            {{ formatCurrency(currentSalary.other_allowance) }}
          </el-descriptions-item>
          <el-descriptions-item label="收入合计">
            {{ formatCurrency(calculateTotalIncome(currentSalary)) }}
          </el-descriptions-item>
        </el-descriptions>
        
        <h4 class="section-title">扣款项目</h4>
        <el-descriptions :column="3" border>
          <el-descriptions-item label="社保">
            {{ formatCurrency(currentSalary.social_security) }}
          </el-descriptions-item>
          <el-descriptions-item label="公积金">
            {{ formatCurrency(currentSalary.housing_fund) }}
          </el-descriptions-item>
          <el-descriptions-item label="个税">
            {{ formatCurrency(currentSalary.tax) }}
          </el-descriptions-item>
          <el-descriptions-item label="考勤扣款">
            {{ formatCurrency(currentSalary.attendance_deduction) }}
          </el-descriptions-item>
          <el-descriptions-item label="其他扣款">
            {{ formatCurrency(currentSalary.other_deduction) }}
          </el-descriptions-item>
          <el-descriptions-item label="扣款合计">
            {{ formatCurrency(calculateTotalDeduction(currentSalary)) }}
          </el-descriptions-item>
        </el-descriptions>
        
        <div class="net-salary-section">
          <h4>实发工资: <span class="net-salary">{{ formatCurrency(currentSalary.net_salary) }}</span></h4>
        </div>
        
        <div class="remark-section" v-if="currentSalary.remark">
          <h4>备注:</h4>
          <p>{{ currentSalary.remark }}</p>
        </div>
      </div>
      
      <template #footer>
        <div class="dialog-footer">
          <el-button @click="salaryDetailVisible = false">关闭</el-button>
          <el-button type="primary" @click="printCurrentSalary">打印</el-button>
        </div>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted, watch } from 'vue';
import { useRouter, useRoute } from 'vue-router';
import { ElMessage } from 'element-plus';
import { useEmployeesStore } from '@/stores/employees';
import { useDepartmentsStore } from '@/stores/departments';
import { usePositionsStore } from '@/stores/positions';

// 定义接口类型
interface Employee {
  id: number;
  name: string;
  department_id: number;
  position_id: number;
  base_salary: number;
  hire_date: string;
  phone: string;
  email?: string;
  address?: string;
  id_card: string;
  bank_name?: string;
  bank_account?: string;
  status: boolean;
  department?: {
    id: number;
    name: string;
  };
  position?: {
    id: number;
    name: string;
  };
}

interface SalaryRecord {
  id: number;
  employee_id: number;
  year: number;
  month: number;
  base_salary: number;
  basic_salary?: number; // 保留兼容性
  performance: number;
  overtime_pay: number;
  bonus: number;
  other_allowance: number;
  social_security: number;
  housing_fund: number;
  tax: number;
  attendance_deduction: number;
  other_deduction: number;
  net_salary: number;
  status: string;
  payment_date: string;
  remark?: string;
}

// 路由和Store
const router = useRouter();
const route = useRoute();
const employeeId = computed(() => Number(route.params.id));
const employeesStore = useEmployeesStore();
const departmentsStore = useDepartmentsStore();
const positionsStore = usePositionsStore();

// 状态定义
const employeeLoading = ref(false);
const salaryLoading = ref(false);
const employeeInfo = ref<Employee | null>(null);
const salaryRecords = ref<SalaryRecord[]>([]);
const salaryDetailVisible = ref(false);
const currentSalary = ref<SalaryRecord | null>(null);

// 搜索表单
const searchForm = reactive({
  year: new Date().getFullYear(),
  month: null as number | null
});

// 年份选项（从2020年到当前年份）
const yearOptions = computed(() => {
  const currentYear = new Date().getFullYear();
  const years = [];
  for (let year = 2020; year <= currentYear; year++) {
    years.push(year);
  }
  return years;
});

// 监听路由参数变化
watch(() => route.params.id, (newId) => {
  if (newId) {
    // 当员工ID变化时，重新获取员工数据和工资记录
    fetchEmployeeInfo();
    fetchSalaries();
  }
});

// 获取员工信息
const fetchEmployeeInfo = async () => {
  if (!employeeId.value) return;
  
  employeeLoading.value = true;
  try {
    // 强制从API重新获取员工数据，不使用缓存
    const data = await employeesStore.getEmployee(employeeId.value, true);
      
      // 确保部门和职位信息可用
    if (data && data.department_id && !data.department) {
        const departments = departmentsStore.departments;
        const department = departments.find(d => d.id === data.department_id);
        if (department) {
          data.department = department;
        }
      }
      
    if (data && data.position_id && !data.position) {
        const positions = positionsStore.positions;
        const position = positions.find(p => p.id === data.position_id);
        if (position) {
          data.position = position;
      }
    }
    
    employeeInfo.value = data;
    console.log('员工工资页面 - 获取到的员工数据:', data);
  } catch (error) {
    ElMessage.error('获取员工信息失败');
    console.error('获取员工信息失败:', error);
  } finally {
    employeeLoading.value = false;
  }
};

// 获取工资记录
const fetchSalaries = async () => {
  if (!employeeId.value) return;
  
  salaryLoading.value = true;
  try {
    const year = searchForm.year;
    const month = searchForm.month;
    
    const data = await employeesStore.getEmployeeSalaries(employeeId.value, year, month);
    salaryRecords.value = data || [];
  } catch (error) {
    ElMessage.error('获取工资记录失败');
    console.error('获取工资记录失败:', error);
  } finally {
    salaryLoading.value = false;
  }
};

// 重置搜索条件
const resetSearch = () => {
  searchForm.year = new Date().getFullYear();
  searchForm.month = null;
  fetchSalaries();
};

// 查看工资详情
const viewSalaryDetail = (salary: SalaryRecord) => {
  currentSalary.value = salary;
  salaryDetailVisible.value = true;
};

// 打印工资条
const printSalary = (salary: SalaryRecord) => {
  currentSalary.value = salary;
  printCurrentSalary();
};

// 打印当前工资条
const printCurrentSalary = () => {
  // 这里实现打印功能
  // 可以使用window.print()或第三方打印库
  ElMessage.success('打印功能已触发');
};

// 导出工资明细
const exportSalary = () => {
  ElMessage.success('导出功能已触发');
  // 实现导出功能
};

// 格式化货币
const formatCurrency = (value: number | undefined | null) => {
  if (value === undefined || value === null) return '¥0.00';
  return `¥${Number(value).toFixed(2)}`;
};

// 计算总收入
const calculateTotalIncome = (salary: SalaryRecord | null) => {
  if (!salary) return 0;
  // 优先使用base_salary，如果没有则尝试使用basic_salary
  const baseSalary = salary.base_salary !== undefined ? salary.base_salary : (salary.basic_salary || 0);
  return (
    baseSalary +
    (salary.performance || 0) +
    (salary.overtime_pay || 0) +
    (salary.bonus || 0) +
    (salary.other_allowance || 0)
  );
};

// 计算总扣款
const calculateTotalDeduction = (salary: SalaryRecord | null) => {
  if (!salary) return 0;
  return (
    (salary.social_security || 0) +
    (salary.housing_fund || 0) +
    (salary.tax || 0) +
    (salary.attendance_deduction || 0) +
    (salary.other_deduction || 0)
  );
};

// 返回上一页
const goBack = () => {
  router.back();
};

// 初始化
onMounted(async () => {
  console.log('员工工资页面初始化，员工ID:', employeeId.value);
  
  try {
    // 加载部门和职位数据，以便正确显示部门和职位信息
    if (departmentsStore.departments.length === 0) {
      console.log('加载部门数据...');
      await departmentsStore.getDepartments();
    }
    
    if (positionsStore.positions.length === 0) {
      console.log('加载职位数据...');
      await positionsStore.getPositions();
    }
    
    await fetchEmployeeInfo();
    await fetchSalaries();
    
    console.log('员工工资页面初始化完成');
  } catch (error) {
    console.error('员工工资页面初始化失败:', error);
    ElMessage.error('数据加载失败');
  }
});
</script>

<style scoped>
.employee-salary {
  padding: 20px;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.page-header h2 {
  margin: 0;
}

.info-card,
.filter-card,
.salary-card {
  margin-bottom: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.empty-tip {
  padding: 30px 0;
}

.net-salary {
  color: #f56c6c;
  font-weight: bold;
}

.salary-slip {
  padding: 10px;
}

.slip-title {
  text-align: center;
  margin-bottom: 20px;
}

.section-title {
  margin: 15px 0 10px;
  padding-left: 5px;
  border-left: 3px solid #409eff;
}

.net-salary-section {
  margin: 20px 0;
  text-align: right;
  padding-right: 20px;
}

.remark-section {
  border-top: 1px dashed #dcdfe6;
  padding-top: 10px;
  margin-top: 20px;
}
</style> 