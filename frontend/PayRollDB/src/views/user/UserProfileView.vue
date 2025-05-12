<template>
  <div class="user-profile">
    <div class="page-header">
      <h2>个人信息</h2>
      <el-button type="primary" @click="handleEdit">编辑信息</el-button>
    </div>
    
    <div class="profile-content">
      <el-row :gutter="20">
        <el-col :xs="24" :md="8">
          <el-card class="avatar-card" shadow="hover">
            <div class="avatar-wrapper">
              <el-avatar :size="120" :src="userInfo.avatar" />
              <h3 class="user-name">{{ userInfo.name }}</h3>
              <p class="user-role">{{ userInfo.roleName }}</p>
            </div>
            <div class="user-stats">
              <div class="stat-item">
                <div class="stat-value">{{ userInfo.workYears }}</div>
                <div class="stat-label">工作年限</div>
              </div>
              <div class="stat-item">
                <div class="stat-value">{{ userInfo.attendanceRate }}%</div>
                <div class="stat-label">出勤率</div>
              </div>
              <div class="stat-item">
                <div class="stat-value">{{ userInfo.rank }}</div>
                <div class="stat-label">绩效等级</div>
              </div>
            </div>
          </el-card>
        </el-col>
        
        <el-col :xs="24" :md="16">
          <el-card shadow="hover">
            <template #header>
              <div class="card-header">
                <span>基本信息</span>
              </div>
            </template>
            
            <el-descriptions :column="2" border>
              <el-descriptions-item label="姓名">{{ userInfo.name }}</el-descriptions-item>
              <el-descriptions-item label="工号">{{ userInfo.employeeId }}</el-descriptions-item>
              <el-descriptions-item label="部门">{{ userInfo.departmentName }}</el-descriptions-item>
              <el-descriptions-item label="职位">{{ userInfo.positionName }}</el-descriptions-item>
              <el-descriptions-item label="入职日期">{{ userInfo.hireDate }}</el-descriptions-item>
              <el-descriptions-item label="状态">
                <el-tag :type="userInfo.status === 1 ? 'success' : 'danger'">
                  {{ userInfo.status === 1 ? '在职' : '离职' }}
                </el-tag>
              </el-descriptions-item>
              <el-descriptions-item label="基本工资">{{ formatCurrency(userInfo.baseSalary) }}</el-descriptions-item>
              <el-descriptions-item label="联系电话">{{ userInfo.phone }}</el-descriptions-item>
              <el-descriptions-item label="电子邮箱" :span="2">{{ userInfo.email }}</el-descriptions-item>
              <el-descriptions-item label="联系地址" :span="2">{{ userInfo.address }}</el-descriptions-item>
            </el-descriptions>
          </el-card>
          
          <el-card shadow="hover" class="bank-info-card">
            <template #header>
              <div class="card-header">
                <span>银行信息</span>
              </div>
            </template>
            
            <el-descriptions :column="2" border>
              <el-descriptions-item label="开户银行">{{ userInfo.bankName }}</el-descriptions-item>
              <el-descriptions-item label="银行账号">{{ maskBankAccount(userInfo.bankAccount) }}</el-descriptions-item>
              <el-descriptions-item label="开户支行">{{ userInfo.bankBranch }}</el-descriptions-item>
              <el-descriptions-item label="账户名">{{ userInfo.bankAccountName }}</el-descriptions-item>
            </el-descriptions>
          </el-card>
        </el-col>
      </el-row>
      
      <el-card shadow="hover" class="salary-history-card">
        <template #header>
          <div class="card-header">
            <span>最近工资记录</span>
            <el-button type="primary" link @click="viewMoreSalary">查看更多</el-button>
          </div>
        </template>
        
        <el-table :data="salaryRecords" style="width: 100%" stripe>
          <el-table-column prop="month" label="月份" width="120" />
          <el-table-column prop="baseSalary" label="基本工资" width="120">
            <template #default="{ row }">
              {{ formatCurrency(row.baseSalary) }}
            </template>
          </el-table-column>
          <el-table-column prop="bonus" label="奖金" width="120">
            <template #default="{ row }">
              {{ formatCurrency(row.bonus) }}
            </template>
          </el-table-column>
          <el-table-column prop="deduction" label="扣款" width="120">
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
          <el-table-column label="操作" width="120">
            <template #default="{ row }">
              <el-button type="primary" link size="small" @click="viewSalaryDetail(row)">
                查看详情
              </el-button>
            </template>
          </el-table-column>
        </el-table>
      </el-card>
    </div>
    
    <el-dialog
      v-model="editVisible"
      title="编辑个人信息"
      width="600px"
      :before-close="handleDialogClose"
    >
      <el-form
        ref="userFormRef"
        :model="userForm"
        :rules="userFormRules"
        label-width="100px"
      >
        <el-form-item label="手机号码" prop="phone">
          <el-input v-model="userForm.phone" placeholder="请输入手机号码" />
        </el-form-item>
        
        <el-form-item label="电子邮箱" prop="email">
          <el-input v-model="userForm.email" placeholder="请输入电子邮箱" />
        </el-form-item>
        
        <el-form-item label="联系地址" prop="address">
          <el-input v-model="userForm.address" placeholder="请输入联系地址" />
        </el-form-item>
        
        <el-form-item label="开户银行" prop="bankName">
          <el-input v-model="userForm.bankName" placeholder="请输入开户银行" />
        </el-form-item>
        
        <el-form-item label="银行账号" prop="bankAccount">
          <el-input v-model="userForm.bankAccount" placeholder="请输入银行账号" />
        </el-form-item>
        
        <el-form-item label="开户支行" prop="bankBranch">
          <el-input v-model="userForm.bankBranch" placeholder="请输入开户支行" />
        </el-form-item>
        
        <el-form-item label="账户名" prop="bankAccountName">
          <el-input v-model="userForm.bankAccountName" placeholder="请输入账户名" />
        </el-form-item>
      </el-form>
      
      <template #footer>
        <div class="dialog-footer">
          <el-button @click="handleDialogClose">取消</el-button>
          <el-button type="primary" @click="handleSaveUser" :loading="saving">保存</el-button>
        </div>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, FormInstance } from 'element-plus'
import defaultAvatar from '@/assets/avatar.png'

const router = useRouter()

// 用户信息
const userInfo = ref({
  id: 1,
  employeeId: 'EMP001',
  name: '张三',
  avatar: defaultAvatar,
  roleName: '研发工程师',
  workYears: 3,
  attendanceRate: 98,
  rank: 'A',
  departmentName: '研发部',
  positionName: '工程师',
  baseSalary: 15000,
  hireDate: '2020-01-01',
  phone: '13800138000',
  email: 'zhangsan@example.com',
  address: '北京市朝阳区XXX路XXX号',
  status: 1,
  bankName: '中国银行',
  bankAccount: '6222021234567890123',
  bankBranch: '北京朝阳支行',
  bankAccountName: '张三'
})

// 工资记录
const salaryRecords = ref([
  {
    id: 1,
    month: '2023-05',
    baseSalary: 15000,
    bonus: 3000,
    deduction: 500,
    socialSecurity: 2000,
    netSalary: 15500,
    status: 'paid'
  },
  {
    id: 2,
    month: '2023-04',
    baseSalary: 15000,
    bonus: 2500,
    deduction: 0,
    socialSecurity: 2000,
    netSalary: 15500,
    status: 'paid'
  },
  {
    id: 3,
    month: '2023-03',
    baseSalary: 15000,
    bonus: 2000,
    deduction: 300,
    socialSecurity: 2000,
    netSalary: 14700,
    status: 'paid'
  }
])

// 格式化货币
const formatCurrency = (value: number) => {
  return `¥${value.toFixed(2)}`
}

// 银行账号掩码
const maskBankAccount = (account: string) => {
  if (!account) return ''
  return account.replace(/^(\d{4})(\d+)(\d{4})$/, '$1****$3')
}

// 查看更多工资记录
const viewMoreSalary = () => {
  router.push('/salary/list')
}

// 查看工资详情
const viewSalaryDetail = (row: any) => {
  router.push(`/salary/detail/${row.id}`)
}

// 编辑信息
const editVisible = ref(false)
const userFormRef = ref<FormInstance>()
const saving = ref(false)

// 用户表单
const userForm = reactive({
  phone: '',
  email: '',
  address: '',
  bankName: '',
  bankAccount: '',
  bankBranch: '',
  bankAccountName: ''
})

// 表单验证规则
const userFormRules = {
  phone: [
    { required: true, message: '请输入手机号码', trigger: 'blur' },
    { pattern: /^1[3-9]\d{9}$/, message: '请输入正确的手机号码', trigger: 'blur' }
  ],
  email: [
    { required: true, message: '请输入电子邮箱', trigger: 'blur' },
    { type: 'email', message: '请输入正确的邮箱地址', trigger: 'blur' }
  ],
  address: [
    { required: true, message: '请输入联系地址', trigger: 'blur' }
  ],
  bankName: [
    { required: true, message: '请输入开户银行', trigger: 'blur' }
  ],
  bankAccount: [
    { required: true, message: '请输入银行账号', trigger: 'blur' },
    { pattern: /^\d{16,19}$/, message: '请输入正确的银行账号', trigger: 'blur' }
  ],
  bankBranch: [
    { required: true, message: '请输入开户支行', trigger: 'blur' }
  ],
  bankAccountName: [
    { required: true, message: '请输入账户名', trigger: 'blur' }
  ]
}

// 处理编辑
const handleEdit = () => {
  // 填充表单
  userForm.phone = userInfo.value.phone
  userForm.email = userInfo.value.email
  userForm.address = userInfo.value.address
  userForm.bankName = userInfo.value.bankName
  userForm.bankAccount = userInfo.value.bankAccount
  userForm.bankBranch = userInfo.value.bankBranch
  userForm.bankAccountName = userInfo.value.bankAccountName
  
  editVisible.value = true
}

// 处理关闭对话框
const handleDialogClose = () => {
  editVisible.value = false
  // 重置表单
  userFormRef.value?.resetFields()
}

// 处理保存用户信息
const handleSaveUser = () => {
  userFormRef.value?.validate((valid) => {
    if (valid) {
      saving.value = true
      
      // 模拟保存
      setTimeout(() => {
        // 更新用户信息
        userInfo.value.phone = userForm.phone
        userInfo.value.email = userForm.email
        userInfo.value.address = userForm.address
        userInfo.value.bankName = userForm.bankName
        userInfo.value.bankAccount = userForm.bankAccount
        userInfo.value.bankBranch = userForm.bankBranch
        userInfo.value.bankAccountName = userForm.bankAccountName
        
        saving.value = false
        editVisible.value = false
        
        ElMessage.success('保存成功')
      }, 1000)
    }
  })
}

onMounted(() => {
  // 这里可以加载用户信息
})
</script>

<style scoped lang="scss">
.user-profile {
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
  }
  
  .profile-content {
    .avatar-card {
      margin-bottom: 20px;
      
      .avatar-wrapper {
        display: flex;
        flex-direction: column;
        align-items: center;
        padding: 20px 0;
        
        .user-name {
          margin-top: 15px;
          margin-bottom: 5px;
          font-size: 18px;
        }
        
        .user-role {
          color: #909399;
          margin: 0;
        }
      }
      
      .user-stats {
        display: flex;
        justify-content: space-around;
        padding: 15px 0;
        border-top: 1px solid #ebeef5;
        
        .stat-item {
          text-align: center;
          
          .stat-value {
            font-size: 20px;
            font-weight: bold;
            color: #409eff;
          }
          
          .stat-label {
            font-size: 14px;
            color: #909399;
            margin-top: 5px;
          }
        }
      }
    }
    
    .bank-info-card, .salary-history-card {
      margin-top: 20px;
    }
    
    .card-header {
      display: flex;
      justify-content: space-between;
      align-items: center;
    }
  }
}
</style> 