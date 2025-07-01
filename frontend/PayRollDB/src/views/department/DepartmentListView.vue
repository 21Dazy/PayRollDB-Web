<template>
  <div class="department-list">
    <div class="page-header">
      <h2>部门列表</h2>
      <div class="page-actions">
        <el-button type="primary" :icon="Plus" @click="handleAdd">添加部门</el-button>
      </div>
    </div>
    
    <div class="search-bar">
      <el-form :inline="true" :model="searchForm" class="search-form">
        <el-form-item label="关键词">
          <el-input v-model="searchForm.keyword" placeholder="部门名称" clearable />
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
        <el-table-column prop="id" label="部门编号" width="100" />
        <el-table-column prop="name" label="部门名称" width="180" />
        <el-table-column prop="description" label="部门描述" />
        <el-table-column prop="employeeCount" label="员工数量" width="100" />
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
import { ref, reactive, onMounted, onActivated, computed, watch } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus, Search, Refresh } from '@element-plus/icons-vue'
import { useDepartmentsStore } from '@/stores/departments'

const router = useRouter()
const route = useRoute()

// 引入store
const departmentsStore = useDepartmentsStore()

// 搜索表单
const searchForm = reactive({
  keyword: ''
})

// 表格数据
const tableData = computed(() => {
  return (departmentsStore.departmentsWithCount || []).map(dept => ({
    id: dept.id,
    name: dept.name,
    description: dept.description || '-',
    employeeCount: dept.employee_count,
    createdAt: formatDate(dept.created_at)
  }))
})

// 分页
const currentPage = ref(1)
const pageSize = ref(10)
const total = computed(() => departmentsStore.totalCount)

// 加载状态
const loading = computed(() => departmentsStore.isLoading)

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

// 获取部门列表数据
const fetchData = async () => {
  try {
    await departmentsStore.getDepartmentsWithEmployeeCount()
  } catch (error: any) {
    ElMessage.error(`获取部门列表失败: ${error.message || '未知错误'}`)
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

// 添加部门
const handleAdd = () => {
  router.push('/department/add')
}

// 查看部门
const handleView = (row: any) => {
  router.push(`/department/view/${row.id}`)
}

// 编辑部门
const handleEdit = (row: any) => {
  router.push(`/department/edit/${row.id}`)
}

// 删除部门
const handleDelete = (row: any) => {
  ElMessageBox.confirm(
    `确定要删除部门 ${row.name} 吗？`,
    '删除确认',
    {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning',
    }
  ).then(async () => {
    try {
      await departmentsStore.deleteDepartment(row.id)
      ElMessage.success('删除成功')
      fetchData() // 重新加载数据
    } catch (error: any) {
      ElMessage.error(`删除失败: ${error.message || '未知错误'}`)
    }
  }).catch(() => {
    // 取消操作
  })
}

// 监听路由变化，当从其他页面返回时自动刷新数据
watch(
  () => route.path,
  (newPath) => {
    if (newPath === '/department/list') {
      fetchData()
    }
  }
)

// 初始化
onMounted(() => {
  fetchData()
})

// 当组件被激活时（如从 keep-alive 中恢复）自动刷新数据
onActivated(() => {
  fetchData()
})
</script>

<style scoped lang="scss">
.department-list {
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