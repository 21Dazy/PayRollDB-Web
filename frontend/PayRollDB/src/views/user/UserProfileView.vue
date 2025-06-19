<template>
  <div class="user-profile-container">
    <div class="profile-header">
      <h2>个人中心</h2>
      <p>查看和管理您的个人信息</p>
    </div>

    <el-tabs v-model="activeTab" type="border-card">
      <!-- 基本信息标签页 -->
      <el-tab-pane label="基本信息" name="basic">
        <div class="info-section">
          <div class="section-header">
            <h3>个人基本信息</h3>
            <el-button type="primary" @click="showChangeRequestDialog = true">
              申请修改信息
            </el-button>
          </div>
          
          <el-descriptions :column="2" border>
            <el-descriptions-item label="姓名">
              {{ profileData.employee_info?.name }}
            </el-descriptions-item>
            <el-descriptions-item label="部门">
              {{ profileData.employee_info?.department_name }}
            </el-descriptions-item>
            <el-descriptions-item label="职位">
              {{ profileData.employee_info?.position_name }}
            </el-descriptions-item>
            <el-descriptions-item label="入职日期">
              {{ formatDate(profileData.employee_info?.hire_date) }}
            </el-descriptions-item>
            <el-descriptions-item label="状态">
              <el-tag :type="getStatusType(profileData.employee_info?.status)">
                {{ profileData.employee_info?.status }}
              </el-tag>
            </el-descriptions-item>
            <el-descriptions-item label="手机号">
              {{ profileData.employee_info?.phone }}
            </el-descriptions-item>
            <el-descriptions-item label="邮箱">
              {{ profileData.employee_info?.email }}
            </el-descriptions-item>
            <el-descriptions-item label="地址" :span="2">
              {{ profileData.employee_info?.address }}
            </el-descriptions-item>
            <el-descriptions-item label="身份证号">
              {{ profileData.employee_info?.id_card }}
            </el-descriptions-item>
            <el-descriptions-item label="基本工资">
              ¥{{ formatMoney(profileData.employee_info?.base_salary) }}
            </el-descriptions-item>
          </el-descriptions>
        </div>

        <div class="info-section">
          <h3>银行信息</h3>
          <el-descriptions :column="2" border>
            <el-descriptions-item label="开户银行">
              {{ profileData.employee_info?.bank_name }}
            </el-descriptions-item>
            <el-descriptions-item label="银行账号">
              {{ profileData.employee_info?.bank_account }}
            </el-descriptions-item>
          </el-descriptions>
        </div>

        <div class="info-section">
          <h3>紧急联系人</h3>
          <el-descriptions :column="2" border>
            <el-descriptions-item label="联系人姓名">
              {{ profileData.employee_info?.emergency_contact_name }}
            </el-descriptions-item>
            <el-descriptions-item label="联系人关系">
              {{ profileData.employee_info?.emergency_contact_relationship }}
            </el-descriptions-item>
            <el-descriptions-item label="联系电话" :span="2">
              {{ profileData.employee_info?.emergency_contact_phone }}
            </el-descriptions-item>
          </el-descriptions>
        </div>
      </el-tab-pane>

      <!-- 变更申请标签页 -->
      <el-tab-pane label="变更申请" name="requests">
        <div class="requests-section">
          <div class="section-header">
            <h3>我的变更申请</h3>
            <el-button type="primary" @click="loadChangeRequests">刷新</el-button>
          </div>
          
          <el-table :data="changeRequests" style="width: 100%">
            <el-table-column prop="field_name" label="申请字段" width="120" />
            <el-table-column prop="old_value" label="原值" width="150">
              <template #default="scope">
                <span class="text-ellipsis">{{ scope.row.old_value }}</span>
              </template>
            </el-table-column>
            <el-table-column prop="new_value" label="新值" width="150">
              <template #default="scope">
                <span class="text-ellipsis">{{ scope.row.new_value }}</span>
              </template>
            </el-table-column>
            <el-table-column prop="status" label="状态" width="100">
              <template #default="scope">
                <el-tag :type="getRequestStatusType(scope.row.status)">
                  {{ scope.row.status }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="reason" label="申请理由" min-width="150">
              <template #default="scope">
                <span class="text-ellipsis">{{ scope.row.reason }}</span>
              </template>
            </el-table-column>
            <el-table-column prop="created_at" label="申请时间" width="160">
              <template #default="scope">
                {{ formatDateTime(scope.row.created_at) }}
              </template>
            </el-table-column>
            <el-table-column prop="reviewed_at" label="审核时间" width="160">
              <template #default="scope">
                {{ scope.row.reviewed_at ? formatDateTime(scope.row.reviewed_at) : '-' }}
              </template>
            </el-table-column>
            <el-table-column prop="admin_remark" label="审核备注" min-width="150">
              <template #default="scope">
                {{ scope.row.admin_remark || '-' }}
              </template>
            </el-table-column>
          </el-table>
        </div>
      </el-tab-pane>

      <!-- 个人设置标签页 -->
      <el-tab-pane label="个人设置" name="settings">
        <div class="settings-section">
          <div class="section-header">
            <h3>个人设置</h3>
            <el-button type="primary" @click="showSettingDialog = true">
              添加设置
            </el-button>
          </div>
          
          <el-table :data="userSettings" style="width: 100%">
            <el-table-column prop="setting_key" label="设置项" width="200" />
            <el-table-column prop="setting_value" label="设置值" min-width="200" />
            <el-table-column prop="description" label="描述" min-width="200" />
            <el-table-column prop="updated_at" label="更新时间" width="160">
              <template #default="scope">
                {{ formatDateTime(scope.row.updated_at) }}
              </template>
            </el-table-column>
            <el-table-column label="操作" width="150">
              <template #default="scope">
                <el-button 
                  size="small" 
                  @click="editSetting(scope.row)"
                >编辑</el-button>
                <el-button 
                  size="small" 
                  type="danger" 
                  @click="deleteSetting(scope.row)"
                >删除</el-button>
              </template>
            </el-table-column>
          </el-table>
        </div>
      </el-tab-pane>

      <!-- 活动日志标签页 -->
      <el-tab-pane label="活动日志" name="logs">
        <div class="logs-section">
          <div class="section-header">
            <h3>活动日志</h3>
            <el-select 
              v-model="logFilter" 
              placeholder="筛选操作类型" 
              clearable
              @change="loadActivityLogs"
              style="width: 200px;"
            >
              <el-option label="查看个人信息" value="查看个人信息" />
              <el-option label="查看薪资记录" value="查看薪资记录" />
              <el-option label="查看考勤记录" value="查看考勤记录" />
              <el-option label="提交信息变更申请" value="提交信息变更申请" />
              <el-option label="下载工资条" value="下载工资条" />
            </el-select>
          </div>
          
          <el-table :data="activityLogs" style="width: 100%">
            <el-table-column prop="action_type" label="操作类型" width="150" />
            <el-table-column prop="description" label="操作描述" min-width="200" />
            <el-table-column prop="resource_type" label="资源类型" width="120" />
            <el-table-column prop="ip_address" label="IP地址" width="130" />
            <el-table-column prop="created_at" label="操作时间" width="160">
              <template #default="scope">
                {{ formatDateTime(scope.row.created_at) }}
              </template>
            </el-table-column>
          </el-table>
          
          <div class="pagination">
            <el-pagination
              v-model:current-page="logPage"
              :page-size="logPageSize"
              :total="logTotal"
              layout="total, prev, pager, next"
              @current-change="loadActivityLogs"
            />
          </div>
        </div>
      </el-tab-pane>
    </el-tabs>

    <!-- 信息变更申请对话框 -->
    <el-dialog
      v-model="showChangeRequestDialog"
      title="申请修改信息"
      width="500px"
    >
      <el-form 
        ref="changeRequestFormRef"
        :model="changeRequestForm"
        :rules="changeRequestRules"
        label-width="100px"
      >
        <el-form-item label="修改字段" prop="field_name">
          <el-select v-model="changeRequestForm.field_name" placeholder="请选择要修改的字段">
            <el-option label="手机号" value="phone" />
            <el-option label="邮箱" value="email" />
            <el-option label="地址" value="address" />
            <el-option label="开户银行" value="bank_name" />
            <el-option label="银行账号" value="bank_account" />
            <el-option label="紧急联系人姓名" value="emergency_contact_name" />
            <el-option label="紧急联系人电话" value="emergency_contact_phone" />
            <el-option label="紧急联系人关系" value="emergency_contact_relationship" />
          </el-select>
        </el-form-item>
        
        <el-form-item label="当前值" prop="old_value">
          <el-input 
            v-model="changeRequestForm.old_value" 
            readonly 
            placeholder="自动填充当前值"
          />
        </el-form-item>
        
        <el-form-item label="新值" prop="new_value">
          <el-input 
            v-model="changeRequestForm.new_value" 
            placeholder="请输入新的值"
          />
        </el-form-item>
        
        <el-form-item label="申请理由" prop="reason">
          <el-input 
            v-model="changeRequestForm.reason" 
            type="textarea" 
            :rows="3"
            placeholder="请说明修改理由"
          />
        </el-form-item>
      </el-form>
      
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="showChangeRequestDialog = false">取消</el-button>
          <el-button type="primary" @click="submitChangeRequest">提交申请</el-button>
        </span>
      </template>
    </el-dialog>

    <!-- 个人设置对话框 -->
    <el-dialog
      v-model="showSettingDialog"
      :title="settingDialogTitle"
      width="500px"
    >
      <el-form 
        ref="settingFormRef"
        :model="settingForm"
        :rules="settingRules"
        label-width="100px"
      >
        <el-form-item label="设置项" prop="setting_key">
          <el-input 
            v-model="settingForm.setting_key" 
            placeholder="请输入设置项名称"
            :disabled="settingEditMode"
          />
        </el-form-item>
        
        <el-form-item label="设置值" prop="setting_value">
          <el-input 
            v-model="settingForm.setting_value" 
            placeholder="请输入设置值"
          />
        </el-form-item>
        
        <el-form-item label="描述" prop="description">
          <el-input 
            v-model="settingForm.description" 
            type="textarea" 
            :rows="3"
            placeholder="请输入设置描述（可选）"
          />
        </el-form-item>
      </el-form>
      
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="showSettingDialog = false">取消</el-button>
          <el-button type="primary" @click="submitSetting">
            {{ settingEditMode ? '保存' : '添加' }}
          </el-button>
        </span>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted, computed, watch } from 'vue'
import { ElMessage, ElMessageBox, type FormInstance } from 'element-plus'
import request from '@/utils/request'

// 当前激活的标签页
const activeTab = ref('basic')

// 个人资料数据
interface UserInfo {
  id: number;
  username: string;
  role: string;
  is_active: boolean;
  last_login: string | null;
}

interface EmployeeInfo {
  id: number;
  name: string;
  department_name: string;
  position_name: string;
  hire_date: string;
  status: string;
  phone: string;
  email: string;
  address: string;
  id_card: string;
  bank_name: string;
  bank_account: string;
  base_salary: number;
  emergency_contact_name: string;
  emergency_contact_phone: string;
  emergency_contact_relationship: string;
}

interface ProfileData {
  user_info: UserInfo;
  employee_info: EmployeeInfo;
}

const profileData = ref<ProfileData>({
  user_info: {
    id: 0,
    username: '',
    role: '',
    is_active: false,
    last_login: null
  },
  employee_info: {
    id: 0,
    name: '',
    department_name: '',
    position_name: '',
    hire_date: '',
    status: '',
    phone: '',
    email: '',
    address: '',
    id_card: '',
    bank_name: '',
    bank_account: '',
    base_salary: 0,
    emergency_contact_name: '',
    emergency_contact_phone: '',
    emergency_contact_relationship: ''
  }
})

// 添加调试数据
const rawResponseData = ref<any>(null)

// 变更申请数据
const changeRequests = ref([])

// 用户设置数据
const userSettings = ref([])

// 活动日志数据
const activityLogs = ref([])
const logFilter = ref('')
const logPage = ref(1)
const logPageSize = ref(20)
const logTotal = ref(0)

// 信息变更申请对话框
const showChangeRequestDialog = ref(false)
const changeRequestFormRef = ref<FormInstance>()
const changeRequestForm = reactive({
  field_name: '',
  old_value: '',
  new_value: '',
  reason: ''
})

// 个人设置对话框
const showSettingDialog = ref(false)
const settingFormRef = ref<FormInstance>()
const settingForm = reactive({
  setting_key: '',
  setting_value: '',
  description: ''
})
const settingEditMode = ref(false)
const currentEditingSetting = ref(null)

// 计算属性
const settingDialogTitle = computed(() => {
  return settingEditMode.value ? '编辑设置' : '添加设置'
})

// 验证规则
const changeRequestRules = {
  field_name: [
    { required: true, message: '请选择要修改的字段', trigger: 'change' }
  ],
  new_value: [
    { required: true, message: '请输入新值', trigger: 'blur' }
  ],
  reason: [
    { required: true, message: '请说明修改理由', trigger: 'blur' }
  ]
}

const settingRules = {
  setting_key: [
    { required: true, message: '请输入设置项名称', trigger: 'blur' }
  ],
  setting_value: [
    { required: true, message: '请输入设置值', trigger: 'blur' }
  ]
}

// 监听字段选择变化
watch(() => changeRequestForm.field_name, (newField) => {
  if (newField && profileData.value.employee_info) {
    const fieldMap: Record<string, string> = {
      phone: profileData.value.employee_info.phone,
      email: profileData.value.employee_info.email,
      address: profileData.value.employee_info.address,
      bank_name: profileData.value.employee_info.bank_name,
      bank_account: profileData.value.employee_info.bank_account,
      emergency_contact_name: profileData.value.employee_info.emergency_contact_name,
      emergency_contact_phone: profileData.value.employee_info.emergency_contact_phone,
      emergency_contact_relationship: profileData.value.employee_info.emergency_contact_relationship
    }
    changeRequestForm.old_value = fieldMap[newField] || ''
  }
})

// 工具函数
const formatDate = (dateStr: string) => {
  if (!dateStr) return '-'
  return new Date(dateStr).toLocaleDateString()
}

const formatDateTime = (dateStr: string) => {
  if (!dateStr) return '-'
  return new Date(dateStr).toLocaleString()
}

const formatMoney = (amount: number) => {
  if (!amount) return '0.00'
  return amount.toLocaleString('zh-CN', { minimumFractionDigits: 2, maximumFractionDigits: 2 })
}

const getStatusType = (status: string) => {
  const statusMap: Record<string, string> = {
    '在职': 'success',
    '离职': 'danger',
    '试用期': 'warning'
  }
  return statusMap[status] || 'info'
}

const getRequestStatusType = (status: string) => {
  const statusMap: Record<string, string> = {
    '待审核': 'warning',
    '已通过': 'success',
    '已拒绝': 'danger'
  }
  return statusMap[status] || 'info'
}

// API 调用函数
const loadProfile = async () => {
  try {
    const response: any = await request.get('/api/v1/user/profile/profile')
    console.log('API返回的原始数据:', response)
    rawResponseData.value = response
    
    // 确保数据结构正确
    if (response && typeof response === 'object') {
      profileData.value = {
        user_info: response.user_info || profileData.value.user_info,
        employee_info: response.employee_info || profileData.value.employee_info
      }
      console.log('处理后的profileData:', profileData.value)
    } else {
      console.error('API返回的数据格式不正确:', response)
    }
  } catch (error: any) {
    console.error('加载个人信息失败:', error)
    ElMessage.error(error.response?.data?.detail || '加载个人信息失败')
  }
}

const loadChangeRequests = async () => {
  try {
    const response = await request.get('/api/v1/user/profile/change-requests')
    changeRequests.value = response.data
  } catch (error: any) {
    ElMessage.error(error.response?.data?.detail || '加载变更申请失败')
  }
}

const loadUserSettings = async () => {
  try {
    const response = await request.get('/api/v1/user/profile/settings')
    userSettings.value = response.data
  } catch (error: any) {
    ElMessage.error(error.response?.data?.detail || '加载个人设置失败')
  }
}

const loadActivityLogs = async () => {
  try {
    const params = {
      skip: (logPage.value - 1) * logPageSize.value,
      limit: logPageSize.value,
      action_type: logFilter.value || undefined
    }
    const response = await request.get('/api/v1/user/profile/activity-logs', { params })
    activityLogs.value = response.data.logs
    logTotal.value = response.data.total
  } catch (error: any) {
    ElMessage.error(error.response?.data?.detail || '加载活动日志失败')
  }
}

// 事件处理函数
const submitChangeRequest = () => {
  changeRequestFormRef.value?.validate(async (valid) => {
    if (valid) {
      try {
        await request.post('/api/v1/user/profile/change-requests', changeRequestForm)
        ElMessage.success('变更申请提交成功')
        showChangeRequestDialog.value = false
        loadChangeRequests()
        // 重置表单
        Object.assign(changeRequestForm, {
          field_name: '',
          old_value: '',
          new_value: '',
          reason: ''
        })
      } catch (error: any) {
        ElMessage.error(error.response?.data?.detail || '提交变更申请失败')
      }
    }
  })
}

const submitSetting = () => {
  settingFormRef.value?.validate(async (valid) => {
    if (valid) {
      try {
        if (settingEditMode.value) {
          await request.put(`/api/v1/user/profile/settings/${settingForm.setting_key}`, {
            setting_value: settingForm.setting_value,
            description: settingForm.description
          })
          ElMessage.success('设置更新成功')
        } else {
          await request.post('/api/v1/user/profile/settings', settingForm)
          ElMessage.success('设置添加成功')
        }
        
        showSettingDialog.value = false
        loadUserSettings()
        resetSettingForm()
      } catch (error: any) {
        ElMessage.error(error.response?.data?.detail || '操作失败')
      }
    }
  })
}

const editSetting = (setting: any) => {
  settingEditMode.value = true
  currentEditingSetting.value = setting
  Object.assign(settingForm, {
    setting_key: setting.setting_key,
    setting_value: setting.setting_value,
    description: setting.description
  })
  showSettingDialog.value = true
}

const deleteSetting = (setting: any) => {
  ElMessageBox.confirm(
    `确定要删除设置项"${setting.setting_key}"吗？`,
    '确认删除',
    {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning',
    }
  ).then(async () => {
    try {
      await request.delete(`/api/v1/user/profile/settings/${setting.setting_key}`)
      ElMessage.success('设置删除成功')
      loadUserSettings()
    } catch (error: any) {
      ElMessage.error(error.response?.data?.detail || '删除失败')
    }
  })
}

const resetSettingForm = () => {
  settingEditMode.value = false
  currentEditingSetting.value = null
  Object.assign(settingForm, {
    setting_key: '',
    setting_value: '',
    description: ''
  })
}

// 监听设置对话框关闭
watch(() => showSettingDialog.value, (newVal) => {
  if (!newVal) {
    resetSettingForm()
  }
})

// 组件挂载时加载数据
onMounted(() => {
  console.log('组件已挂载，开始加载数据')
  loadProfile()
  loadChangeRequests()
  loadUserSettings()
  loadActivityLogs()
})
</script>

<style scoped lang="scss">
.user-profile-container {
  padding: 20px;
}

.profile-header {
  margin-bottom: 20px;
  
  h2 {
    color: #333;
    font-size: 24px;
    margin-bottom: 8px;
  }
  
  p {
    color: #666;
    margin: 0;
  }
}

.info-section {
  margin-bottom: 30px;
  
  h3 {
    color: #333;
    font-size: 16px;
    margin-bottom: 15px;
  }
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
  
  h3 {
    color: #333;
    font-size: 16px;
    margin: 0;
  }
}

.requests-section,
.settings-section,
.logs-section {
  .text-ellipsis {
    display: inline-block;
    max-width: 140px;
    overflow: hidden;
    white-space: nowrap;
    text-overflow: ellipsis;
    vertical-align: middle;
  }
}

.pagination {
  margin-top: 20px;
  text-align: center;
}

.dialog-footer {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
}

// 标签页样式调整
:deep(.el-tabs--border-card) {
  border: 1px solid #dcdfe6;
  border-radius: 4px;
  
  .el-tabs__header {
    background-color: #f5f7fa;
    border-bottom: 1px solid #dcdfe6;
    margin: 0;
  }
  
  .el-tabs__content {
    padding: 20px;
  }
}

// 描述列表样式调整
:deep(.el-descriptions) {
  .el-descriptions__label {
    font-weight: 600;
    color: #333;
  }
}

// 响应式设计
@media (max-width: 768px) {
  .user-profile-container {
    padding: 15px;
  }
  
  .section-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 10px;
  }
  
  :deep(.el-descriptions) {
    .el-descriptions__table {
      .el-descriptions__cell {
        padding: 8px 10px;
      }
    }
  }
  
  .requests-section,
  .settings-section,
  .logs-section {
    .text-ellipsis {
      max-width: 80px;
    }
  }
}
</style> 