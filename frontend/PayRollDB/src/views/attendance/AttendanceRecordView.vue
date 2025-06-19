<template>
  <div class="attendance-record">
    <div class="page-header">
      <h2>考勤记录</h2>
      <div class="page-actions">
        <el-button type="primary" :icon="Plus" @click="handleAdd">添加记录</el-button>
        <el-button :icon="Upload" @click="handleImport">批量导入</el-button>
        <el-button :icon="Download" @click="handleExport">导出报表</el-button>
      </div>
    </div>
    
    <div class="search-bar">
      <el-form :inline="true" :model="searchForm" class="search-form">
        <el-form-item label="日期">
          <el-date-picker
            v-model="searchForm.dateRange"
            type="daterange"
            range-separator="至"
            start-placeholder="开始日期"
            end-placeholder="结束日期"
            :shortcuts="dateShortcuts"
          />
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
        <el-form-item label="员工ID">
          <el-input v-model="searchForm.employeeId" placeholder="请输入员工ID" clearable />
        </el-form-item>
        <el-form-item label="考勤状态">
          <el-select v-model="searchForm.statusId" placeholder="请选择状态" clearable>
            <el-option 
              v-for="status in attendanceStatuses" 
              :key="status.id" 
              :label="status.name" 
              :value="status.id" 
            />
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
        :data="attendances"
        style="width: 100%"
        border
        stripe
        v-loading="isLoading"
      >
        <el-table-column type="selection" width="55" />
        <el-table-column prop="date" label="日期" width="120" sortable />
        <el-table-column prop="employee.employee_id" label="工号" width="100" />
        <el-table-column prop="employee.name" label="姓名" width="100" />
        <el-table-column prop="employee.department.name" label="部门" width="100" />
        <el-table-column prop="status.name" label="状态" width="100">
          <template #default="{ row }">
            <el-tag :type="getStatusType(row.status.name)">
              {{ row.status.name }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="overtime_hours" label="加班时长" width="100">
          <template #default="{ row }">
            {{ row.overtime_hours ? `${row.overtime_hours}小时` : '-' }}
          </template>
        </el-table-column>
        <el-table-column prop="remarks" label="备注" />
        <el-table-column fixed="right" label="操作" width="150">
          <template #default="{ row }">
            <el-button link type="primary" size="small" @click="handleEdit(row)">编辑</el-button>
            <el-button link type="danger" size="small" @click="handleDelete(row)">删除</el-button>
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
        :total="totalCount"
        @size-change="handleSizeChange"
        @current-change="handleCurrentChange"
      />
    </div>
    
    <!-- 添加/编辑考勤记录弹窗 -->
    <el-dialog
      v-model="dialogVisible"
      :title="isEdit ? '编辑考勤记录' : '添加考勤记录'"
      width="600px"
    >
      <el-form
        ref="formRef"
        :model="form"
        :rules="rules"
        label-width="100px"
      >
        <el-form-item label="日期" prop="date">
          <el-date-picker
            v-model="form.date"
            type="date"
            placeholder="选择日期"
            style="width: 100%"
          />
        </el-form-item>
        <el-form-item label="员工" prop="employee_id">
          <el-select v-model="form.employee_id" placeholder="请选择员工" style="width: 100%">
            <el-option
              v-for="item in employeeOptions"
              :key="item.value"
              :label="item.label"
              :value="item.value"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="状态" prop="status_id">
          <el-select v-model="form.status_id" placeholder="请选择状态" style="width: 100%">
            <el-option 
              v-for="status in attendanceStatuses" 
              :key="status.id" 
              :label="status.name" 
              :value="status.id" 
            />
          </el-select>
        </el-form-item>
        <el-form-item label="加班时长" prop="overtime_hours">
          <el-input-number
            v-model="form.overtime_hours"
            :min="0"
            :max="24"
            :precision="1"
            :step="0.5"
            style="width: 100%"
          />
        </el-form-item>
        <el-form-item label="备注" prop="remarks">
          <el-input
            v-model="form.remarks"
            type="textarea"
            :rows="3"
            placeholder="请输入备注"
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <div class="dialog-footer">
          <el-button @click="dialogVisible = false">取消</el-button>
          <el-button type="primary" @click="handleSave">确认</el-button>
        </div>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted, computed } from 'vue'
import { ElMessage, ElMessageBox, FormInstance } from 'element-plus'
import { Plus, Search, Refresh, Upload, Download } from '@element-plus/icons-vue'
import { useAttendanceStore } from '@/stores/attendance'
import { storeToRefs } from 'pinia'
import { useDepartmentsStore } from '@/stores/departments'
import { useEmployeesStore } from '@/stores/employees'

// 初始化store
const attendanceStore = useAttendanceStore()
const departmentsStore = useDepartmentsStore()
const employeesStore = useEmployeesStore()

// 从store获取数据
const { attendances, attendanceStatuses, totalCount, isLoading, error } = storeToRefs(attendanceStore)

// 日期快捷选项
const dateShortcuts = [
  {
    text: '最近一周',
    value: () => {
      const end = new Date()
      const start = new Date()
      start.setTime(start.getTime() - 3600 * 1000 * 24 * 7)
      return [start, end]
    },
  },
  {
    text: '最近一个月',
    value: () => {
      const end = new Date()
      const start = new Date()
      start.setTime(start.getTime() - 3600 * 1000 * 24 * 30)
      return [start, end]
    },
  },
  {
    text: '最近三个月',
    value: () => {
      const end = new Date()
      const start = new Date()
      start.setTime(start.getTime() - 3600 * 1000 * 24 * 90)
      return [start, end]
    },
  },
]

// 部门选项
const departmentOptions = ref([])

// 员工选项
const employeeOptions = ref([])

// 加载部门和员工数据
const loadOptions = async () => {
  try {
    // 加载部门数据
    await departmentsStore.getDepartments()
    departmentOptions.value = departmentsStore.departments.map(dept => ({
      value: dept.id,
      label: dept.name
    }))
    
    // 加载员工数据
    await employeesStore.getEmployees()
    employeeOptions.value = employeesStore.employees.map(emp => ({
      value: emp.id,
      label: `${emp.name} (${emp.employee_id})`
    }))
    
    // 加载考勤状态
    await attendanceStore.getAttendanceStatuses()
  } catch (err) {
    ElMessage.error('加载选项数据失败')
  }
}

// 搜索表单
const searchForm = reactive({
  dateRange: [],
  departmentId: '',
  employeeId: '',
  statusId: ''
})

// 分页
const currentPage = ref(1)
const pageSize = ref(10)

// 对话框相关
const dialogVisible = ref(false)
const isEdit = ref(false)
const formRef = ref<FormInstance>()
const form = reactive({
  id: '',
  date: new Date(),
  employee_id: '',
  status_id: '',
  overtime_hours: 0,
  remarks: ''
})

// 表单验证规则
const rules = {
  date: [
    { required: true, message: '请选择日期', trigger: 'change' }
  ],
  employee_id: [
    { required: true, message: '请选择员工', trigger: 'change' }
  ],
  status_id: [
    { required: true, message: '请选择状态', trigger: 'change' }
  ]
}

// 获取考勤记录数据
const fetchData = async () => {
  try {
    const params = {
      skip: (currentPage.value - 1) * pageSize.value,
      limit: pageSize.value,
      department_id: searchForm.departmentId || undefined,
      employee_id: searchForm.employeeId || undefined,
      status_id: searchForm.statusId || undefined,
      start_date: searchForm.dateRange && searchForm.dateRange[0] ? searchForm.dateRange[0].toISOString().split('T')[0] : undefined,
      end_date: searchForm.dateRange && searchForm.dateRange[1] ? searchForm.dateRange[1].toISOString().split('T')[0] : undefined
    }
    
    await attendanceStore.getAttendances(params)
  } catch (err) {
    ElMessage.error('获取考勤记录失败')
  }
}

// 获取状态对应的标签类型
const getStatusType = (status: string) => {
  const map = {
    '正常': 'success',
    '迟到': 'warning',
    '早退': 'warning',
    '缺勤': 'danger',
    '病假': 'info',
    '事假': 'info',
    '年假': 'info'
  }
  return map[status] || 'info'
}

// 处理查询
const handleSearch = () => {
  currentPage.value = 1
  fetchData()
}

// 处理重置
const handleReset = () => {
  searchForm.dateRange = []
  searchForm.departmentId = ''
  searchForm.employeeId = ''
  searchForm.statusId = ''
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

// 添加考勤记录
const handleAdd = () => {
  isEdit.value = false
  form.id = ''
  form.date = new Date()
  form.employee_id = ''
  form.status_id = ''
  form.overtime_hours = 0
  form.remarks = ''
  
  dialogVisible.value = true
}

// 编辑考勤记录
const handleEdit = (row) => {
  isEdit.value = true
  form.id = row.id
  form.date = new Date(row.date)
  form.employee_id = row.employee.id
  form.status_id = row.status.id
  form.overtime_hours = row.overtime_hours || 0
  form.remarks = row.remarks || ''
  
  dialogVisible.value = true
}

// 保存考勤记录
const handleSave = async () => {
  formRef.value?.validate(async (valid) => {
    if (valid) {
      try {
        const attendanceData = {
          employee_id: form.employee_id,
          date: form.date.toISOString().split('T')[0],
          status_id: form.status_id,
          overtime_hours: form.overtime_hours,
          remarks: form.remarks
        }
        
        if (isEdit.value) {
          // 更新现有记录
          await attendanceStore.updateAttendance(form.id, attendanceData)
          ElMessage.success('考勤记录更新成功')
        } else {
          // 添加新记录
          await attendanceStore.createAttendance(attendanceData)
          ElMessage.success('考勤记录添加成功')
        }
        
        dialogVisible.value = false
        fetchData() // 重新加载数据
      } catch (err: any) {
        ElMessage.error(err.message || '操作失败')
      }
    }
  })
}

// 删除考勤记录
const handleDelete = (row) => {
  ElMessageBox.confirm(
    `确定要删除 ${row.employee.name} 在 ${row.date} 的考勤记录吗？`,
    '删除确认',
    {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning',
    }
  ).then(async () => {
    try {
      await attendanceStore.deleteAttendance(row.id)
      ElMessage.success('考勤记录删除成功')
      fetchData() // 重新加载数据
    } catch (err: any) {
      ElMessage.error(err.message || '删除失败')
    }
  }).catch(() => {
    ElMessage.info('已取消删除')
  })
}

// 批量导入
const handleImport = () => {
  ElMessage.info('批量导入功能待实现')
}

// 导出报表
const handleExport = () => {
  ElMessage.success('考勤报表导出成功')
}

onMounted(() => {
  loadOptions()
  fetchData()
})
</script>

<style scoped lang="scss">
.attendance-record {
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