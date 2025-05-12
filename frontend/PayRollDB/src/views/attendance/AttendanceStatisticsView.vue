<template>
  <div class="attendance-statistics">
    <div class="page-header">
      <h2>考勤统计</h2>
      <div class="page-actions">
        <el-button :icon="Download" @click="handleExport">导出报表</el-button>
      </div>
    </div>
    
    <div class="filter-bar">
      <el-form :inline="true" :model="filterForm">
        <el-form-item label="统计周期">
          <el-select v-model="filterForm.type" placeholder="请选择统计周期" style="width: 120px">
            <el-option label="月度" value="month" />
            <el-option label="季度" value="quarter" />
            <el-option label="年度" value="year" />
          </el-select>
        </el-form-item>
        <el-form-item label="年份">
          <el-select v-model="filterForm.year" placeholder="请选择年份" style="width: 120px">
            <el-option
              v-for="item in yearOptions"
              :key="item.value"
              :label="item.label"
              :value="item.value"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="月份" v-if="filterForm.type === 'month'">
          <el-select v-model="filterForm.month" placeholder="请选择月份" style="width: 120px">
            <el-option
              v-for="item in monthOptions"
              :key="item.value"
              :label="item.label"
              :value="item.value"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="季度" v-if="filterForm.type === 'quarter'">
          <el-select v-model="filterForm.quarter" placeholder="请选择季度" style="width: 120px">
            <el-option label="第一季度" value="1" />
            <el-option label="第二季度" value="2" />
            <el-option label="第三季度" value="3" />
            <el-option label="第四季度" value="4" />
          </el-select>
        </el-form-item>
        <el-form-item label="部门">
          <el-select v-model="filterForm.departmentId" placeholder="请选择部门" clearable style="width: 120px">
            <el-option
              v-for="item in departmentOptions"
              :key="item.value"
              :label="item.label"
              :value="item.value"
            />
          </el-select>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" :icon="Search" @click="handleFilter">查询</el-button>
          <el-button :icon="Refresh" @click="handleReset">重置</el-button>
        </el-form-item>
      </el-form>
    </div>
    
    <div class="statistics-cards">
      <el-row :gutter="20">
        <el-col :xs="24" :sm="12" :md="6" v-for="(card, index) in statisticsCards" :key="index">
          <el-card class="statistics-card" shadow="hover" :body-style="{ padding: '20px' }">
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
    
    <div class="charts-container">
      <el-row :gutter="20">
        <el-col :xs="24" :lg="12">
          <el-card class="chart-card" shadow="hover">
            <template #header>
              <div class="card-header">
                <span>考勤状态分布</span>
              </div>
            </template>
            <div class="chart status-chart" id="statusChart"></div>
          </el-card>
        </el-col>
        
        <el-col :xs="24" :lg="12">
          <el-card class="chart-card" shadow="hover">
            <template #header>
              <div class="card-header">
                <span>各部门考勤对比</span>
              </div>
            </template>
            <div class="chart department-chart" id="departmentChart"></div>
          </el-card>
        </el-col>
      </el-row>
      
      <el-card class="chart-card" shadow="hover">
        <template #header>
          <div class="card-header">
            <span>出勤率趋势</span>
          </div>
        </template>
        <div class="chart trend-chart" id="trendChart"></div>
      </el-card>
    </div>
    
    <div class="statistics-table">
      <el-card shadow="hover">
        <template #header>
          <div class="card-header">
            <span>考勤详细统计</span>
          </div>
        </template>
        <el-table
          :data="tableData"
          style="width: 100%"
          border
          stripe
          v-loading="loading"
        >
          <el-table-column prop="departmentName" label="部门" width="120" />
          <el-table-column prop="employeeId" label="工号" width="100" />
          <el-table-column prop="employeeName" label="姓名" width="100" />
          <el-table-column prop="attendanceDays" label="出勤天数" width="100" />
          <el-table-column prop="lateTimes" label="迟到次数" width="100" />
          <el-table-column prop="earlyTimes" label="早退次数" width="100" />
          <el-table-column prop="absentTimes" label="缺勤次数" width="100" />
          <el-table-column prop="leaveTimes" label="请假次数" width="100" />
          <el-table-column prop="overtimeHours" label="加班时长" width="100">
            <template #default="{ row }">
              {{ row.overtimeHours }}小时
            </template>
          </el-table-column>
          <el-table-column prop="attendanceRate" label="出勤率" width="100">
            <template #default="{ row }">
              <el-progress 
                :percentage="row.attendanceRate" 
                :color="getAttendanceRateColor(row.attendanceRate)"
              />
            </template>
          </el-table-column>
        </el-table>
      </el-card>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted, watch } from 'vue'
import { ElMessage } from 'element-plus'
import { Search, Refresh, Download } from '@element-plus/icons-vue'
import * as echarts from 'echarts'

// 年份选项
const currentYear = new Date().getFullYear()
const yearOptions = ref([
  { value: currentYear, label: `${currentYear}年` },
  { value: currentYear - 1, label: `${currentYear - 1}年` },
  { value: currentYear - 2, label: `${currentYear - 2}年` }
])

// 月份选项
const monthOptions = ref(Array.from({ length: 12 }, (_, i) => ({
  value: i + 1,
  label: `${i + 1}月`
})))

// 部门选项
const departmentOptions = ref([
  { value: '1', label: '研发部' },
  { value: '2', label: '市场部' },
  { value: '3', label: '销售部' },
  { value: '4', label: '财务部' },
  { value: '5', label: '人事部' }
])

// 筛选表单
const filterForm = reactive({
  type: 'month',
  year: currentYear,
  month: new Date().getMonth() + 1,
  quarter: Math.floor((new Date().getMonth() / 3) + 1).toString(),
  departmentId: ''
})

// 统计卡片数据
const statisticsCards = ref([
  { title: '考勤人数', value: '126', icon: 'User', color: '#409EFF' },
  { title: '平均出勤率', value: '96.3%', icon: 'Calendar', color: '#67C23A' },
  { title: '迟到/早退', value: '18', icon: 'Warning', color: '#E6A23C' },
  { title: '加班总时长', value: '326小时', icon: 'Timer', color: '#F56C6C' }
])

// 表格数据
const tableData = ref([])

// 加载状态
const loading = ref(false)

// 图表实例
let statusChart = null
let departmentChart = null
let trendChart = null

// 出勤率颜色
const getAttendanceRateColor = (rate) => {
  if (rate >= 95) return '#67C23A'
  if (rate >= 85) return '#E6A23C'
  return '#F56C6C'
}

// 处理筛选
const handleFilter = () => {
  fetchData()
}

// 处理重置
const handleReset = () => {
  filterForm.type = 'month'
  filterForm.year = currentYear
  filterForm.month = new Date().getMonth() + 1
  filterForm.quarter = Math.floor((new Date().getMonth() / 3) + 1).toString()
  filterForm.departmentId = ''
  fetchData()
}

// 导出报表
const handleExport = () => {
  ElMessage.success('考勤统计报表导出成功')
}

// 获取统计数据
const fetchData = () => {
  loading.value = true
  
  // 模拟API调用
  setTimeout(() => {
    // 更新统计卡片
    updateStatisticsCards()
    
    // 更新表格数据
    updateTableData()
    
    // 更新图表
    updateCharts()
    
    loading.value = false
  }, 500)
}

// 更新统计卡片
const updateStatisticsCards = () => {
  const attendanceCount = Math.floor(Math.random() * 50) + 100
  const attendanceRate = (Math.random() * 10 + 90).toFixed(1)
  const lateEarlyCount = Math.floor(Math.random() * 20)
  const overtimeHours = Math.floor(Math.random() * 200) + 200
  
  statisticsCards.value = [
    { title: '考勤人数', value: attendanceCount.toString(), icon: 'User', color: '#409EFF' },
    { title: '平均出勤率', value: `${attendanceRate}%`, icon: 'Calendar', color: '#67C23A' },
    { title: '迟到/早退', value: lateEarlyCount.toString(), icon: 'Warning', color: '#E6A23C' },
    { title: '加班总时长', value: `${overtimeHours}小时`, icon: 'Timer', color: '#F56C6C' }
  ]
}

// 更新表格数据
const updateTableData = () => {
  const mockData = []
  for (let i = 0; i < 10; i++) {
    const deptIndex = i % 5
    const attendanceDays = Math.floor(Math.random() * 5) + 15
    const lateTimes = Math.floor(Math.random() * 3)
    const earlyTimes = Math.floor(Math.random() * 2)
    const absentTimes = Math.floor(Math.random() * 2)
    const leaveTimes = Math.floor(Math.random() * 3)
    const totalDays = 22
    const attendanceRate = Math.round((attendanceDays / totalDays) * 100)
    
    mockData.push({
      departmentName: ['研发部', '市场部', '销售部', '财务部', '人事部'][deptIndex],
      departmentId: (deptIndex + 1).toString(),
      employeeId: `EMP${1000 + i}`,
      employeeName: ['张三', '李四', '王五', '赵六', '钱七'][i % 5],
      attendanceDays,
      lateTimes,
      earlyTimes,
      absentTimes,
      leaveTimes,
      overtimeHours: Math.floor(Math.random() * 10) + 2,
      attendanceRate
    })
  }
  
  tableData.value = mockData
}

// 更新图表
const updateCharts = () => {
  // 状态分布图表
  if (statusChart) {
    const statusOption = {
      title: {
        text: '',
        left: 'center'
      },
      tooltip: {
        trigger: 'item',
        formatter: '{a} <br/>{b}: {c} ({d}%)'
      },
      legend: {
        orient: 'vertical',
        left: 'left',
        data: ['正常出勤', '迟到', '早退', '缺勤', '请假']
      },
      series: [
        {
          name: '考勤状态',
          type: 'pie',
          radius: ['50%', '70%'],
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
            { value: 335, name: '正常出勤' },
            { value: 21, name: '迟到' },
            { value: 14, name: '早退' },
            { value: 8, name: '缺勤' },
            { value: 18, name: '请假' }
          ]
        }
      ],
      color: ['#67C23A', '#E6A23C', '#F56C6C', '#909399', '#409EFF']
    }
    
    statusChart.setOption(statusOption)
  }
  
  // 部门考勤对比图表
  if (departmentChart) {
    const departmentOption = {
      tooltip: {
        trigger: 'axis',
        axisPointer: {
          type: 'shadow'
        }
      },
      legend: {
        data: ['正常出勤率', '迟到率', '早退率', '缺勤率', '请假率']
      },
      grid: {
        left: '3%',
        right: '4%',
        bottom: '3%',
        containLabel: true
      },
      xAxis: {
        type: 'value',
        boundaryGap: [0, 0.01]
      },
      yAxis: {
        type: 'category',
        data: ['研发部', '市场部', '销售部', '财务部', '人事部']
      },
      series: [
        {
          name: '正常出勤率',
          type: 'bar',
          stack: 'total',
          data: [92, 94, 89, 97, 95],
          color: '#67C23A'
        },
        {
          name: '迟到率',
          type: 'bar',
          stack: 'total',
          data: [3, 2, 4, 1, 2],
          color: '#E6A23C'
        },
        {
          name: '早退率',
          type: 'bar',
          stack: 'total',
          data: [2, 1, 3, 0, 1],
          color: '#F56C6C'
        },
        {
          name: '缺勤率',
          type: 'bar',
          stack: 'total',
          data: [1, 1, 2, 0, 0],
          color: '#909399'
        },
        {
          name: '请假率',
          type: 'bar',
          stack: 'total',
          data: [2, 2, 2, 2, 2],
          color: '#409EFF'
        }
      ]
    }
    
    departmentChart.setOption(departmentOption)
  }
  
  // 趋势图表
  if (trendChart) {
    const days = Array.from({ length: 30 }, (_, i) => i + 1)
    const attendanceRates = days.map(() => Math.floor(Math.random() * 15) + 85)
    
    const trendOption = {
      tooltip: {
        trigger: 'axis'
      },
      grid: {
        left: '3%',
        right: '4%',
        bottom: '3%',
        containLabel: true
      },
      xAxis: {
        type: 'category',
        boundaryGap: false,
        data: days
      },
      yAxis: {
        type: 'value',
        min: 80,
        max: 100
      },
      series: [
        {
          name: '出勤率',
          type: 'line',
          data: attendanceRates,
          smooth: true,
          areaStyle: {
            color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
              {
                offset: 0,
                color: 'rgba(58, 71, 212, 0.8)'
              },
              {
                offset: 1,
                color: 'rgba(58, 71, 212, 0.3)'
              }
            ])
          },
          lineStyle: {
            width: 2,
            color: '#3a47d4'
          },
          itemStyle: {
            color: '#3a47d4'
          }
        }
      ]
    }
    
    trendChart.setOption(trendOption)
  }
}

// 初始化图表
const initCharts = () => {
  // 初始化状态分布图表
  statusChart = echarts.init(document.getElementById('statusChart'))
  
  // 初始化部门对比图表
  departmentChart = echarts.init(document.getElementById('departmentChart'))
  
  // 初始化趋势图表
  trendChart = echarts.init(document.getElementById('trendChart'))
  
  // 窗口大小变化时，重新调整图表大小
  window.addEventListener('resize', () => {
    statusChart.resize()
    departmentChart.resize()
    trendChart.resize()
  })
}

// 监听筛选条件变化
watch(() => filterForm.type, (newVal) => {
  if (newVal === 'month') {
    filterForm.month = new Date().getMonth() + 1
  } else if (newVal === 'quarter') {
    filterForm.quarter = Math.floor((new Date().getMonth() / 3) + 1).toString()
  }
})

onMounted(() => {
  // 初始化图表
  initCharts()
  
  // 加载数据
  fetchData()
})
</script>

<style scoped lang="scss">
.attendance-statistics {
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
  
  .filter-bar {
    margin-bottom: 20px;
    background-color: #fff;
    padding: 20px;
    border-radius: 4px;
    box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.04);
  }
  
  .statistics-cards {
    margin-bottom: 20px;
    
    .statistics-card {
      height: 100%;
      transition: all 0.3s;
      
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
  
  .charts-container {
    margin-bottom: 20px;
    
    .chart-card {
      margin-bottom: 20px;
      
      .card-header {
        font-weight: bold;
      }
    }
    
    .chart {
      height: 350px;
    }
  }
  
  .statistics-table {
    .card-header {
      font-weight: bold;
    }
  }
}
</style> 