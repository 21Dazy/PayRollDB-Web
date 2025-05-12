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
        <el-form-item label="姓名/工号">
          <el-input v-model="searchForm.keyword" placeholder="请输入姓名或工号" clearable />
        </el-form-item>
        <el-form-item label="考勤状态">
          <el-select v-model="searchForm.status" placeholder="请选择状态" clearable>
            <el-option label="正常" value="正常" />
            <el-option label="迟到" value="迟到" />
            <el-option label="早退" value="早退" />
            <el-option label="缺勤" value="缺勤" />
            <el-option label="请假" value="请假" />
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
        <el-table-column prop="date" label="日期" width="120" sortable />
        <el-table-column prop="employeeId" label="工号" width="100" />
        <el-table-column prop="employeeName" label="姓名" width="100" />
        <el-table-column prop="departmentName" label="部门" width="100" />
        <el-table-column prop="checkInTime" label="签到时间" width="120" />
        <el-table-column prop="checkOutTime" label="签退时间" width="120" />
        <el-table-column prop="status" label="状态" width="100">
          <template #default="{ row }">
            <el-tag :type="getStatusType(row.status)">
              {{ row.status }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="overtimeHours" label="加班时长" width="100">
          <template #default="{ row }">
            {{ row.overtimeHours ? `${row.overtimeHours}小时` : '-' }}
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
        :total="total"
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
        <el-form-item label="员工" prop="employeeId">
          <el-select v-model="form.employeeId" placeholder="请选择员工" style="width: 100%">
            <el-option
              v-for="item in employeeOptions"
              :key="item.value"
              :label="item.label"
              :value="item.value"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="签到时间" prop="checkInTime">
          <el-time-picker
            v-model="form.checkInTime"
            format="HH:mm:ss"
            placeholder="选择时间"
            style="width: 100%"
          />
        </el-form-item>
        <el-form-item label="签退时间" prop="checkOutTime">
          <el-time-picker
            v-model="form.checkOutTime"
            format="HH:mm:ss"
            placeholder="选择时间"
            style="width: 100%"
          />
        </el-form-item>
        <el-form-item label="状态" prop="status">
          <el-select v-model="form.status" placeholder="请选择状态" style="width: 100%">
            <el-option label="正常" value="正常" />
            <el-option label="迟到" value="迟到" />
            <el-option label="早退" value="早退" />
            <el-option label="缺勤" value="缺勤" />
            <el-option label="病假" value="病假" />
            <el-option label="事假" value="事假" />
          </el-select>
        </el-form-item>
        <el-form-item label="加班时长" prop="overtimeHours">
          <el-input-number
            v-model="form.overtimeHours"
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
import { ref, reactive, onMounted } from 'vue'
import { ElMessage, ElMessageBox, FormInstance } from 'element-plus'
import { Plus, Search, Refresh, Upload, Download } from '@element-plus/icons-vue'

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
const departmentOptions = ref([
  { value: '1', label: '研发部' },
  { value: '2', label: '市场部' },
  { value: '3', label: '销售部' },
  { value: '4', label: '财务部' },
  { value: '5', label: '人事部' }
])

// 员工选项
const employeeOptions = ref([
  { value: 'EMP001', label: '张三 (EMP001)' },
  { value: 'EMP002', label: '李四 (EMP002)' },
  { value: 'EMP003', label: '王五 (EMP003)' },
  { value: 'EMP004', label: '赵六 (EMP004)' },
  { value: 'EMP005', label: '钱七 (EMP005)' }
])

// 搜索表单
const searchForm = reactive({
  dateRange: [],
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

// 对话框相关
const dialogVisible = ref(false)
const isEdit = ref(false)
const formRef = ref<FormInstance>()
const form = reactive({
  id: '',
  date: '',
  employeeId: '',
  checkInTime: '',
  checkOutTime: '',
  status: '正常',
  overtimeHours: 0,
  remarks: ''
})

// 表单验证规则
const rules = {
  date: [
    { required: true, message: '请选择日期', trigger: 'change' }
  ],
  employeeId: [
    { required: true, message: '请选择员工', trigger: 'change' }
  ],
  checkInTime: [
    { required: true, message: '请选择签到时间', trigger: 'change' }
  ],
  status: [
    { required: true, message: '请选择状态', trigger: 'change' }
  ]
}

// 获取考勤记录数据
const fetchData = () => {
  loading.value = true
  
  // 模拟API调用
  setTimeout(() => {
    // 模拟数据
    const mockData = []
    
    for (let i = 0; i < 10; i++) {
      const date = new Date()
      date.setDate(date.getDate() - i)
      
      const statuses = ['正常', '迟到', '早退', '缺勤', '病假', '事假']
      const status = statuses[Math.floor(Math.random() * statuses.length)]
      
      // 根据状态设置不同的时间
      let checkInTime = '09:00:00'
      let checkOutTime = '18:00:00'
      let overtimeHours = 0
      
      if (status === '迟到') {
        checkInTime = '09:' + (Math.floor(Math.random() * 30) + 15) + ':00'
      } else if (status === '早退') {
        checkOutTime = '17:' + Math.floor(Math.random() * 30) + ':00'
      } else if (status === '缺勤') {
        checkInTime = ''
        checkOutTime = ''
      } else if (Math.random() > 0.7) {
        // 加班
        overtimeHours = Math.floor(Math.random() * 4) + 1
        checkOutTime = (18 + Math.floor(overtimeHours)) + ':00:00'
      }
      
      mockData.push({
        id: i + 1,
        date: date.toISOString().split('T')[0],
        employeeId: 'EMP00' + (i % 5 + 1),
        employeeName: ['张三', '李四', '王五', '赵六', '钱七'][i % 5],
        departmentName: ['研发部', '市场部', '销售部', '财务部', '人事部'][i % 5],
        departmentId: (i % 5 + 1).toString(),
        checkInTime,
        checkOutTime,
        status,
        overtimeHours: status === '正常' ? overtimeHours : 0,
        remarks: status === '正常' ? (overtimeHours > 0 ? '加班处理项目' : '') : '系统自动记录'
      })
    }
    
    tableData.value = mockData
    total.value = 68 // 模拟总数
    loading.value = false
  }, 500)
}

// 获取状态对应的标签类型
const getStatusType = (status: string) => {
  const map = {
    '正常': 'success',
    '迟到': 'warning',
    '早退': 'warning',
    '缺勤': 'danger',
    '病假': 'info',
    '事假': 'info'
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
  searchForm.keyword = ''
  searchForm.status = ''
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
  form.employeeId = ''
  form.checkInTime = new Date(new Date().setHours(9, 0, 0))
  form.checkOutTime = new Date(new Date().setHours(18, 0, 0))
  form.status = '正常'
  form.overtimeHours = 0
  form.remarks = ''
  
  dialogVisible.value = true
}

// 编辑考勤记录
const handleEdit = (row) => {
  isEdit.value = true
  form.id = row.id
  form.date = row.date
  form.employeeId = row.employeeId
  
  // 转换时间字符串为Date对象
  if (row.checkInTime) {
    const [hours, minutes, seconds] = row.checkInTime.split(':').map(Number)
    form.checkInTime = new Date(new Date().setHours(hours, minutes, seconds))
  } else {
    form.checkInTime = null
  }
  
  if (row.checkOutTime) {
    const [hours, minutes, seconds] = row.checkOutTime.split(':').map(Number)
    form.checkOutTime = new Date(new Date().setHours(hours, minutes, seconds))
  } else {
    form.checkOutTime = null
  }
  
  form.status = row.status
  form.overtimeHours = row.overtimeHours || 0
  form.remarks = row.remarks || ''
  
  dialogVisible.value = true
}

// 保存考勤记录
const handleSave = () => {
  formRef.value?.validate((valid) => {
    if (valid) {
      // 实际项目中应该调用API
      if (isEdit.value) {
        // 更新现有记录
        const index = tableData.value.findIndex(item => item.id === form.id)
        if (index !== -1) {
          // 获取员工信息
          const employee = employeeOptions.value.find(item => item.value === form.employeeId)
          const employeeName = employee ? employee.label.split(' ')[0] : ''
          
          // 更新数据
          tableData.value[index] = {
            ...tableData.value[index],
            date: form.date,
            employeeId: form.employeeId,
            employeeName,
            checkInTime: form.checkInTime ? form.checkInTime.toTimeString().split(' ')[0] : '',
            checkOutTime: form.checkOutTime ? form.checkOutTime.toTimeString().split(' ')[0] : '',
            status: form.status,
            overtimeHours: form.overtimeHours,
            remarks: form.remarks
          }
          
          ElMessage.success('考勤记录更新成功')
        }
      } else {
        // 添加新记录
        // 获取员工信息
        const employee = employeeOptions.value.find(item => item.value === form.employeeId)
        const employeeName = employee ? employee.label.split(' ')[0] : ''
        const department = Math.floor(Math.random() * 5)
        
        // 创建新记录
        const newRecord = {
          id: tableData.value.length + 1,
          date: form.date,
          employeeId: form.employeeId,
          employeeName,
          departmentName: ['研发部', '市场部', '销售部', '财务部', '人事部'][department],
          departmentId: (department + 1).toString(),
          checkInTime: form.checkInTime ? form.checkInTime.toTimeString().split(' ')[0] : '',
          checkOutTime: form.checkOutTime ? form.checkOutTime.toTimeString().split(' ')[0] : '',
          status: form.status,
          overtimeHours: form.overtimeHours,
          remarks: form.remarks
        }
        
        // 添加到表格数据
        tableData.value.unshift(newRecord)
        total.value++
        
        ElMessage.success('考勤记录添加成功')
      }
      
      dialogVisible.value = false
    }
  })
}

// 删除考勤记录
const handleDelete = (row) => {
  ElMessageBox.confirm(
    `确定要删除 ${row.employeeName} 在 ${row.date} 的考勤记录吗？`,
    '删除确认',
    {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning',
    }
  ).then(() => {
    // 实际项目中应该调用API
    const index = tableData.value.findIndex(item => item.id === row.id)
    if (index !== -1) {
      tableData.value.splice(index, 1)
      total.value--
      ElMessage.success('考勤记录删除成功')
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