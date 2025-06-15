<template>
  <div class="position-list">
    <div class="page-header">
      <h2>职位列表</h2>
      <div class="page-actions">
        <el-button type="primary" :icon="Plus" @click="handleAdd">添加职位</el-button>
      </div>
    </div>
    
    <div class="search-bar">
      <el-form :inline="true" :model="searchForm" class="search-form">
        <el-form-item label="关键词">
          <el-input v-model="searchForm.keyword" placeholder="职位名称" clearable />
        </el-form-item>
        <el-form-item label="部门">
          <el-select v-model="searchForm.department_id" placeholder="请选择部门" clearable>
            <el-option
              v-for="item in departmentOptions"
              :key="item.value"
              :label="item.label"
              :value="item.value"
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
        :data="tableData"
        style="width: 100%"
        border
        stripe
        v-loading="loading"
      >
        <el-table-column type="selection" width="55" />
        <el-table-column prop="id" label="职位编号" width="100" />
        <el-table-column prop="name" label="职位名称" width="150" />
        <el-table-column prop="departmentName" label="所属部门" width="150" />
        <el-table-column prop="description" label="职位描述" />
        <el-table-column prop="salaryRange" label="薪资范围" width="180" />
        <el-table-column prop="createdAt" label="创建时间" width="180" />
        <el-table-column fixed="right" label="操作" width="200">
          <template #default="{ row }">
            <el-button link type="primary" size="small" @click="handleView(row)">查看</el-button>
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
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted, computed } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus, Search, Refresh } from '@element-plus/icons-vue'
import { usePositionsStore } from '@/stores/positions'
import { useDepartmentsStore } from '@/stores/departments'

const router = useRouter()

// 引入store
const positionsStore = usePositionsStore()
const departmentsStore = useDepartmentsStore()

// 搜索表单
const searchForm = reactive({
  keyword: '',
  department_id: ''
})

// 部门选项
const departmentOptions = computed(() => {
  return (departmentsStore.departments || []).map(dept => ({
    value: dept.id,
    label: dept.name
  }))
})

// 表格数据
const tableData = computed(() => {
  const positions = positionsStore.positions || [];
  console.log('构建表格数据:', positions);
  
  return positions.map(pos => ({
    id: pos.id,
    name: pos.name,
    departmentName: pos.department_name || '-',
    description: pos.description || '-',
    salaryRange: formatSalaryRange(pos.salary_range_min, pos.salary_range_max),
    createdAt: formatDate(pos.created_at)
  }));
})

// 分页
const currentPage = ref(1)
const pageSize = ref(10)
const total = computed(() => positionsStore.totalCount)

// 加载状态
const loading = computed(() => positionsStore.isLoading)

// 格式化日期
const formatDate = (dateStr: string) => {
  if (!dateStr) return '-'
  const date = new Date(dateStr)
  return date.toLocaleString('zh-CN', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit'
  })
}

// 格式化薪资范围
const formatSalaryRange = (min?: number, max?: number) => {
  if (!min && !max) return '-'
  if (min && !max) return `¥${min.toFixed(2)} 以上`
  if (!min && max) return `¥${max.toFixed(2)} 以下`
  return `¥${min.toFixed(2)} ~ ¥${max.toFixed(2)}`
}

// 获取职位列表数据
const fetchData = async () => {
  try {
    const params: any = {
      skip: (currentPage.value - 1) * pageSize.value,
      limit: pageSize.value
    }
    
    if (searchForm.keyword) {
      params.keyword = searchForm.keyword
    }
    
    if (searchForm.department_id) {
      params.department_id = searchForm.department_id
    }
    
    console.log('请求职位数据参数:', params)
    
    const response = await positionsStore.getPositions(params)
    console.log('职位数据响应:', response)
    console.log('当前 store 中的职位数据:', positionsStore.positions)
    
  } catch (error: any) {
    ElMessage.error(`获取职位列表失败: ${error.message || '未知错误'}`)
  }
}

// 处理查询
const handleSearch = () => {
  currentPage.value = 1
  fetchData()
}

// 处理重置
const handleReset = () => {
  searchForm.keyword = ''
  searchForm.department_id = ''
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

// 添加职位
const handleAdd = () => {
  router.push('/position/add')
}

// 查看职位
const handleView = (row: any) => {
  router.push(`/position/view/${row.id}`)
}

// 编辑职位
const handleEdit = (row: any) => {
  router.push(`/position/edit/${row.id}`)
}

// 删除职位
const handleDelete = (row: any) => {
  ElMessageBox.confirm(
    `确定要删除职位 ${row.name} 吗？`,
    '删除确认',
    {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning',
    }
  ).then(async () => {
    try {
      await positionsStore.deletePosition(row.id)
      ElMessage.success('删除成功')
      fetchData() // 重新加载数据
    } catch (error: any) {
      ElMessage.error(`删除失败: ${error.message || '未知错误'}`)
    }
  }).catch(() => {
    // 取消操作
  })
}

// 初始化
onMounted(async () => {
  try {
    // 确保先加载部门数据
    await departmentsStore.getDepartments();
    
    // 再加载职位数据
    await fetchData();
    
    console.log('挂载后的职位数据:', positionsStore.positions);
  } catch (error: any) {
    ElMessage.error(`初始化数据失败: ${error.message || '未知错误'}`);
  }
})
</script>

<style scoped lang="scss">
.position-list {
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