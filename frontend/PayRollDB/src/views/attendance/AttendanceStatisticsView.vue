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
import { useAttendanceStore } from '@/stores/attendance'
import { useDepartmentsStore } from '@/stores/departments'
import { useEmployeesStore } from '@/stores/employees'
import { storeToRefs } from 'pinia'

// 初始化store
const attendanceStore = useAttendanceStore()
const departmentsStore = useDepartmentsStore()
const employeesStore = useEmployeesStore()

// 从store获取数据
const { isLoading, error } = storeToRefs(attendanceStore)

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
const departmentOptions = ref([])

// 加载状态
const loading = ref(false)

// 加载部门和员工数据
const loadOptions = async () => {
  try {
    // 加载部门数据
    await departmentsStore.getDepartments()
    departmentOptions.value = departmentsStore.departments.map(dept => ({
      value: dept.id,
      label: dept.name
    }))
  } catch (err) {
    ElMessage.error('加载选项数据失败')
  }
}

// 筛选表单
const filterForm = reactive({
  type: 'month',
  year: currentYear,
  month: new Date().getMonth() + 1,
  quarter: Math.floor((new Date().getMonth() / 3) + 1).toString(),
  departmentId: ''
})

// 表格数据
const tableData = ref([])

// 图表实例
let statusChart: echarts.ECharts | null = null
let departmentChart: echarts.ECharts | null = null
let trendChart: echarts.ECharts | null = null

// 统计卡片数据
const statisticsCards = ref([
  { title: '考勤人数', value: '0', icon: 'User', color: '#409EFF' },
  { title: '平均出勤率', value: '0%', icon: 'Calendar', color: '#67C23A' },
  { title: '迟到/早退', value: '0', icon: 'Warning', color: '#E6A23C' },
  { title: '缺勤人次', value: '0', icon: 'CircleClose', color: '#F56C6C' }
])

// 出勤率颜色
const getAttendanceRateColor = (rate) => {
  if (rate >= 95) return '#67C23A'
  if (rate >= 85) return '#E6A23C'
  return '#F56C6C'
}

// 更新状态分布图表
const updateStatusChart = () => {
  if (!statusChart) return;
  
  // 统计各状态数量
  const statusCounts = {
    '正常': 0,
    '迟到': 0,
    '早退': 0,
    '缺勤': 0,
    '请假': 0
  };
  
  tableData.value.forEach(item => {
    statusCounts['正常'] += item.attendanceDays || 0;
    statusCounts['迟到'] += item.lateTimes || 0;
    statusCounts['早退'] += item.earlyTimes || 0;
    statusCounts['缺勤'] += item.absentTimes || 0;
    statusCounts['请假'] += item.leaveTimes || 0;
  });
  
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
          { value: statusCounts['正常'], name: '正常出勤' },
          { value: statusCounts['迟到'], name: '迟到' },
          { value: statusCounts['早退'], name: '早退' },
          { value: statusCounts['缺勤'], name: '缺勤' },
          { value: statusCounts['请假'], name: '请假' }
          ]
        }
      ],
      color: ['#67C23A', '#E6A23C', '#F56C6C', '#909399', '#409EFF']
  };
    
  statusChart.setOption(statusOption);
};
  
// 更新部门考勤对比图表
const updateDepartmentChart = () => {
  if (!departmentChart) return;
  
  // 按部门分组统计
  const departmentStats = {};
  
  tableData.value.forEach(item => {
    if (!departmentStats[item.departmentName]) {
      departmentStats[item.departmentName] = {
        total: 0,
        normal: 0,
        late: 0,
        early: 0,
        absent: 0,
        leave: 0
      };
    }
    
    const stats = departmentStats[item.departmentName];
    const total = (item.attendanceDays || 0) + (item.lateTimes || 0) + 
                  (item.earlyTimes || 0) + (item.absentTimes || 0) + 
                  (item.leaveTimes || 0);
    
    stats.total += total;
    stats.normal += item.attendanceDays || 0;
    stats.late += item.lateTimes || 0;
    stats.early += item.earlyTimes || 0;
    stats.absent += item.absentTimes || 0;
    stats.leave += item.leaveTimes || 0;
  });
  
  // 计算各部门的百分比
  const departments = Object.keys(departmentStats);
  const normalRates = [];
  const lateRates = [];
  const earlyRates = [];
  const absentRates = [];
  const leaveRates = [];
  
  departments.forEach(dept => {
    const stats = departmentStats[dept];
    if (stats.total > 0) {
      normalRates.push(Math.round((stats.normal / stats.total) * 100));
      lateRates.push(Math.round((stats.late / stats.total) * 100));
      earlyRates.push(Math.round((stats.early / stats.total) * 100));
      absentRates.push(Math.round((stats.absent / stats.total) * 100));
      leaveRates.push(Math.round((stats.leave / stats.total) * 100));
    } else {
      normalRates.push(0);
      lateRates.push(0);
      earlyRates.push(0);
      absentRates.push(0);
      leaveRates.push(0);
    }
  });
  
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
      data: departments
      },
      series: [
        {
          name: '正常出勤率',
          type: 'bar',
          stack: 'total',
        data: normalRates,
          color: '#67C23A'
        },
        {
          name: '迟到率',
          type: 'bar',
          stack: 'total',
        data: lateRates,
          color: '#E6A23C'
        },
        {
          name: '早退率',
          type: 'bar',
          stack: 'total',
        data: earlyRates,
          color: '#F56C6C'
        },
        {
          name: '缺勤率',
          type: 'bar',
          stack: 'total',
        data: absentRates,
          color: '#909399'
        },
        {
          name: '请假率',
          type: 'bar',
          stack: 'total',
        data: leaveRates,
          color: '#409EFF'
        }
      ]
  };
    
  departmentChart.setOption(departmentOption);
};
  
// 更新趋势图表
const updateTrendChart = () => {
  if (!trendChart) return;
  
  // 这里需要按日期统计，但当前数据可能不包含日期维度
  // 可以考虑添加API获取按日期的统计数据
  // 暂时使用模拟数据
  const days = Array.from({ length: 30 }, (_, i) => i + 1);
  const attendanceRates = days.map(() => Math.floor(Math.random() * 15) + 85);
    
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
  };
    
  trendChart.setOption(trendOption);
};

// 处理筛选
const handleFilter = () => {
  fetchData();
};

// 处理重置
const handleReset = () => {
  filterForm.type = 'month';
  filterForm.year = currentYear;
  filterForm.month = new Date().getMonth() + 1;
  filterForm.quarter = Math.floor((new Date().getMonth() / 3) + 1).toString();
  filterForm.departmentId = '';
  
  fetchData();
};

// 导出报表
const handleExport = () => {
  ElMessage.success('考勤报表导出成功');
};

// 获取考勤统计数据
const fetchData = async () => {
  loading.value = true
  
  try {
    // 构建查询参数
    const params: any = {
      year: filterForm.year
    }
    
    if (filterForm.type === 'month') {
      params.month = filterForm.month
    } else if (filterForm.type === 'quarter') {
      // 计算季度对应的月份范围
      const quarterStartMonth = (parseInt(filterForm.quarter) - 1) * 3 + 1
      params.start_date = `${filterForm.year}-${quarterStartMonth.toString().padStart(2, '0')}-01`
      params.end_date = `${filterForm.year}-${(quarterStartMonth + 2).toString().padStart(2, '0')}-31`
    }
    
    if (filterForm.departmentId) {
      params.department_id = filterForm.departmentId
    }
    
    // 获取员工列表
    const employees = await employeesStore.getEmployees({
      department_id: filterForm.departmentId || undefined
    })
    
    // 准备表格数据
    const attendanceData = []
    let totalAttendanceDays = 0
    let totalLateTimes = 0
    let totalEarlyTimes = 0
    let totalAbsentTimes = 0
    let totalLeaveTimes = 0
    
    // 为每个员工获取考勤统计
    for (const employee of employees) {
      try {
        // 获取员工考勤统计
        const stats = await attendanceStore.getEmployeeAttendances(employee.id, params)
        
        // 分析考勤数据
        let normalDays = 0
        let lateTimes = 0
        let earlyTimes = 0
        let absentTimes = 0
        let leaveTimes = 0
        let overtimeHours = 0
        
        for (const record of stats) {
          if (record.status) {
            if (record.status.name === '正常') {
              normalDays++
            } else if (record.status.name === '迟到') {
              lateTimes++
            } else if (record.status.name === '早退') {
              earlyTimes++
            } else if (record.status.name === '缺勤' || record.status.name === '旷工') {
              absentTimes++
            } else if (record.status.name.includes('假')) {
              leaveTimes++
            }
            
            if (record.overtime_hours) {
              overtimeHours += parseFloat(record.overtime_hours.toString())
            }
          }
        }
        
        // 计算出勤率
        const workDays = normalDays + lateTimes + earlyTimes + absentTimes + leaveTimes
        const attendanceRate = workDays > 0 ? Math.round((normalDays / workDays) * 100) : 100
        
        // 添加到表格数据
        attendanceData.push({
          departmentId: employee.department_id,
          departmentName: employee.department?.name || '-',
          employeeId: employee.employee_id,
          employeeName: employee.name,
          attendanceDays: normalDays,
          lateTimes,
          earlyTimes,
          absentTimes,
          leaveTimes,
          overtimeHours,
          attendanceRate
        })
        
        // 累加总数
        totalAttendanceDays += normalDays
        totalLateTimes += lateTimes
        totalEarlyTimes += earlyTimes
        totalAbsentTimes += absentTimes
        totalLeaveTimes += leaveTimes
      } catch (err) {
        console.error(`获取员工 ${employee.id} 的考勤数据失败`, err)
      }
    }
    
    // 更新表格数据
    tableData.value = attendanceData
    
    // 更新统计卡片
    statisticsCards.value[0].value = employees.length.toString()
    
    const totalEmployees = attendanceData.length
    if (totalEmployees > 0) {
      const avgAttendanceRate = Math.round(
        attendanceData.reduce((sum, item) => sum + item.attendanceRate, 0) / totalEmployees
      )
      statisticsCards.value[1].value = `${avgAttendanceRate}%`
      statisticsCards.value[2].value = (totalLateTimes + totalEarlyTimes).toString()
      statisticsCards.value[3].value = totalAbsentTimes.toString()
    }
    
    // 更新图表
    updateCharts()
    
  } catch (err) {
    ElMessage.error('获取考勤统计数据失败')
    console.error('获取考勤统计数据失败', err)
  } finally {
    loading.value = false
  }
}

// 更新图表
const updateCharts = () => {
  // 延迟一下，确保DOM已经更新
  setTimeout(() => {
    updateStatusChart()
    updateDepartmentChart()
    updateTrendChart()
  }, 100)
}

// 初始化图表
const initCharts = () => {
  // 状态分布图表
  if (document.getElementById('statusChart')) {
    statusChart = echarts.init(document.getElementById('statusChart'));
  }
  
  // 部门考勤对比图表
  if (document.getElementById('departmentChart')) {
    departmentChart = echarts.init(document.getElementById('departmentChart'));
  }
  
  // 趋势图表
  if (document.getElementById('trendChart')) {
    trendChart = echarts.init(document.getElementById('trendChart'));
  }
  
  // 窗口大小变化时，重新调整图表大小
  window.addEventListener('resize', () => {
    statusChart?.resize();
    departmentChart?.resize();
    trendChart?.resize();
  });
};

// 页面加载时初始化
onMounted(() => {
  loadOptions();
  initCharts();
  fetchData();
});

// 监听筛选条件变化
watch(() => filterForm.type, (newVal) => {
  if (newVal === 'month') {
    filterForm.month = new Date().getMonth() + 1
  } else if (newVal === 'quarter') {
    filterForm.quarter = Math.floor((new Date().getMonth() / 3) + 1).toString()
  }
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