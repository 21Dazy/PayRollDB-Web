<template>
  <div class="user-attendance-container">
    <div class="attendance-header">
      <h2>我的考勤</h2>
      <p>查看您的考勤记录和统计信息</p>
    </div>

    <el-tabs v-model="activeTab" type="border-card">
      <!-- 考勤记录标签页 -->
      <el-tab-pane label="考勤记录" name="records">
        <div class="records-section">
          <!-- 筛选条件 -->
          <div class="filter-section">
            <el-form :model="filterForm" inline>
              <el-form-item label="年份">
                <el-select 
                  v-model="filterForm.year" 
                  placeholder="选择年份" 
                  clearable
                  @change="loadAttendanceRecords"
                >
                  <el-option 
                    v-for="year in getAvailableYears()" 
                    :key="year" 
                    :label="year + '年'" 
                    :value="year" 
                  />
                </el-select>
              </el-form-item>
              
              <el-form-item label="月份">
                <el-select 
                  v-model="filterForm.month" 
                  placeholder="选择月份" 
                  clearable
                  @change="loadAttendanceRecords"
                >
                  <el-option 
                    v-for="month in 12" 
                    :key="month" 
                    :label="month + '月'" 
                    :value="month" 
                  />
                </el-select>
              </el-form-item>
              
              <el-form-item label="状态">
                <el-select 
                  v-model="filterForm.status" 
                  placeholder="选择状态" 
                  clearable
                  @change="loadAttendanceRecords"
                >
                  <el-option label="正常" value="正常" />
                  <el-option label="迟到" value="迟到" />
                  <el-option label="早退" value="早退" />
                  <el-option label="迟到早退" value="迟到早退" />
                  <el-option label="缺勤" value="缺勤" />
                  <el-option label="请假" value="请假" />
                </el-select>
              </el-form-item>
              
              <el-form-item>
                <el-button type="primary" @click="loadAttendanceRecords">查询</el-button>
                <el-button @click="resetFilter">重置</el-button>
              </el-form-item>
            </el-form>
          </div>

          <!-- 考勤记录表格 -->
          <el-table :data="attendanceRecords" v-loading="loading" style="width: 100%">
            <el-table-column prop="date" label="日期" width="120">
              <template #default="scope">
                {{ formatDate(scope.row.date) }}
              </template>
            </el-table-column>
            <el-table-column prop="weekday" label="星期" width="80" />
            <!-- 由于后端不提供打卡时间和工作时长数据，暂时隐藏这些列 -->
            <!-- <el-table-column prop="clock_in" label="上班时间" width="100">
              <template #default="scope">
                {{ scope.row.clock_in || '-' }}
              </template>
            </el-table-column>
            <el-table-column prop="clock_out" label="下班时间" width="100">
              <template #default="scope">
                {{ scope.row.clock_out || '-' }}
              </template>
            </el-table-column>
            <el-table-column prop="work_hours" label="工作时长" width="100">
              <template #default="scope">
                {{ scope.row.work_hours ? scope.row.work_hours + 'h' : '-' }}
              </template>
            </el-table-column> -->
            <el-table-column prop="overtime_hours" label="加班时长" width="100">
              <template #default="scope">
                {{ scope.row.overtime_hours ? scope.row.overtime_hours + 'h' : '-' }}
              </template>
            </el-table-column>
            <el-table-column prop="status" label="状态" width="100">
              <template #default="scope">
                <el-tag :type="getAttendanceStatusType(scope.row.status)">
                  {{ scope.row.status }}
                </el-tag>
              </template>
            </el-table-column>
            <!-- 由于后端不提供迟到早退分钟数据，暂时隐藏这些列 -->
            <!-- <el-table-column prop="late_minutes" label="迟到分钟" width="100">
              <template #default="scope">
                {{ scope.row.late_minutes || '-' }}
              </template>
            </el-table-column>
            <el-table-column prop="early_leave_minutes" label="早退分钟" width="100">
              <template #default="scope">
                {{ scope.row.early_leave_minutes || '-' }}
              </template>
            </el-table-column> -->
            <el-table-column prop="remarks" label="备注" min-width="150">
              <template #default="scope">
                {{ scope.row.remarks || '-' }}
              </template>
            </el-table-column>
          </el-table>

          <!-- 分页 -->
          <div class="pagination">
            <el-pagination
              v-model:current-page="pagination.page"
              :page-size="pagination.size"
              :total="pagination.total"
              layout="total, prev, pager, next, jumper"
              @current-change="loadAttendanceRecords"
            />
          </div>
        </div>
      </el-tab-pane>

      <!-- 考勤统计标签页 -->
      <el-tab-pane label="考勤统计" name="statistics">
        <div class="statistics-section">
          <!-- 年月选择 -->
          <div class="period-selector">
            <el-select 
              v-model="statisticsYear" 
              placeholder="选择年份"
              @change="loadAttendanceStatistics"
            >
              <el-option 
                v-for="year in getAvailableYears()" 
                :key="year" 
                :label="year + '年'" 
                :value="year" 
              />
            </el-select>
            
            <el-select 
              v-model="statisticsMonth" 
              placeholder="选择月份（可选）"
              clearable
              @change="loadAttendanceStatistics"
              style="margin-left: 10px;"
            >
              <el-option 
                v-for="month in 12" 
                :key="month" 
                :label="month + '月'" 
                :value="month" 
              />
            </el-select>
          </div>

          <!-- 统计概览卡片 -->
          <el-row :gutter="20" class="summary-cards">
            <el-col :xs="24" :sm="12" :md="6">
              <el-card shadow="hover">
                <div class="summary-item">
                  <div class="summary-value">{{ statistics.summary?.total_days || 0 }}</div>
                  <div class="summary-label">总天数</div>
                </div>
              </el-card>
            </el-col>
            
            <el-col :xs="24" :sm="12" :md="6">
              <el-card shadow="hover">
                <div class="summary-item">
                  <div class="summary-value">{{ statistics.summary?.work_days || 0 }}</div>
                  <div class="summary-label">出勤天数</div>
                </div>
              </el-card>
            </el-col>
            
            <el-col :xs="24" :sm="12" :md="6">
              <el-card shadow="hover">
                <div class="summary-item">
                  <div class="summary-value">{{ statistics.summary?.late_days || 0 }}</div>
                  <div class="summary-label">迟到天数</div>
                </div>
              </el-card>
            </el-col>
            
            <el-col :xs="24" :sm="12" :md="6">
              <el-card shadow="hover">
                <div class="summary-item">
                  <div class="summary-value">{{ (statistics.summary?.attendance_rate || 0).toFixed(1) }}%</div>
                  <div class="summary-label">出勤率</div>
                </div>
              </el-card>
            </el-col>
          </el-row>

          <!-- 详细统计信息 -->
          <el-row :gutter="20" class="detail-cards">
            <el-col :xs="24" :sm="12" :md="6">
              <el-card shadow="hover">
                <div class="summary-item">
                  <div class="summary-value">{{ statistics.summary?.normal_days || 0 }}</div>
                  <div class="summary-label">正常天数</div>
                </div>
              </el-card>
            </el-col>
            
            <el-col :xs="24" :sm="12" :md="6">
              <el-card shadow="hover">
                <div class="summary-item">
                  <div class="summary-value">{{ statistics.summary?.early_leave_days || 0 }}</div>
                  <div class="summary-label">早退天数</div>
                </div>
              </el-card>
            </el-col>
            
            <el-col :xs="24" :sm="12" :md="6">
              <el-card shadow="hover">
                <div class="summary-item">
                  <div class="summary-value">{{ statistics.summary?.absent_days || 0 }}</div>
                  <div class="summary-label">缺勤天数</div>
                </div>
              </el-card>
            </el-col>
            
            <el-col :xs="24" :sm="12" :md="6">
              <el-card shadow="hover">
                <div class="summary-item">
                  <div class="summary-value">{{ (statistics.summary?.punctuality_rate || 0).toFixed(1) }}%</div>
                  <div class="summary-label">准时率</div>
                </div>
              </el-card>
            </el-col>
          </el-row>

          <!-- 时间统计 -->
          <el-row :gutter="20" class="time-cards">
            <el-col :xs="24" :sm="12" :md="6">
              <el-card shadow="hover">
                <div class="summary-item">
                  <div class="summary-value">{{ (statistics.summary?.total_work_hours || 0).toFixed(1) }}h</div>
                  <div class="summary-label">总工作时长</div>
                </div>
              </el-card>
            </el-col>
            
            <el-col :xs="24" :sm="12" :md="6">
              <el-card shadow="hover">
                <div class="summary-item">
                  <div class="summary-value">{{ (statistics.summary?.total_overtime_hours || 0).toFixed(1) }}h</div>
                  <div class="summary-label">总加班时长</div>
                </div>
              </el-card>
            </el-col>
            
            <el-col :xs="24" :sm="12" :md="6">
              <el-card shadow="hover">
                <div class="summary-item">
                  <div class="summary-value">{{ statistics.summary?.total_late_minutes || 0 }}分钟</div>
                  <div class="summary-label">累计迟到</div>
                </div>
              </el-card>
            </el-col>
            
            <el-col :xs="24" :sm="12" :md="6">
              <el-card shadow="hover">
                <div class="summary-item">
                  <div class="summary-value">{{ statistics.summary?.total_early_leave_minutes || 0 }}分钟</div>
                  <div class="summary-label">累计早退</div>
                </div>
              </el-card>
            </el-col>
          </el-row>

          <!-- 月度统计表格（仅年度查询时显示） -->
          <el-card v-if="!statisticsMonth && statistics?.monthly_summary" shadow="hover" class="monthly-table">
            <template #header>
              <div class="card-header">
                <span>月度统计</span>
              </div>
            </template>
            
            <el-table :data="statistics.monthly_summary" border>
              <el-table-column prop="month" label="月份" width="80">
                <template #default="scope">
                  {{ scope.row.month }}月
                </template>
              </el-table-column>
              <el-table-column prop="total_days" label="总天数" width="100" />
              <el-table-column prop="work_days" label="出勤天数" width="100" />
              <el-table-column prop="normal_days" label="正常天数" width="100" />
              <el-table-column prop="late_days" label="迟到天数" width="100" />
              <el-table-column prop="absent_days" label="缺勤天数" width="100" />
              <el-table-column prop="attendance_rate" label="出勤率" width="100">
                <template #default="scope">
                  {{ scope.row.attendance_rate }}%
                </template>
              </el-table-column>
            </el-table>
          </el-card>

          <!-- 状态分布饼图 -->
          <el-card shadow="hover" class="chart-card">
            <template #header>
              <div class="card-header">
                <span>考勤状态分布</span>
              </div>
            </template>
            
            <div ref="statusChartRef" class="chart-container"></div>
          </el-card>
        </div>
      </el-tab-pane>

      <!-- 考勤日历标签页 -->
      <el-tab-pane label="考勤日历" name="calendar">
        <div class="calendar-section">
          <!-- 日历头部控制 -->
          <div class="calendar-header">
            <div class="calendar-controls">
              <el-button @click="previousMonth">
                <el-icon><ArrowLeft /></el-icon>
              </el-button>
              <span class="calendar-title">
                {{ calendarYear }}年{{ calendarMonth }}月
              </span>
              <el-button @click="nextMonth">
                <el-icon><ArrowRight /></el-icon>
              </el-button>
            </div>
            
            <div class="calendar-legend">
              <span class="legend-item">
                <span class="legend-color normal"></span>
                正常
              </span>
              <span class="legend-item">
                <span class="legend-color late"></span>
                迟到
              </span>
              <span class="legend-item">
                <span class="legend-color early"></span>
                早退
              </span>
              <span class="legend-item">
                <span class="legend-color absent"></span>
                缺勤
              </span>
            </div>
          </div>

          <!-- 日历网格 -->
          <div class="calendar-grid">
            <div class="calendar-weekdays">
              <div class="weekday" v-for="day in weekdays" :key="day">{{ day }}</div>
            </div>
            
            <div class="calendar-days">
              <div 
                v-for="day in calendarDays" 
                :key="day.date"
                :class="['calendar-day', day.isCurrentMonth ? '' : 'other-month', day.isToday ? 'today' : '']"
                @click="viewDayDetail(day)"
              >
                <div class="day-number">{{ day.day }}</div>
                <div v-if="day.attendance" :class="['attendance-status', getAttendanceClass(day.attendance.status)]">
                  <div class="status-text">{{ day.attendance.status }}</div>
                  <div class="overtime-info" v-if="day.attendance.overtime_hours > 0">
                    <span>加班{{ day.attendance.overtime_hours }}h</span>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </el-tab-pane>

      <!-- 最近考勤标签页 -->
      <el-tab-pane label="最近考勤" name="recent">
        <div class="recent-section">
          <div class="section-header">
            <h3>最近7天考勤</h3>
            <el-button type="primary" @click="loadRecentAttendance">刷新</el-button>
          </div>
          
          <el-timeline>
            <el-timeline-item 
              v-for="record in recentRecords" 
              :key="record.date"
              :timestamp="formatDate(record.date) + ' ' + record.weekday"
              placement="top"
            >
              <el-card>
                <div class="recent-item">
                  <div class="item-header">
                    <el-tag :type="getAttendanceStatusType(record.status)">
                      {{ record.status }}
                    </el-tag>
                    <span class="overtime-hours">
                      加班时长: {{ record.overtime_hours ? record.overtime_hours + 'h' : '-' }}
                    </span>
                  </div>
                  
                  <div class="item-content">
                    <!-- 由于后端不提供打卡时间，暂时隐藏时间信息 -->
                    <!-- <div class="time-info">
                      <span class="clock-time">
                        <el-icon><Timer /></el-icon>
                        上班: {{ record.clock_in || '-' }}
                      </span>
                      <span class="clock-time">
                        <el-icon><Timer /></el-icon>
                        下班: {{ record.clock_out || '-' }}
                      </span>
                    </div> -->
                    
                    <!-- 由于后端不提供具体的迟到早退标记，通过状态显示 -->
                    <div v-if="record.status === '迟到' || record.status === '早退' || record.status === '迟到早退'" class="exception-info">
                      <span v-if="record.status.includes('迟到')" class="exception-tag late-tag">
                        迟到
                      </span>
                      <span v-if="record.status.includes('早退')" class="exception-tag early-tag">
                        早退
                      </span>
                    </div>
                    
                    <div v-if="record.remarks" class="remark">
                      备注: {{ record.remarks }}
                    </div>
                  </div>
                </div>
              </el-card>
            </el-timeline-item>
          </el-timeline>
        </div>
      </el-tab-pane>
    </el-tabs>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted, computed, nextTick, watch } from 'vue'
import { ElMessage } from 'element-plus'
import { ArrowLeft, ArrowRight, Timer } from '@element-plus/icons-vue'
import request from '@/utils/request'
import * as echarts from 'echarts'

// 类型定义
interface AttendanceRecord {
  id: number
  date: string
  weekday: string
  status: string
  status_id: number
  overtime_hours: number
  remarks: string | null
  created_at: string
  updated_at: string | null
}

interface AttendanceStatistics {
  period: {
    year: number
    month: number | null
  }
  summary: {
    total_days: number
    work_days: number
    normal_days: number
    late_days: number
    early_leave_days: number
    absent_days: number
    overtime_days: number
    total_work_hours: number
    total_overtime_hours: number
    total_late_minutes: number
    total_early_leave_minutes: number
    attendance_rate: number
    punctuality_rate: number
  }
  monthly_summary: Array<{
    month: number
    total_days: number
    work_days: number
    normal_days: number
    late_days: number
    absent_days: number
    attendance_rate: number
  }>
  status_breakdown: Record<string, number>
}

interface CalendarData {
  year: number
  month: number
  calendar_data: Record<number, {
    date: string
    status: string
    status_id: number
    overtime_hours: number
    remarks: string | null
  }>
  total_records: number
}

// 当前激活的标签页
const activeTab = ref('records')

// 加载状态
const loading = ref(false)

// 筛选表单
const filterForm = reactive({
  year: null as number | null,
  month: null as number | null,
  status: null as string | null
})

// 分页信息
const pagination = reactive({
  page: 1,
  size: 10,
  total: 0
})

// 考勤记录数据
const attendanceRecords = ref<AttendanceRecord[]>([])

// 统计数据
const statistics = ref<AttendanceStatistics>({
  period: { year: new Date().getFullYear(), month: null },
  summary: {
    total_days: 0,
    work_days: 0,
    normal_days: 0,
    late_days: 0,
    early_leave_days: 0,
    absent_days: 0,
    overtime_days: 0,
    total_work_hours: 0,
    total_overtime_hours: 0,
    total_late_minutes: 0,
    total_early_leave_minutes: 0,
    attendance_rate: 0,
    punctuality_rate: 0
  },
  monthly_summary: [],
  status_breakdown: {}
})
const statisticsYear = ref(new Date().getFullYear())
const statisticsMonth = ref<number | null>(null)

// 日历相关
const calendarYear = ref(new Date().getFullYear())
const calendarMonth = ref(new Date().getMonth() + 1)
const calendarData = ref<Record<number, any>>({})

// 最近考勤
const recentRecords = ref<AttendanceRecord[]>([])

// 图表引用
const statusChartRef = ref()

// 星期数组
const weekdays = ['日', '一', '二', '三', '四', '五', '六']

// 工具函数
const formatDate = (dateStr: string) => {
  if (!dateStr) return '-'
  return new Date(dateStr).toLocaleDateString()
}

const getAttendanceStatusType = (status: string) => {
  const statusMap: Record<string, string> = {
    '正常': 'success',
    '迟到': 'warning',
    '早退': 'warning',
    '迟到早退': 'warning',
    '缺勤': 'danger',
    '请假': 'info'
  }
  return statusMap[status] || 'info'
}

const getAttendanceClass = (status: string) => {
  const classMap: Record<string, string> = {
    '正常': 'normal',
    '迟到': 'late',
    '早退': 'early',
    '迟到早退': 'late',
    '缺勤': 'absent',
    '请假': 'leave'
  }
  return classMap[status] || 'normal'
}

const getAvailableYears = () => {
  const currentYear = new Date().getFullYear()
  return Array.from({ length: 5 }, (_, i) => currentYear - i)
}

// 计算日历天数
const calendarDays = computed(() => {
  const year = calendarYear.value
  const month = calendarMonth.value
  const firstDay = new Date(year, month - 1, 1)
  const lastDay = new Date(year, month, 0)
  const firstDayWeek = firstDay.getDay()
  const daysInMonth = lastDay.getDate()
  
  const days = []
  const today = new Date()
  
  // 上个月的天数
  const prevMonth = month === 1 ? 12 : month - 1
  const prevYear = month === 1 ? year - 1 : year
  const prevMonthLastDay = new Date(prevYear, prevMonth, 0).getDate()
  
  for (let i = firstDayWeek - 1; i >= 0; i--) {
    const day = prevMonthLastDay - i
    days.push({
      day,
      date: `${prevYear}-${prevMonth.toString().padStart(2, '0')}-${day.toString().padStart(2, '0')}`,
      isCurrentMonth: false,
      isToday: false,
      attendance: null
    })
  }
  
  // 当前月的天数
  for (let day = 1; day <= daysInMonth; day++) {
    const date = `${year}-${month.toString().padStart(2, '0')}-${day.toString().padStart(2, '0')}`
    const isToday = today.getFullYear() === year && 
                   today.getMonth() + 1 === month && 
                   today.getDate() === day
    
    days.push({
      day,
      date,
      isCurrentMonth: true,
      isToday,
      attendance: calendarData.value[day] || null
    })
  }
  
  // 下个月的天数
  const totalCells = 42 // 6周 × 7天
  const nextMonth = month === 12 ? 1 : month + 1
  const nextYear = month === 12 ? year + 1 : year
  
  for (let day = 1; days.length < totalCells; day++) {
    const date = `${nextYear}-${nextMonth.toString().padStart(2, '0')}-${day.toString().padStart(2, '0')}`
    days.push({
      day,
      date,
      isCurrentMonth: false,
      isToday: false,
      attendance: null
    })
  }
  
  return days
})

// API 调用函数
const loadAttendanceRecords = async () => {
  loading.value = true
  
  try {
    const params = {
      year: filterForm.year,
      month: filterForm.month,
      status: filterForm.status,
      skip: (pagination.page - 1) * pagination.size,
      limit: pagination.size
    }
    
    const response: any = await request.get('/api/v1/user/attendance/records', { params })
    attendanceRecords.value = response.records
    pagination.total = response.total
  } catch (error: any) {
    console.error("加载考勤记录失败:", error)
    ElMessage.error(error.response?.data?.detail || '加载考勤记录失败')
  } finally {
    loading.value = false
  }
}

const loadAttendanceStatistics = async () => {
  try {
    const params = {
      year: statisticsYear.value,
      month: statisticsMonth.value
    }
    
    const response: any = await request.get('/api/v1/user/attendance/statistics', { params })
    statistics.value = response
    
    // 更新图表
    nextTick(() => {
      renderStatusChart()
    })
  } catch (error: any) {
    console.error("加载考勤统计失败:", error)
    ElMessage.error(error.response?.data?.detail || '加载考勤统计失败')
  }
}

const loadCalendarData = async () => {
  try {
    const response: any = await request.get('/api/v1/user/attendance/calendar', {
      params: {
        year: calendarYear.value,
        month: calendarMonth.value
      }
    })
    calendarData.value = response.calendar_data
  } catch (error: any) {
    console.error("加载日历数据失败:", error)
    ElMessage.error(error.response?.data?.detail || '加载日历数据失败')
  }
}

const loadRecentAttendance = async () => {
  try {
    const response: any = await request.get('/api/v1/user/attendance/recent', {
      params: { days: 7 }
    })
    recentRecords.value = response.records
  } catch (error: any) {
    console.error("加载最近考勤失败:", error)
    ElMessage.error(error.response?.data?.detail || '加载最近考勤失败')
  }
}

// 重置筛选条件
const resetFilter = () => {
  filterForm.year = null
  filterForm.month = null
  filterForm.status = null
  pagination.page = 1
  loadAttendanceRecords()
}

// 日历导航
const previousMonth = () => {
  if (calendarMonth.value === 1) {
    calendarMonth.value = 12
    calendarYear.value -= 1
  } else {
    calendarMonth.value -= 1
  }
  loadCalendarData()
}

const nextMonth = () => {
  if (calendarMonth.value === 12) {
    calendarMonth.value = 1
    calendarYear.value += 1
  } else {
    calendarMonth.value += 1
  }
  loadCalendarData()
}

const viewDayDetail = (day: any) => {
  if (day.attendance) {
    ElMessage.info(`${day.date} 考勤详情：${day.attendance.status}`)
  }
}

// 图表渲染函数
const renderStatusChart = () => {
  if (!statusChartRef.value || !statistics.value?.status_breakdown) return
  
  const chart = echarts.init(statusChartRef.value)
  
  const data = Object.entries(statistics.value.status_breakdown).map(([key, value]) => ({
    name: key,
    value: value
  }))
  
  const option = {
    title: {
      text: '考勤状态分布',
      left: 'center'
    },
    tooltip: {
      trigger: 'item',
      formatter: '{a} <br/>{b}: {c} ({d}%)'
    },
    legend: {
      orient: 'vertical',
      left: 'left',
      top: 50
    },
    series: [
      {
        name: '考勤状态',
        type: 'pie',
        radius: '60%',
        center: ['60%', '60%'],
        data: data,
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
  
  chart.setOption(option)
}

// 监听统计年月变化
watch([() => statisticsYear.value, () => statisticsMonth.value], () => {
  loadAttendanceStatistics()
})

// 组件挂载时加载数据
onMounted(() => {
  loadAttendanceRecords()
  loadAttendanceStatistics()
  loadCalendarData()
  loadRecentAttendance()
})
</script>

<style scoped lang="scss">
.user-attendance-container {
  padding: 20px;
}

.attendance-header {
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

.filter-section {
  margin-bottom: 20px;
  padding: 20px;
  background: #f5f7fa;
  border-radius: 4px;
}

.pagination {
  margin-top: 20px;
  text-align: center;
}

// 统计页面样式
.statistics-section {
  .period-selector {
    margin-bottom: 20px;
    text-align: center;
  }
  
  .summary-cards,
  .detail-cards,
  .time-cards {
    margin-bottom: 30px;
    
    .summary-item {
      text-align: center;
      padding: 20px;
      
      .summary-value {
        font-size: 28px;
        font-weight: bold;
        color: #409EFF;
        margin-bottom: 10px;
      }
      
      .summary-label {
        color: #666;
        font-size: 14px;
      }
    }
  }
  
  .monthly-table {
    margin-bottom: 30px;
  }
  
  .chart-card {
    .chart-container {
      height: 300px;
      width: 100%;
    }
  }
}

// 日历样式
.calendar-section {
  .calendar-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 20px;
    
    .calendar-controls {
      display: flex;
      align-items: center;
      gap: 15px;
      
      .calendar-title {
        font-size: 18px;
        font-weight: bold;
        color: #333;
        min-width: 120px;
        text-align: center;
      }
    }
    
    .calendar-legend {
      display: flex;
      gap: 15px;
      
      .legend-item {
        display: flex;
        align-items: center;
        gap: 5px;
        font-size: 14px;
        
        .legend-color {
          width: 12px;
          height: 12px;
          border-radius: 2px;
          
          &.normal { background: #67C23A; }
          &.late { background: #E6A23C; }
          &.early { background: #F56C6C; }
          &.absent { background: #909399; }
        }
      }
    }
  }
  
  .calendar-grid {
    border: 1px solid #dcdfe6;
    border-radius: 4px;
    overflow: hidden;
    
    .calendar-weekdays {
      display: grid;
      grid-template-columns: repeat(7, 1fr);
      background: #f5f7fa;
      
      .weekday {
        padding: 10px;
        text-align: center;
        font-weight: bold;
        color: #333;
        border-right: 1px solid #dcdfe6;
        
        &:last-child {
          border-right: none;
        }
      }
    }
    
    .calendar-days {
      display: grid;
      grid-template-columns: repeat(7, 1fr);
      
      .calendar-day {
        min-height: 80px;
        padding: 8px;
        border-right: 1px solid #dcdfe6;
        border-bottom: 1px solid #dcdfe6;
        cursor: pointer;
        transition: background-color 0.3s;
        
        &:hover {
          background: #f5f7fa;
        }
        
        &:nth-child(7n) {
          border-right: none;
        }
        
        &.other-month {
          color: #c0c4cc;
          background: #fafafa;
        }
        
        &.today {
          background: #ecf5ff;
          
          .day-number {
            color: #409EFF;
            font-weight: bold;
          }
        }
        
        .day-number {
          font-size: 14px;
          margin-bottom: 4px;
        }
        
        .attendance-status {
          font-size: 12px;
          padding: 2px 4px;
          border-radius: 2px;
          color: white;
          
          &.normal { background: #67C23A; }
          &.late { background: #E6A23C; }
          &.early { background: #F56C6C; }
          &.absent { background: #909399; }
          &.leave { background: #409EFF; }
          
          .status-text {
            margin-bottom: 2px;
          }
          
          .overtime-info {
            font-size: 10px;
            opacity: 0.9;
          }
        }
      }
    }
  }
}

// 最近考勤样式
.recent-section {
  .section-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 20px;
    
    h3 {
      color: #333;
      margin: 0;
    }
  }
  
  .recent-item {
    .item-header {
      display: flex;
      justify-content: space-between;
      align-items: center;
      margin-bottom: 10px;
      
      .work-hours {
        color: #666;
        font-size: 14px;
      }
    }
    
    .item-content {
      .time-info {
        display: flex;
        gap: 20px;
        margin-bottom: 8px;
        
        .clock-time {
          display: flex;
          align-items: center;
          gap: 5px;
          color: #666;
          font-size: 14px;
        }
      }
      
      .exception-info {
        margin-bottom: 8px;
        
        .exception-tag {
          display: inline-block;
          padding: 2px 8px;
          border-radius: 4px;
          font-size: 12px;
          color: white;
          margin-right: 5px;
          
          &.late-tag { background: #E6A23C; }
          &.early-tag { background: #F56C6C; }
        }
      }
      
      .remark {
        color: #666;
        font-size: 14px;
        font-style: italic;
      }
    }
  }
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
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

// 响应式设计
@media (max-width: 768px) {
  .user-attendance-container {
    padding: 15px;
  }
  
  .filter-section {
    padding: 15px;
    
    :deep(.el-form--inline) {
      .el-form-item {
        display: block;
        margin-right: 0;
        margin-bottom: 15px;
      }
    }
  }
  
  .calendar-header {
    flex-direction: column;
    gap: 15px;
    
    .calendar-legend {
      flex-wrap: wrap;
      gap: 10px;
    }
  }
  
  .calendar-day {
    min-height: 60px !important;
    padding: 4px !important;
    
    .attendance-status {
      font-size: 10px !important;
      
      .time-info {
        display: none;
      }
    }
  }
  
  .summary-cards,
  .detail-cards,
  .time-cards {
    .el-col {
      margin-bottom: 15px;
    }
  }
}
</style> 