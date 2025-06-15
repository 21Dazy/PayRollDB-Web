<template>
  <div class="salary-config">
    <div class="page-header">
      <h2>薪资配置</h2>
    </div>
    
    <div class="filter-bar">
      <el-form :inline="true" :model="filterForm">
        <el-form-item label="部门">
          <el-select v-model="filterForm.departmentId" placeholder="请选择部门" clearable @change="handleDepartmentChange">
            <el-option
              v-for="item in departmentOptions"
              :key="item.value"
              :label="item.label"
              :value="item.value"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="员工搜索">
          <el-input
            v-model="filterForm.keyword"
            placeholder="输入姓名/工号/职位搜索"
            clearable
            class="search-input"
            @keyup.enter="handleEmployeeSearch"
          >
            <template #append>
              <el-button :icon="Search" @click="handleEmployeeSearch"></el-button>
            </template>
          </el-input>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="handleEmployeeSearch" :loading="employeesLoading">搜索</el-button>
        </el-form-item>
      </el-form>
      
      <div class="search-tips">
        <el-alert
          title="提示：可以先选择部门，再输入关键词搜索，或直接输入关键词进行全局搜索。支持按姓名、工号、职位等进行搜索。"
          type="info"
          :closable="false"
          show-icon
        />
      </div>
      
      <div v-if="employeeSearchResults.length > 0" class="employee-search-results">
        <div class="search-results-header">
          <span>搜索结果 ({{ employeeSearchResults.length }})</span>
          <el-button link type="primary" @click="clearSearchResults">清空</el-button>
        </div>
        <el-table
          :data="employeeSearchResults"
          style="width: 100%"
          height="250"
          border
          stripe
          @row-click="handleEmployeeSelect"
        >
          <el-table-column prop="employee_id" label="工号" width="100" />
          <el-table-column prop="name" label="姓名" width="100" />
          <el-table-column prop="department_name" label="部门" width="120" />
          <el-table-column prop="position_name" label="职位" width="120" />
          <el-table-column label="操作" width="100" fixed="right">
            <template #default="{ row }">
              <el-button link type="primary" @click.stop="handleEmployeeSelect(row)">选择</el-button>
            </template>
          </el-table-column>
        </el-table>
      </div>
    </div>
    
    <div v-if="currentEmployee" class="employee-info">
      <el-descriptions title="员工信息" :column="4" border>
        <el-descriptions-item label="工号">{{ currentEmployee.employee_id || '-' }}</el-descriptions-item>
        <el-descriptions-item label="姓名">{{ currentEmployee.name || '-' }}</el-descriptions-item>
        <el-descriptions-item label="部门">{{ currentEmployee.department_name || '-' }}</el-descriptions-item>
        <el-descriptions-item label="职位">{{ currentEmployee.position_name || '-' }}</el-descriptions-item>
        <el-descriptions-item label="入职日期">{{ formatDate(currentEmployee.hire_date) || '-' }}</el-descriptions-item>
        <el-descriptions-item label="银行">{{ currentEmployee.bank_name || '-' }}</el-descriptions-item>
        <el-descriptions-item label="银行账号">{{ currentEmployee.bank_account ? maskBankAccount(currentEmployee.bank_account) : '-' }}</el-descriptions-item>
        <el-descriptions-item label="基本工资">{{ formatCurrency(currentEmployee.base_salary) }}</el-descriptions-item>
      </el-descriptions>
    </div>
    
    <div v-if="currentEmployee" class="salary-items">
      <div class="section-header">
        <h3>薪资项目配置</h3>
        <el-button type="primary" @click="handleAddItem">添加薪资项目</el-button>
      </div>
      
      <el-table
        :data="employeeSalaryItems"
        style="width: 100%"
        border
        stripe
      >
        <el-table-column prop="item_name" label="项目名称" width="150" />
        <el-table-column prop="type" label="类型" width="120">
          <template #default="{ row }">
            <el-tag :type="row.type === 'addition' ? 'success' : 'danger'">
              {{ row.type === 'addition' ? '收入项' : '扣减项' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="calculation_method" label="计算方式" width="150">
          <template #default="{ row }">
            <span v-if="row.is_percentage">
              {{ row.value }}% {{ row.base_item ? `(基于${row.base_item})` : '' }}
            </span>
            <span v-else>{{ formatCurrency(row.value) }}</span>
          </template>
        </el-table-column>
        <el-table-column label="预览金额" width="120">
          <template #default="{ row }">
            {{ formatCurrency(calculateItemAmount(row)) }}
          </template>
        </el-table-column>
        <el-table-column label="操作" width="150">
          <template #default="{ row }">
            <el-button 
              link 
              type="primary" 
              size="small" 
              @click="handleEditItem(row)"
              :disabled="row.is_system"
            >
              编辑
            </el-button>
            <el-button 
              link 
              type="danger" 
              size="small" 
              @click="handleDeleteItem(row)"
              :disabled="row.is_system"
            >
              删除
            </el-button>
          </template>
        </el-table-column>
      </el-table>
      
      <div class="salary-summary">
        <el-descriptions title="工资预览" :column="2" border>
          <el-descriptions-item label="收入合计">
            <span class="text-success">{{ formatCurrency(totalAddition) }}</span>
          </el-descriptions-item>
          <el-descriptions-item label="扣减合计">
            <span class="text-danger">{{ formatCurrency(totalDeduction) }}</span>
          </el-descriptions-item>
          <el-descriptions-item label="预计实发工资">
            <span class="text-primary">{{ formatCurrency(netSalary) }}</span>
          </el-descriptions-item>
        </el-descriptions>
        
        <div class="action-buttons">
          <el-button type="primary" @click="handleSaveConfig" :loading="saving">保存配置</el-button>
        </div>
      </div>
    </div>
    
    <!-- 添加/编辑薪资项目对话框 -->
    <el-dialog
      v-model="dialogVisible"
      :title="isEdit ? '编辑薪资项目' : '添加薪资项目'"
      width="500px"
    >
      <el-form 
        ref="formRef" 
        :model="form" 
        :rules="rules" 
        label-width="100px"
      >
        <el-form-item label="薪资项目" prop="item_id">
          <el-select 
            v-model="form.item_id" 
            placeholder="请选择薪资项目" 
            style="width: 100%"
            @change="handleItemChange"
          >
            <el-option 
              v-for="item in salaryItemOptions" 
              :key="item.value" 
              :label="item.label" 
              :value="item.value"
            />
          </el-select>
        </el-form-item>
        
        <el-form-item label="计算方式">
          <el-radio-group v-model="selectedItem.is_percentage" disabled>
            <el-radio :label="false">固定金额</el-radio>
            <el-radio :label="true">百分比</el-radio>
          </el-radio-group>
        </el-form-item>
        
        <el-form-item label="数值" prop="value">
          <el-input-number 
            v-model="form.value" 
            :precision="selectedItem.is_percentage ? 2 : 2" 
            :step="selectedItem.is_percentage ? 1 : 100" 
            :min="0"
            style="width: 100%"
          />
        </el-form-item>
        
        <el-form-item 
          label="基准项目" 
          prop="base_item"
          v-if="selectedItem.is_percentage"
        >
          <el-select 
            v-model="form.base_item" 
            placeholder="请选择基准项目" 
            style="width: 100%"
            clearable
          >
            <el-option label="基本工资" value="base_salary" />
          </el-select>
        </el-form-item>
      </el-form>
      <template #footer>
        <div class="dialog-footer">
          <el-button @click="dialogVisible = false">取消</el-button>
          <el-button type="primary" @click="submitForm" :loading="submitting">确认</el-button>
        </div>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted, watch, getCurrentInstance } from 'vue';
import { ElMessage, ElMessageBox } from 'element-plus';
import type { FormInstance } from 'element-plus';
import { useDepartmentsStore } from '@/stores/departments';
import { useEmployeesStore } from '@/stores/employees';
import { useSalaryItemsStore } from '@/stores/salaryItems';
import { useSalaryConfigStore } from '@/stores/salaryConfig';
import { Search } from '@element-plus/icons-vue';

// Store 实例
const departmentsStore = useDepartmentsStore();
const employeesStore = useEmployeesStore();
const salaryItemsStore = useSalaryItemsStore();
const salaryConfigStore = useSalaryConfigStore();

// 获取Vue实例，用于强制刷新
const { proxy } = getCurrentInstance() || { proxy: null };

// 状态变量
const employeesLoading = ref(false);
const currentEmployee = ref(null);
const employeeSalaryItems = ref([]);
const employeeSearchResults = ref([]);
const dialogVisible = ref(false);
const isEdit = ref(false);
const submitting = ref(false);
const saving = ref(false);
const formRef = ref<FormInstance | null>(null);
const currentItemId = ref(null);

// 部门选项
const departmentOptions = computed(() => {
  return departmentsStore.departments.map(dept => ({
    value: dept.id,
    label: dept.name
  }));
});

// 员工选项
const employeeOptions = computed(() => {
  return employeesStore.employees.map(emp => ({
    value: emp.id,
    label: `${emp.name} (${emp.employee_id})`
  }));
});

// 薪资项目选项
const salaryItemOptions = computed(() => {
  // 过滤掉已经配置的项目
  const configuredItemIds = employeeSalaryItems.value.map(item => item.item_id);
  
  return salaryItemsStore.salaryItems
    .filter(item => !configuredItemIds.includes(item.id) || (isEdit.value && item.id === form.item_id))
    .map(item => ({
      value: item.id,
      label: item.name,
      type: item.type,
      is_percentage: item.is_percentage
    }));
});

// 表单数据
const filterForm = reactive({
  departmentId: '',
  keyword: ''
});

// 当前选中的薪资项目
const selectedItem = reactive({
  id: null,
  name: '',
  type: 'addition',
  is_percentage: false
});

// 薪资项目表单
const form = reactive({
  item_id: null,
  item_name: '',
  type: 'addition',
  is_percentage: false,
  value: 0,
  base_item: 'base_salary'
});

// 表单验证规则
const rules = {
  item_id: [
    { required: true, message: '请选择薪资项目', trigger: 'change' }
  ],
  value: [
    { required: true, message: '请输入数值', trigger: 'blur' }
  ]
};

// 合计计算
const totalAddition = computed(() => {
  return employeeSalaryItems.value
    .filter(item => item.type === 'addition')
    .reduce((sum, item) => sum + calculateItemAmount(item), 0);
});

const totalDeduction = computed(() => {
  return employeeSalaryItems.value
    .filter(item => item.type === 'deduction')
    .reduce((sum, item) => sum + calculateItemAmount(item), 0);
});

const netSalary = computed(() => {
  return totalAddition.value - totalDeduction.value;
});

// 格式化货币
const formatCurrency = (value) => {
  if (value === undefined || value === null) return '¥0.00';
  return `¥${Number(value).toFixed(2)}`;
};

// 格式化日期
const formatDate = (dateStr) => {
  if (!dateStr) return '-';
  try {
    const date = new Date(dateStr);
    return date.toISOString().split('T')[0];
  } catch (e) {
    return dateStr;
  }
};

// 掩码银行账号
const maskBankAccount = (account) => {
  if (!account) return '';
  return account.replace(/^(\d{6})(\d+)(\d{4})$/, '$1****$3');
};

// 计算薪资项目金额
const calculateItemAmount = (item) => {
  if (!currentEmployee.value) return 0;
  
  if (item.is_percentage) {
    // 百分比计算
    const baseValue = item.base_item === 'base_salary' 
      ? currentEmployee.value.base_salary 
      : 0;
    return baseValue * (item.value / 100);
  } else {
    // 固定金额
    return item.value;
  }
};

// 处理部门变更
const handleDepartmentChange = async () => {
  console.log('部门变更:', filterForm.departmentId, typeof filterForm.departmentId);
  // 强制刷新组件，解决选择值不显示的问题
  window.requestAnimationFrame(() => {
    window.requestAnimationFrame(() => {
      proxy?.$forceUpdate();
    });
  });
  
  filterForm.keyword = '';
  currentEmployee.value = null;
  employeeSalaryItems.value = [];
  employeeSearchResults.value = [];
  
  if (!filterForm.departmentId) return;
  
  // 当部门选择变化时，直接执行搜索，显示该部门所有员工
  employeesLoading.value = true;
  try {
    const departmentIdNum = Number(filterForm.departmentId);
    console.log('调用searchEmployees:', '', departmentIdNum);
    const results = await employeesStore.searchEmployees(
      '', // 空关键词
      departmentIdNum
    );
    employeeSearchResults.value = results;
    
    if (results.length === 0) {
      ElMessage.info('该部门下没有员工');
    }
  } catch (error) {
    console.error('获取部门员工失败:', error);
    ElMessage.error('获取部门员工失败');
  } finally {
    employeesLoading.value = false;
  }
};

// 处理员工搜索
const handleEmployeeSearch = async () => {
  console.log('员工搜索参数:', filterForm.keyword, filterForm.departmentId, typeof filterForm.departmentId);
  
  if (!filterForm.keyword && !filterForm.departmentId) {
    ElMessage.warning('请输入搜索关键词或选择部门');
    return;
  }
  
  employeesLoading.value = true;
  try {
    // 清除当前选中的员工
    currentEmployee.value = null;
    employeeSalaryItems.value = [];
    
    // 使用后端专门的搜索接口
    const departmentIdParam = filterForm.departmentId ? Number(filterForm.departmentId) : undefined;
    console.log('调用searchEmployees:', filterForm.keyword, departmentIdParam);
    
    const results = await employeesStore.searchEmployees(
      filterForm.keyword,
      departmentIdParam
    );
    employeeSearchResults.value = results;
    
    if (results.length === 0) {
      ElMessage.info('未找到匹配的员工');
    } else {
      console.log('搜索结果:', results);
    }
  } catch (error) {
    console.error('搜索员工失败:', error);
    ElMessage.error('搜索员工失败');
  } finally {
    employeesLoading.value = false;
  }
};

// 员工搜索功能现在直接使用后端返回的department_name和position_name
// 不再需要前端手动处理这些字段

// 处理员工选择
const handleEmployeeSelect = async (row) => {
  // 后端已经返回了正确的department_name和position_name
  // 直接使用即可，不需要额外处理
  currentEmployee.value = row;
  employeeSalaryItems.value = [];
  
  try {
    // 获取员工薪资配置
    const config = await salaryConfigStore.getEmployeeSalaryConfig(row.id);
    employeeSalaryItems.value = config.items || [];
  } catch (error) {
    console.error('获取员工薪资配置失败:', error);
    ElMessage.error('获取员工薪资配置失败');
  }
};

// 处理添加薪资项目
const handleAddItem = () => {
  resetForm();
  isEdit.value = false;
  dialogVisible.value = true;
};

// 处理编辑薪资项目
const handleEditItem = (row) => {
  resetForm();
  isEdit.value = true;
  currentItemId.value = row.id;
  
  // 填充表单数据
  form.item_id = row.item_id;
  form.item_name = row.item_name;
  form.type = row.type;
  form.is_percentage = row.is_percentage;
  form.value = row.value;
  form.base_item = row.base_item || 'base_salary';
  
  // 设置选中的薪资项目
  const item = salaryItemsStore.salaryItems.find(item => item.id === row.item_id);
  if (item) {
    selectedItem.id = item.id;
    selectedItem.name = item.name;
    selectedItem.type = item.type;
    selectedItem.is_percentage = item.is_percentage;
  }
  
  dialogVisible.value = true;
};

// 处理删除薪资项目
const handleDeleteItem = (row) => {
  if (row.is_system) {
    ElMessage.warning('系统项目不可删除');
    return;
  }
  
  ElMessageBox.confirm(
    `确定要删除薪资项目"${row.item_name}"吗？`,
    '删除确认',
    {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning',
    }
  ).then(() => {
    // 从列表中删除
    employeeSalaryItems.value = employeeSalaryItems.value.filter(item => item.id !== row.id);
    ElMessage.success('删除成功');
  }).catch(() => {
    ElMessage.info('已取消删除');
  });
};

// 处理薪资项目变更
const handleItemChange = () => {
  const item = salaryItemsStore.salaryItems.find(item => item.id === form.item_id);
  if (item) {
    selectedItem.id = item.id;
    selectedItem.name = item.name;
    selectedItem.type = item.type;
    selectedItem.is_percentage = item.is_percentage;
    
    form.item_name = item.name;
    form.type = item.type;
    form.is_percentage = item.is_percentage;
    
    // 重置数值
    form.value = item.is_percentage ? 0 : 0;
  }
};

// 提交表单
const submitForm = async () => {
  if (!formRef.value) return;
  
  try {
    await formRef.value.validate();
    
    submitting.value = true;
    
    const newItem = {
      id: isEdit.value ? currentItemId.value : Date.now(), // 临时ID
      item_id: form.item_id,
      item_name: form.item_name,
      type: form.type,
      is_percentage: form.is_percentage,
      value: form.value,
      base_item: form.is_percentage ? form.base_item : null,
      is_system: false
    };
    
    if (isEdit.value) {
      // 更新项目
      const index = employeeSalaryItems.value.findIndex(item => item.id === currentItemId.value);
      if (index !== -1) {
        employeeSalaryItems.value[index] = newItem;
      }
    } else {
      // 添加项目
      employeeSalaryItems.value.push(newItem);
    }
    
    dialogVisible.value = false;
    ElMessage.success(isEdit.value ? '更新成功' : '添加成功');
  } catch (error) {
    console.error('表单验证失败:', error);
  } finally {
    submitting.value = false;
  }
};

// 保存薪资配置
const handleSaveConfig = async () => {
  if (!currentEmployee.value) {
    ElMessage.warning('请先选择员工');
    return;
  }
  
  saving.value = true;
  try {
    // 准备要保存的数据，确保包含effective_date
    const configItems = employeeSalaryItems.value.map(item => ({
      item_id: item.item_id,
      value: item.value,
      base_item: item.base_item,
      is_active: true,
      effective_date: new Date().toISOString().split('T')[0] // 当前日期
    }));
    
    await salaryConfigStore.saveEmployeeSalaryConfig(currentEmployee.value.id, {
      items: configItems
    });
    
    ElMessage.success('薪资配置保存成功');
  } catch (error) {
    console.error('保存薪资配置失败:', error);
    ElMessage.error('保存薪资配置失败');
  } finally {
    saving.value = false;
  }
};

// 重置表单
const resetForm = () => {
  if (formRef.value) {
    formRef.value.resetFields();
  }
  
  Object.assign(form, {
    item_id: null,
    item_name: '',
    type: 'addition',
    is_percentage: false,
    value: 0,
    base_item: 'base_salary'
  });
  
  Object.assign(selectedItem, {
    id: null,
    name: '',
    type: 'addition',
    is_percentage: false
  });
  
  currentItemId.value = null;
};

// 清空搜索结果
const clearSearchResults = () => {
  employeeSearchResults.value = [];
  filterForm.keyword = '';
};

// 初始化
onMounted(async () => {
  try {
    // 获取部门列表
    await departmentsStore.getDepartments();
    
    // 获取薪资项目列表
    await salaryItemsStore.getSalaryItems();
  } catch (error) {
    console.error('初始化数据失败:', error);
    ElMessage.error('初始化数据失败');
  }
});
</script>

<style scoped lang="scss">
.salary-config {
  .page-header {
    margin-bottom: 20px;
    
    h2 {
      font-size: 20px;
      font-weight: 600;
      margin: 0;
    }
  }
  
  .filter-bar {
    background-color: #fff;
    padding: 20px;
    border-radius: 4px;
    box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.04);
    margin-bottom: 20px;
    
    .search-input {
      width: 250px;
    }
    
    .search-tips {
      margin: 10px 0;
    }
    
    .employee-search-results {
      margin-top: 15px;
      border: 1px solid #ebeef5;
      border-radius: 4px;
      overflow: hidden;
      
      .search-results-header {
        padding: 8px 15px;
        background-color: #f5f7fa;
        display: flex;
        justify-content: space-between;
        align-items: center;
        font-size: 14px;
        font-weight: 500;
      }
    }
  }
  
  .employee-info {
    background-color: #fff;
    padding: 20px;
    border-radius: 4px;
    box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.04);
    margin-bottom: 20px;
  }
  
  .salary-items {
    background-color: #fff;
    padding: 20px;
    border-radius: 4px;
    box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.04);
    
    .section-header {
      display: flex;
      justify-content: space-between;
      align-items: center;
      margin-bottom: 20px;
      
      h3 {
        font-size: 16px;
        font-weight: 600;
        margin: 0;
      }
    }
    
    .salary-summary {
      margin-top: 30px;
      
      .text-success {
        color: #67c23a;
        font-weight: bold;
      }
      
      .text-danger {
        color: #f56c6c;
        font-weight: bold;
      }
      
      .text-primary {
        color: #409eff;
        font-weight: bold;
        font-size: 18px;
      }
      
      .action-buttons {
        display: flex;
        justify-content: flex-end;
        margin-top: 20px;
      }
    }
  }
}
</style> 