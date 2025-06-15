<template>
  <div class="employee-edit">
    <div class="page-header">
      <h2>编辑员工</h2>
      <div class="page-actions">
        <el-button @click="goBack">返回</el-button>
        <el-button @click="resetForm">重置</el-button>
        <el-button type="primary" @click="handleSubmit" :loading="loading">保存</el-button>
      </div>
    </div>
    
    <div class="form-container" v-loading="formLoading">
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
              <span>基本信息</span>
            </div>
          </template>
          
          <el-row :gutter="20">
            <el-col :span="12">
              <el-form-item label="姓名" prop="name">
                <el-input v-model="form.name" placeholder="请输入姓名" />
              </el-form-item>
            </el-col>
            <el-col :span="12">
              <el-form-item label="身份证号" prop="idCard">
                <el-input v-model="form.idCard" placeholder="请输入身份证号" />
              </el-form-item>
            </el-col>
          </el-row>
          
          <el-row :gutter="20">
            <el-col :span="12">
              <el-form-item label="部门" prop="departmentId">
                <el-select v-model="form.departmentId" placeholder="请选择部门" style="width: 100%">
                  <el-option
                    v-for="item in departmentOptions"
                    :key="item.value"
                    :label="item.label"
                    :value="item.value"
                  />
                </el-select>
              </el-form-item>
            </el-col>
            <el-col :span="12">
              <el-form-item label="职位" prop="positionId">
                <el-select v-model="form.positionId" placeholder="请选择职位" style="width: 100%">
                  <el-option
                    v-for="item in positionOptions"
                    :key="item.value"
                    :label="item.label"
                    :value="item.value"
                  />
                </el-select>
              </el-form-item>
            </el-col>
          </el-row>
          
          <el-row :gutter="20">
            <el-col :span="12">
              <el-form-item label="入职日期" prop="hireDate">
                <el-date-picker
                  v-model="form.hireDate"
                  type="date"
                  placeholder="请选择入职日期"
                  style="width: 100%"
                />
              </el-form-item>
            </el-col>
            <el-col :span="12">
              <el-form-item label="状态" prop="status">
                <el-select v-model="form.status" placeholder="请选择状态" style="width: 100%">
                  <el-option label="在职" :value="true" />
                  <el-option label="离职" :value="false" />
                </el-select>
              </el-form-item>
            </el-col>
          </el-row>
        </el-card>
        
        <el-card shadow="hover" class="form-card">
          <template #header>
            <div class="card-header">
              <span>薪资信息</span>
            </div>
          </template>
          
          <el-row :gutter="20">
            <el-col :span="12">
              <el-form-item label="基本工资" prop="baseSalary">
                <el-input-number
                  v-model="form.baseSalary"
                  :min="0"
                  :precision="2"
                  :step="1000"
                  style="width: 100%"
                />
              </el-form-item>
            </el-col>
          </el-row>
        </el-card>
        
        <el-card shadow="hover" class="form-card">
          <template #header>
            <div class="card-header">
              <span>联系信息</span>
            </div>
          </template>
          
          <el-row :gutter="20">
            <el-col :span="12">
              <el-form-item label="手机号码" prop="phone">
                <el-input v-model="form.phone" placeholder="请输入手机号码" />
              </el-form-item>
            </el-col>
            <el-col :span="12">
              <el-form-item label="电子邮箱" prop="email">
                <el-input v-model="form.email" placeholder="请输入电子邮箱" />
              </el-form-item>
            </el-col>
          </el-row>
          
          <el-form-item label="联系地址" prop="address">
            <el-input v-model="form.address" placeholder="请输入联系地址" />
          </el-form-item>
        </el-card>
        
        <el-card shadow="hover" class="form-card">
          <template #header>
            <div class="card-header">
              <span>银行信息</span>
            </div>
          </template>
          
          <el-row :gutter="20">
            <el-col :span="12">
              <el-form-item label="开户银行" prop="bankName">
                <el-input v-model="form.bankName" placeholder="请输入开户银行" />
              </el-form-item>
            </el-col>
            <el-col :span="12">
              <el-form-item label="银行账号" prop="bankAccount">
                <el-input v-model="form.bankAccount" placeholder="请输入银行账号" />
              </el-form-item>
            </el-col>
          </el-row>
        </el-card>
      </el-form>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted, watch } from 'vue';
import { useRouter, useRoute } from 'vue-router';
import { ElMessage, type FormInstance } from 'element-plus';
import { useEmployeesStore } from '@/stores/employees';
import { useDepartmentsStore } from '@/stores/departments';
import { usePositionsStore } from '@/stores/positions';
import { useAuthStore } from '@/stores/auth';

// 路由和Store
const router = useRouter();
const route = useRoute();
const employeeId = computed(() => Number(route.params.id));
const employeesStore = useEmployeesStore();
const departmentsStore = useDepartmentsStore();
const positionsStore = usePositionsStore();
const authStore = useAuthStore();

// 状态定义
const loading = ref(false);
const formLoading = ref(false);
const formRef = ref<FormInstance | null>(null);

// 表单数据
const form = reactive({
  name: '',
  departmentId: '',
  positionId: '',
  hireDate: '',
  status: true,
  baseSalary: 0,
  idCard: '',
  phone: '',
  email: '',
  address: '',
  bankName: '',
  bankAccount: ''
});

// 表单验证规则
const rules = {
  name: [{ required: true, message: '请输入姓名', trigger: 'blur' }],
  departmentId: [{ required: true, message: '请选择部门', trigger: 'change' }],
  positionId: [{ required: true, message: '请选择职位', trigger: 'change' }],
  hireDate: [{ required: true, message: '请选择入职日期', trigger: 'change' }],
  status: [{ required: true, message: '请选择员工状态', trigger: 'change' }],
  baseSalary: [{ required: true, message: '请输入基本工资', trigger: 'blur' }],
  phone: [{ required: true, message: '请输入手机号码', trigger: 'blur' }],
  idCard: [{ required: true, message: '请输入身份证号', trigger: 'blur' }]
};

// 计算属性
const departmentOptions = computed(() => {
  return (departmentsStore.departments || []).map(dept => ({
    value: dept.id,
    label: dept.name
  }));
});

const positionOptions = computed(() => {
  if (!positionsStore.positions || positionsStore.positions.length === 0) {
    return [];
  }
  
  if (!form.departmentId) {
    return [];
  }
  
  return positionsStore.positions
    .filter(pos => pos.department_id === parseInt(form.departmentId))
    .map(pos => ({
      value: pos.id,
      label: pos.name
    }));
});

// 监听部门变化，重置职位选择
watch(() => form.departmentId, (newVal, oldVal) => {
  if (newVal !== oldVal) {
    form.positionId = '';
  }
});

// 监听路由参数变化
watch(() => route.params.id, (newId) => {
  if (newId) {
    // 当员工ID变化时，重新获取员工数据
    fetchEmployeeDetail();
  }
});

// 重置表单
const resetForm = () => {
  formRef.value?.resetFields();
  fetchEmployeeDetail(); // 重新获取员工信息
};

// 获取员工详情并填充表单
const fetchEmployeeDetail = async () => {
  if (!employeeId.value) return;
  
  formLoading.value = true;
  try {
    // 强制从API重新获取员工数据，不使用缓存
    const employeeData = await employeesStore.getEmployee(employeeId.value, true);
    console.log('获取到的员工数据:', employeeData);
    
    if (!employeeData) {
      ElMessage.error('未获取到员工数据');
      return;
    }
    
    // 处理字段映射
    const mapEmployeeData = () => {
      // 基本信息
      form.name = employeeData.name || '';
      form.departmentId = employeeData.department_id || '';
      form.positionId = employeeData.position_id || '';
      
      // 日期需要特殊处理
      if (employeeData.hire_date) {
        form.hireDate = employeeData.hire_date;
      }
      
      // 状态处理
      form.status = employeeData.status !== undefined ? employeeData.status : true;
      
      // 薪资信息
      form.baseSalary = employeeData.base_salary || 0;
      
      // 个人信息
      form.idCard = employeeData.id_card || '';
      
      // 联系信息
      form.phone = employeeData.phone || '';
      form.email = employeeData.email || '';
      form.address = employeeData.address || '';
      
      // 银行信息
      form.bankName = employeeData.bank_name || '';
      form.bankAccount = employeeData.bank_account || '';
    };
    
    // 映射数据
    mapEmployeeData();
    
    // 打印映射后的表单数据
    console.log('表单数据已填充:', JSON.stringify(form, null, 2));
    
  } catch (error) {
    ElMessage.error('获取员工详情失败');
    console.error('获取员工详情失败:', error);
  } finally {
    formLoading.value = false;
  }
};

// 格式化日期对象为字符串(YYYY-MM-DD)
const formatDate = (date: any): string | null => {
  if (!date) return null;
  
  if (date instanceof Date) {
    return date.toISOString().split('T')[0];
  }
  
  if (typeof date === 'string') {
    return date;
  }
  
  return null;
};

// 提交表单
const handleSubmit = async () => {
  if (!formRef.value) return;
  
  try {
    await formRef.value.validate();
    
    loading.value = true;
    
    // 确保部门和职位ID是数字
    const parseDepartmentId = () => {
      if (!form.departmentId) return null;
      if (typeof form.departmentId === 'number') return form.departmentId;
      return parseInt(form.departmentId, 10) || null;
    };
    
    const parsePositionId = () => {
      if (!form.positionId) return null;
      if (typeof form.positionId === 'number') return form.positionId;
      return parseInt(form.positionId, 10) || null;
    };
    
    // 准备提交的数据，包含所有字段，确保与后端模型一致
    const updateData = {
      name: form.name,
      id_card: form.idCard,
      phone: form.phone,
      email: form.email,
      address: form.address,
      department_id: parseDepartmentId(),
      position_id: parsePositionId(),
      hire_date: formatDate(form.hireDate),
      base_salary: form.baseSalary,
      status: form.status,
      bank_name: form.bankName,
      bank_account: form.bankAccount
    };
    
    console.log('提交的更新数据:', updateData);
    
    await employeesStore.updateEmployee(employeeId.value, updateData);
    
    ElMessage.success('员工信息更新成功');
    goBack();
    
  } catch (error: any) {
    if (error.message) {
      ElMessage.error(`保存失败: ${error.message}`);
    } else {
      ElMessage.error('保存失败，请检查表单');
    }
    console.error('更新员工失败:', error);
  } finally {
    loading.value = false;
  }
};

// 返回上一页
const goBack = () => {
  router.back();
};

// 初始化数据
onMounted(async () => {
  try {
    console.log('开始初始化员工编辑页面，员工ID:', employeeId.value);
    
    // 获取部门和职位数据
    if (departmentsStore.departments.length === 0) {
      console.log('加载部门数据...');
      await departmentsStore.getDepartments();
    }
    
    if (positionsStore.positions.length === 0) {
      console.log('加载职位数据...');
      await positionsStore.getPositions();
    }
    
    // 获取员工详情
    console.log('获取员工详情...');
    await fetchEmployeeDetail();
    
    console.log('员工编辑页面初始化完成');
    
  } catch (error) {
    ElMessage.error('初始化数据失败');
    console.error('初始化数据失败:', error);
  }
});

// 添加异步监听，确保部门和职位数据已加载
watch([() => departmentsStore.departments, () => positionsStore.positions], 
  ([departments, positions]) => {
    if (departments.length > 0 && positions.length > 0) {
      console.log('部门和职位数据已加载，检查表单数据...');
      
      // 如果数据已加载但表单为空，尝试重新获取员工详情
      if (!form.name && employeeId.value) {
        console.log('表单数据为空，重新获取员工详情...');
        fetchEmployeeDetail();
      }
    }
  }, 
  { immediate: true }
);
</script>

<style scoped>
.employee-edit {
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

.form-container {
  background-color: #fff;
  border-radius: 4px;
}

.form-card {
  margin-bottom: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
</style> 