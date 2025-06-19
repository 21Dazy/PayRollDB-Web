<template>
  <div class="dashboard-container">
    <div class="dashboard-header">
      <div class="welcome-message">
        <h2>欢迎使用薪资管理系统</h2>
        <p>今天是 {{ currentDate }}，{{ greeting }}{{ userDisplayName ? '，' + userDisplayName : '' }}</p>
      </div>
    </div>
    
    <div class="stat-cards">
      <el-row :gutter="20">
        <el-col :xs="24" :sm="12" :md="6" v-for="(card, index) in statCards" :key="index">
          <el-card class="stat-card" shadow="hover" :body-style="{ padding: '20px' }">
            <div class="card-content">
              <el-icon class="card-icon" :size="36" :color="card.color">
                <component :is="card.icon"></component>
              </el-icon>
              <div class="card-info">
                <div class="card-value">{{ card.value }}</div>
                <div class="card-title">{{ card.title }}</div>
              </div>
            </div>
          </el-card>
        </el-col>
      </el-row>
    </div>
    
    <div class="dashboard-content">
      <el-row :gutter="20">
        <el-col :xs="24" :lg="16">
          <el-card class="chart-card" shadow="hover">
            <template #header>
              <div class="card-header">
                <span>{{ isAdmin ? '薪资发放统计' : '我的薪资趋势' }}</span>
              </div>
            </template>
            <div class="chart" id="salaryChart"></div>
          </el-card>
        </el-col>
        
        <el-col :xs="24" :lg="8">
          <el-card class="chart-card" shadow="hover">
            <template #header>
              <div class="card-header">
                <span>{{ isAdmin ? '部门人员分布' : '我的考勤统计' }}</span>
              </div>
            </template>
            <div class="chart" id="deptChart"></div>
          </el-card>
        </el-col>
      </el-row>
    </div>
    
    <div class="todo-section">
      <el-card class="todo-card" shadow="hover">
        <template #header>
          <div class="card-header">
            <span>{{ isAdmin ? '待办事项' : '最近活动' }}</span>
            <el-button v-if="isAdmin" type="primary" size="small" :icon="Plus">添加</el-button>
          </div>
        </template>
        <el-table :data="isAdmin ? todoList : activityList" style="width: 100%">
          <el-table-column v-if="isAdmin" prop="title" label="内容" />
          <el-table-column v-else prop="action_type" label="操作类型" width="120" />
          <el-table-column v-else prop="description" label="描述" />
          <el-table-column 
            :prop="isAdmin ? 'createTime' : 'created_at'" 
            :label="isAdmin ? '创建时间' : '时间'" 
            width="180" />
          <el-table-column v-if="isAdmin" prop="status" label="状态" width="100">
            <template #default="scope">
              <el-tag :type="scope.row.status === '已完成' ? 'success' : 'warning'">
                {{ scope.row.status }}
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column v-if="isAdmin" label="操作" width="150">
            <template #default="scope">
              <el-button
                link
                type="primary"
                size="small"
                @click="handleComplete(scope.row)"
                v-if="scope.row.status === '进行中'"
              >
                完成
              </el-button>
              <el-button
                link
                type="danger"
                size="small"
                @click="handleDelete(scope.row)"
              >
                删除
              </el-button>
            </template>
          </el-table-column>
        </el-table>
      </el-card>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { Plus, User, Money, Warning, Document, Clock, Trophy } from '@element-plus/icons-vue'
import { useSystemStore } from '@/stores/system'
import { useAuthStore } from '@/stores/auth'
import { getUserDashboardStats, getUserActivityLogs } from '@/api/user'
import { ElLoading, ElMessage } from 'element-plus'

// 系统数据
const systemStore = useSystemStore()
const authStore = useAuthStore()
const systemOverview = ref<any>(null)
const userStats = ref<any>(null)
const isDataLoaded = ref(false)
const activityList = ref<any[]>([])

// 判断是否为管理员
const isAdmin = computed(() => {
  return authStore.user?.role === 'admin' || authStore.user?.role === 'manager'
})

// 用户显示名称
const userDisplayName = computed(() => {
  return authStore.user?.username || ''
})

// 当前日期
const now = new Date()
const currentDate = computed(() => {
  return now.toLocaleDateString('zh-CN', { 
    year: 'numeric', 
    month: 'long', 
    day: 'numeric',
    weekday: 'long'
  })
})

// 问候语
const greeting = computed(() => {
  const hour = now.getHours()
  if (hour < 6) return '凌晨好'
  if (hour < 9) return '早上好'
  if (hour < 12) return '上午好'
  if (hour < 14) return '中午好'
  if (hour < 17) return '下午好'
  if (hour < 19) return '傍晚好'
  return '晚上好'
})

// 统计卡片数据
const statCards = computed(() => {
  if (isAdmin.value) {
    // 管理员显示系统统计
    if (!systemOverview.value) {
      return [
        { title: '员工总数', value: '加载中...', icon: 'User', color: '#409EFF' },
        { title: '本月薪资总额', value: '加载中...', icon: 'Money', color: '#67C23A' },
        { title: '本月考勤异常', value: '加载中...', icon: 'Warning', color: '#E6A23C' },
        { title: '待审批', value: '加载中...', icon: 'Document', color: '#F56C6C' }
      ]
    }
    
    return [
      { 
        title: '员工总数', 
        value: systemOverview.value.employee_count || '0', 
        icon: 'User', 
        color: '#409EFF' 
      },
      { 
        title: '本月薪资总额', 
        value: `¥${formatNumber(systemOverview.value.total_salary || 0)}`, 
        icon: 'Money', 
        color: '#67C23A' 
      },
      { 
        title: '本月考勤异常', 
        value: systemOverview.value.attendance_issues || '0', 
        icon: 'Warning', 
        color: '#E6A23C' 
      },
      { 
        title: '待审批', 
        value: systemOverview.value.pending_approvals || '0', 
        icon: 'Document', 
        color: '#F56C6C' 
      }
    ]
  } else {
    // 普通员工显示个人统计
    if (!userStats.value) {
      return [
        { title: '本月薪资', value: '加载中...', icon: 'Money', color: '#67C23A' },
        { title: '考勤率', value: '加载中...', icon: 'Clock', color: '#409EFF' },
        { title: '迟到次数', value: '加载中...', icon: 'Warning', color: '#E6A23C' },
        { title: '待处理申请', value: '加载中...', icon: 'Document', color: '#F56C6C' }
      ]
    }
    
    return [
      { 
        title: '本月薪资', 
        value: `¥${formatNumber(userStats.value.current_month_salary || 0)}`, 
        icon: 'Money', 
        color: '#67C23A' 
      },
      { 
        title: '考勤率', 
        value: `${userStats.value.attendance?.attendance_rate || 0}%`, 
        icon: 'Clock', 
        color: '#409EFF' 
      },
      { 
        title: '迟到次数', 
        value: userStats.value.attendance?.late_days || '0', 
        icon: 'Warning', 
        color: '#E6A23C' 
      },
      { 
        title: '待处理申请', 
        value: userStats.value.pending_requests || '0', 
        icon: 'Document', 
        color: '#F56C6C' 
      }
    ]
  }
})

// 格式化数字为千分位
function formatNumber(num: number): string {
  return num.toString().replace(/\B(?=(\d{3})+(?!\d))/g, ',')
}

// 待办事项（仅管理员）
const todoList = ref([
  { id: 1, title: '审核本月薪资', createTime: '2023-06-01 09:00:00', status: '进行中' },
  { id: 2, title: '处理员工请假申请', createTime: '2023-06-01 10:30:00', status: '进行中' },
  { id: 3, title: '更新社保基数', createTime: '2023-05-28 14:20:00', status: '已完成' },
  { id: 4, title: '部门绩效评估', createTime: '2023-05-27 16:45:00', status: '已完成' }
])

// 处理完成待办
const handleComplete = (row: any) => {
  row.status = '已完成'
}

// 处理删除待办
const handleDelete = (row: any) => {
  const index = todoList.value.findIndex(item => item.id === row.id)
  if (index !== -1) {
    todoList.value.splice(index, 1)
  }
}

// 获取系统概览数据（管理员）
const fetchSystemOverview = async () => {
  try {
    systemOverview.value = await systemStore.getSystemOverview()
  } catch (error) {
    console.error('获取系统概览数据失败:', error)
    ElMessage.error('获取系统数据失败')
  }
}

// 获取用户个人统计数据（普通员工）
const fetchUserStats = async () => {
  try {
    userStats.value = await getUserDashboardStats()
  } catch (error) {
    console.error('获取个人统计数据失败:', error)
    ElMessage.error('获取个人数据失败')
  }
}

// 获取用户活动记录（普通员工）
const fetchUserActivity = async () => {
  try {
    const response = await getUserActivityLogs({ limit: 10 })
    activityList.value = response.logs || []
  } catch (error) {
    console.error('获取活动记录失败:', error)
  }
}

// 获取数据的统一方法
const fetchData = async () => {
  const loading = ElLoading.service({
    lock: true,
    text: '加载数据中...',
    background: 'rgba(0, 0, 0, 0.7)'
  })
  
  try {
    if (isAdmin.value) {
      await fetchSystemOverview()
    } else {
      await Promise.all([
        fetchUserStats(),
        fetchUserActivity()
      ])
    }
    isDataLoaded.value = true
    
    // 当数据加载完成后初始化图表
    initCharts()
  } catch (error) {
    console.error('获取数据失败:', error)
  } finally {
    loading.close()
  }
}

// 初始化薪资统计图表
const initSalaryChart = (echarts: any) => {
  const chartDom = document.getElementById('salaryChart')
  if (!chartDom) return
  
  const myChart = echarts.init(chartDom)
  
  let salaryData
  if (isAdmin.value) {
    // 管理员显示全局薪资统计
    salaryData = systemOverview.value?.salary_data || {
      months: ['1月', '2月', '3月', '4月', '5月', '6月'],
      basic: [320000, 320000, 320000, 320000, 320000, 320000],
      performance: [120000, 132000, 101000, 134000, 150000, 130000],
      bonus: [80000, 60000, 90000, 70000, 80000, 100000],
      allowance: [50000, 50000, 50000, 50000, 50000, 50000]
    }
  } else {
    // 普通员工显示个人薪资趋势
    salaryData = userStats.value?.salary_trend || {
      months: ['1月', '2月', '3月', '4月', '5月', '6月'],
      basic: [8000, 8000, 8000, 8000, 8000, 8000],
      performance: [2000, 2200, 1800, 2400, 2100, 2300],
      bonus: [1000, 0, 1500, 800, 1000, 1200],
      allowance: [500, 500, 500, 500, 500, 500]
    }
  }
  
  const option = {
    tooltip: {
      trigger: 'axis',
      axisPointer: {
        type: 'shadow'
      }
    },
    legend: {
      data: ['基本工资', '绩效工资', '奖金', '补贴']
    },
    grid: {
      left: '3%',
      right: '4%',
      bottom: '3%',
      containLabel: true
    },
    xAxis: {
      type: 'category',
      data: salaryData.months
    },
    yAxis: {
      type: 'value'
    },
    series: [
      {
        name: '基本工资',
        type: 'bar',
        stack: 'total',
        emphasis: {
          focus: 'series'
        },
        data: salaryData.basic,
        color: '#409EFF'
      },
      {
        name: '绩效工资',
        type: 'bar',
        stack: 'total',
        emphasis: {
          focus: 'series'
        },
        data: salaryData.performance,
        color: '#67C23A'
      },
      {
        name: '奖金',
        type: 'bar',
        stack: 'total',
        emphasis: {
          focus: 'series'
        },
        data: salaryData.bonus,
        color: '#E6A23C'
      },
      {
        name: '补贴',
        type: 'bar',
        stack: 'total',
        emphasis: {
          focus: 'series'
        },
        data: salaryData.allowance,
        color: '#F56C6C'
      }
    ]
  }
  
  myChart.setOption(option)
  
  // 自适应窗口大小
  window.addEventListener('resize', () => {
    myChart.resize()
  })
}

// 初始化右侧图表
const initDeptChart = (echarts: any) => {
  const chartDom = document.getElementById('deptChart')
  if (!chartDom) return
  
  const myChart = echarts.init(chartDom)
  
  let option
  if (isAdmin.value) {
    // 管理员显示部门人员分布
    const deptData = systemOverview.value?.department_data || [
      { name: '研发部', value: 40 },
      { name: '市场部', value: 25 },
      { name: '销售部', value: 30 },
      { name: '行政部', value: 15 },
      { name: '财务部', value: 10 },
      { name: '人力资源部', value: 6 }
    ]
    
    option = {
      tooltip: {
        trigger: 'item',
        formatter: '{a} <br/>{b}: {c} ({d}%)'
      },
      legend: {
        orient: 'horizontal',
        bottom: 'bottom',
        data: deptData.map((item: any) => item.name)
      },
      series: [
        {
          name: '部门分布',
          type: 'pie',
          radius: '50%',
          center: ['50%', '45%'],
          data: deptData,
          emphasis: {
            itemStyle: {
              shadowBlur: 10,
              shadowOffsetX: 0,
              shadowColor: 'rgba(0, 0, 0, 0.5)'
            }
          }
        }
      ]
    }
  } else {
    // 普通员工显示考勤统计
    const attendanceData = userStats.value?.attendance || {
      present_days: 20,
      late_days: 2,
      absent_days: 0,
      leave_days: 1
    }
    
    option = {
      tooltip: {
        trigger: 'item',
        formatter: '{a} <br/>{b}: {c} 天 ({d}%)'
      },
      legend: {
        orient: 'horizontal',
        bottom: 'bottom',
        data: ['正常出勤', '迟到', '缺勤', '请假']
      },
      series: [
        {
          name: '考勤统计',
          type: 'pie',
          radius: '50%',
          center: ['50%', '45%'],
          data: [
            { name: '正常出勤', value: attendanceData.present_days, itemStyle: { color: '#67C23A' } },
            { name: '迟到', value: attendanceData.late_days, itemStyle: { color: '#E6A23C' } },
            { name: '缺勤', value: attendanceData.absent_days, itemStyle: { color: '#F56C6C' } },
            { name: '请假', value: attendanceData.leave_days, itemStyle: { color: '#909399' } }
          ],
          emphasis: {
            itemStyle: {
              shadowBlur: 10,
              shadowOffsetX: 0,
              shadowColor: 'rgba(0, 0, 0, 0.5)'
            }
          }
        }
      ]
    }
  }
  
  myChart.setOption(option)
  
  // 自适应窗口大小
  window.addEventListener('resize', () => {
    myChart.resize()
  })
}

// 初始化所有图表
const initCharts = () => {
  import('echarts').then((echarts) => {
    initSalaryChart(echarts)
    initDeptChart(echarts)
  })
}

// 组件挂载时获取数据
onMounted(() => {
  fetchData()
})
</script>

<style scoped lang="scss">
.dashboard-container {
  padding: 20px;
  
  .dashboard-header {
    margin-bottom: 24px;
    
    .welcome-message {
      h2 {
        font-size: 24px;
        color: #303133;
        margin: 0 0 8px 0;
      }
      
      p {
        font-size: 14px;
        color: #909399;
        margin: 0;
      }
    }
  }
  
  .stat-cards {
    margin-bottom: 24px;
    
    .stat-card {
      height: 100%;
      transition: all 0.3s;
      margin-bottom: 15px;
      
      &:hover {
        transform: translateY(-5px);
      }
      
      .card-content {
        display: flex;
        align-items: center;
        
        .card-icon {
          margin-right: 16px;
        }
        
        .card-info {
          .card-value {
            font-size: 24px;
            font-weight: bold;
            color: #303133;
            line-height: 1.5;
          }
          
          .card-title {
            font-size: 14px;
            color: #909399;
          }
        }
      }
    }
  }
  
  .dashboard-content {
    margin-bottom: 24px;
    
    .chart-card {
      margin-bottom: 20px;
      
      .card-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
      }
      
      .chart {
        height: 350px;
      }
    }
  }
  
  .todo-section {
    .todo-card {
      .card-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
      }
    }
  }
}

@media screen and (max-width: 768px) {
  .dashboard-container {
    padding: 15px 10px;
    
    .dashboard-header {
      .welcome-message {
        h2 {
          font-size: 20px;
        }
      }
    }
    
    .chart {
      height: 300px !important;
    }
  }
}
</style> 