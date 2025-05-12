<template>
  <div class="dashboard-container">
    <div class="dashboard-header">
      <div class="welcome-message">
        <h2>欢迎使用薪资管理系统</h2>
        <p>今天是 {{ currentDate }}，{{ greeting }}</p>
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
                <span>薪资发放统计</span>
              </div>
            </template>
            <div class="chart" id="salaryChart"></div>
          </el-card>
        </el-col>
        
        <el-col :xs="24" :lg="8">
          <el-card class="chart-card" shadow="hover">
            <template #header>
              <div class="card-header">
                <span>部门人员分布</span>
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
            <span>待办事项</span>
            <el-button type="primary" size="small" :icon="Plus">添加</el-button>
          </div>
        </template>
        <el-table :data="todoList" style="width: 100%">
          <el-table-column prop="title" label="内容" />
          <el-table-column prop="createTime" label="创建时间" width="180" />
          <el-table-column prop="status" label="状态" width="100">
            <template #default="scope">
              <el-tag :type="scope.row.status === '已完成' ? 'success' : 'warning'">
                {{ scope.row.status }}
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column label="操作" width="150">
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
import { Plus, User, Money, Warning, Document } from '@element-plus/icons-vue'

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
const statCards = ref([
  { title: '员工总数', value: '126', icon: 'User', color: '#409EFF' },
  { title: '本月薪资总额', value: '¥862,500', icon: 'Money', color: '#67C23A' },
  { title: '本月考勤异常', value: '8', icon: 'Warning', color: '#E6A23C' },
  { title: '待审批', value: '5', icon: 'Document', color: '#F56C6C' }
])

// 待办事项
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

// 初始化薪资统计图表
const initSalaryChart = (echarts: any) => {
  const chartDom = document.getElementById('salaryChart')
  if (!chartDom) return
  
  const myChart = echarts.init(chartDom)
  
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
      data: ['1月', '2月', '3月', '4月', '5月', '6月']
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
        data: [320000, 320000, 320000, 320000, 320000, 320000],
        color: '#409EFF'
      },
      {
        name: '绩效工资',
        type: 'bar',
        stack: 'total',
        emphasis: {
          focus: 'series'
        },
        data: [120000, 132000, 101000, 134000, 150000, 130000],
        color: '#67C23A'
      },
      {
        name: '奖金',
        type: 'bar',
        stack: 'total',
        emphasis: {
          focus: 'series'
        },
        data: [80000, 60000, 90000, 70000, 80000, 100000],
        color: '#E6A23C'
      },
      {
        name: '补贴',
        type: 'bar',
        stack: 'total',
        emphasis: {
          focus: 'series'
        },
        data: [50000, 50000, 50000, 50000, 50000, 50000],
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

// 初始化部门人数分布图表
const initDeptChart = (echarts: any) => {
  const chartDom = document.getElementById('deptChart')
  if (!chartDom) return
  
  const myChart = echarts.init(chartDom)
  
  const option = {
    tooltip: {
      trigger: 'item',
      formatter: '{a} <br/>{b}: {c} ({d}%)'
    },
    legend: {
      orient: 'horizontal',
      bottom: 'bottom',
    },
    series: [
      {
        name: '部门分布',
        type: 'pie',
        radius: ['40%', '70%'],
        avoidLabelOverlap: false,
        itemStyle: {
          borderRadius: 10,
          borderColor: '#fff',
          borderWidth: 2
        },
        label: {
          show: false,
          position: 'center'
        },
        emphasis: {
          label: {
            show: true,
            fontSize: '18',
            fontWeight: 'bold'
          }
        },
        labelLine: {
          show: false
        },
        data: [
          { value: 35, name: '研发部' },
          { value: 25, name: '市场部' },
          { value: 30, name: '销售部' },
          { value: 20, name: '财务部' },
          { value: 16, name: '人事部' }
        ]
      }
    ]
  }
  
  myChart.setOption(option)
  
  // 自适应窗口大小
  window.addEventListener('resize', () => {
    myChart.resize()
  })
}

onMounted(() => {
  // 动态导入echarts
  import('echarts').then(module => {
    const echarts = module
    // 初始化图表
    setTimeout(() => {
      initSalaryChart(echarts)
      initDeptChart(echarts)
    }, 100)
  }).catch(err => {
    console.error('Failed to load echarts:', err)
  })
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