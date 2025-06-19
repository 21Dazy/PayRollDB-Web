<template>
  <div class="user-salary-container">
    <div class="salary-header">
      <h2>我的薪资</h2>
      <p>查看您的薪资记录和统计信息</p>
    </div>

    <el-tabs v-model="activeTab" type="border-card">
      <!-- 薪资记录标签页 -->
      <el-tab-pane label="薪资记录" name="records">
        <div class="records-section">
          <!-- 筛选条件 -->
          <div class="filter-section">
            <el-form :model="filterForm" inline>
              <el-form-item label="年份">
                <el-select 
                  v-model="filterForm.year" 
                  placeholder="选择年份" 
                  clearable
                  @change="loadSalaryRecords"
                >
                  <el-option 
                    v-for="year in availableYears" 
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
                  @change="loadSalaryRecords"
                >
                  <el-option 
                    v-for="month in 12" 
                    :key="month" 
                    :label="month + '月'" 
                    :value="month" 
                  />
                </el-select>
              </el-form-item>
              
              <el-form-item>
                <el-button type="primary" @click="loadSalaryRecords">查询</el-button>
                <el-button @click="resetFilter">重置</el-button>
              </el-form-item>
            </el-form>
          </div>

          <!-- 薪资记录表格 -->
          <el-table :data="salaryRecords" v-loading="loading" style="width: 100%">
            <el-table-column prop="period" label="薪资月份" width="120" />
            <el-table-column prop="base_salary" label="基本工资" width="120">
              <template #default="scope">
                ¥{{ formatMoney(scope.row.base_salary) }}
              </template>
            </el-table-column>
            <el-table-column prop="overtime_pay" label="加班费" width="100">
              <template #default="scope">
                ¥{{ formatMoney(scope.row.overtime_pay) }}
              </template>
            </el-table-column>
            <el-table-column prop="bonus" label="奖金" width="100">
              <template #default="scope">
                ¥{{ formatMoney(scope.row.bonus) }}
              </template>
            </el-table-column>
            <el-table-column prop="gross_salary" label="应发工资" width="120">
              <template #default="scope">
                ¥{{ formatMoney(scope.row.gross_salary) }}
              </template>
            </el-table-column>
            <el-table-column prop="total_deduction" label="扣款合计" width="120">
              <template #default="scope">
                ¥{{ formatMoney(scope.row.total_deduction) }}
              </template>
            </el-table-column>
            <el-table-column prop="net_salary" label="实发工资" width="120">
              <template #default="scope">
                <span class="net-salary">¥{{ formatMoney(scope.row.net_salary) }}</span>
              </template>
            </el-table-column>
            <el-table-column prop="status" label="状态" width="100">
              <template #default="scope">
                <el-tag :type="getSalaryStatusType(scope.row.status)">
                  {{ scope.row.status }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="payment_date" label="发放日期" width="120">
              <template #default="scope">
                {{ formatDate(scope.row.payment_date) }}
              </template>
            </el-table-column>
            <el-table-column label="操作" width="180">
              <template #default="scope">
                <el-button 
                  size="small" 
                  @click="viewSalaryDetail(scope.row)"
                >
                  查看详情
                </el-button>
                <el-button 
                  size="small" 
                  type="primary" 
                  @click="downloadPayslip(scope.row)"
                  :disabled="scope.row.status !== '已发放'"
                >
                  下载工资条
                </el-button>
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
              @current-change="loadSalaryRecords"
            />
          </div>
        </div>
      </el-tab-pane>

      <!-- 薪资统计标签页 -->
      <el-tab-pane label="薪资统计" name="statistics">
        <div class="statistics-section">
          <!-- 年份选择 -->
          <div class="year-selector">
            <el-select 
              v-model="statisticsYear" 
              placeholder="选择统计年份"
              @change="loadSalaryStatistics"
            >
              <el-option 
                v-for="year in availableYears" 
                :key="year" 
                :label="year + '年'" 
                :value="year" 
              />
            </el-select>
          </div>

          <!-- 年度汇总卡片 -->
          <el-row :gutter="20" class="summary-cards">
            <el-col :xs="24" :sm="12" :md="6">
              <el-card shadow="hover">
                <div class="summary-item">
                  <div class="summary-value">¥{{ formatMoney(statistics.annual_summary?.total_gross || 0) }}</div>
                  <div class="summary-label">年度应发总额</div>
                </div>
              </el-card>
            </el-col>
            
            <el-col :xs="24" :sm="12" :md="6">
              <el-card shadow="hover">
                <div class="summary-item">
                  <div class="summary-value">¥{{ formatMoney(statistics.annual_summary?.total_deduction || 0) }}</div>
                  <div class="summary-label">年度扣款总额</div>
                </div>
              </el-card>
            </el-col>
            
            <el-col :xs="24" :sm="12" :md="6">
              <el-card shadow="hover">
                <div class="summary-item">
                  <div class="summary-value">¥{{ formatMoney(statistics.annual_summary?.total_net || 0) }}</div>
                  <div class="summary-label">年度实发总额</div>
                </div>
              </el-card>
            </el-col>
            
            <el-col :xs="24" :sm="12" :md="6">
              <el-card shadow="hover">
                <div class="summary-item">
                  <div class="summary-value">¥{{ formatMoney(statistics.annual_summary?.average_monthly || 0) }}</div>
                  <div class="summary-label">月均实发</div>
                </div>
              </el-card>
            </el-col>
          </el-row>

          <!-- 月度趋势图 -->
          <el-card shadow="hover" class="chart-card">
            <template #header>
              <div class="card-header">
                <span>月度薪资趋势</span>
              </div>
            </template>
            
            <div ref="monthlyChartRef" class="chart-container"></div>
          </el-card>

          <!-- 收入构成饼图 -->
          <el-row :gutter="20" class="pie-charts">
            <el-col :xs="24" :md="12">
              <el-card shadow="hover">
                <template #header>
                  <div class="card-header">
                    <span>收入构成</span>
                  </div>
                </template>
                
                <div ref="incomeChartRef" class="chart-container"></div>
              </el-card>
            </el-col>
            
            <el-col :xs="24" :md="12">
              <el-card shadow="hover">
                <template #header>
                  <div class="card-header">
                    <span>扣款构成</span>
                  </div>
                </template>
                
                <div ref="deductionChartRef" class="chart-container"></div>
              </el-card>
            </el-col>
          </el-row>
        </div>
      </el-tab-pane>
    </el-tabs>

    <!-- 薪资详情对话框 -->
    <el-dialog
      v-model="showDetailDialog"
      title="薪资详情"
      width="700px"
    >
      <div v-if="selectedRecord" class="salary-detail">
        <!-- 基本信息 -->
        <div class="detail-section">
          <h4>基本信息</h4>
          <el-descriptions :column="2" border>
            <el-descriptions-item label="薪资月份">
              {{ selectedRecord.period }}
            </el-descriptions-item>
            <el-descriptions-item label="发放状态">
              <el-tag :type="getSalaryStatusType(selectedRecord.status)">
                {{ selectedRecord.status }}
              </el-tag>
            </el-descriptions-item>
            <el-descriptions-item label="发放日期">
              {{ formatDate(selectedRecord.payment_date) }}
            </el-descriptions-item>
            <el-descriptions-item label="备注">
              {{ selectedRecord.remark || '-' }}
            </el-descriptions-item>
          </el-descriptions>
        </div>

        <!-- 收入明细 -->
        <div class="detail-section">
          <h4>收入明细</h4>
          <el-table :data="selectedRecord.income_items" border>
            <el-table-column prop="name" label="项目" />
            <el-table-column prop="amount" label="金额">
              <template #default="scope">
                ¥{{ formatMoney(scope.row.amount) }}
              </template>
            </el-table-column>
          </el-table>
        </div>

        <!-- 扣款明细 -->
        <div class="detail-section">
          <h4>扣款明细</h4>
          <el-table :data="selectedRecord.deduction_items" border>
            <el-table-column prop="name" label="项目" />
            <el-table-column prop="amount" label="金额">
              <template #default="scope">
                ¥{{ formatMoney(scope.row.amount) }}
              </template>
            </el-table-column>
          </el-table>
        </div>

        <!-- 汇总信息 -->
        <div class="detail-section">
          <h4>薪资汇总</h4>
          <el-row :gutter="20">
            <el-col :span="8">
              <div class="summary-box">
                <div class="summary-title">应发工资</div>
                <div class="summary-amount income">¥{{ formatMoney(selectedRecord.summary?.gross_salary || 0) }}</div>
              </div>
            </el-col>
            <el-col :span="8">
              <div class="summary-box">
                <div class="summary-title">扣款合计</div>
                <div class="summary-amount deduction">¥{{ formatMoney(selectedRecord.summary?.total_deduction || 0) }}</div>
              </div>
            </el-col>
            <el-col :span="8">
              <div class="summary-box">
                <div class="summary-title">实发工资</div>
                <div class="summary-amount net">¥{{ formatMoney(selectedRecord.summary?.net_salary || 0) }}</div>
              </div>
            </el-col>
          </el-row>
        </div>
      </div>
      
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="showDetailDialog = false">关闭</el-button>
          <el-button 
            v-if="selectedRecord?.status === '已发放'"
            type="primary" 
            @click="downloadPayslip(selectedRecord)"
          >
            下载工资条
          </el-button>
        </span>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted, nextTick, watch } from 'vue'
import { ElMessage } from 'element-plus'
import request from '@/utils/request'
import * as echarts from 'echarts'

// 定义接口类型
interface SalaryRecord {
  id: number;
  period: string;
  base_salary: number;
  overtime_pay: number;
  bonus: number;
  gross_salary: number;
  total_deduction: number;
  net_salary: number;
  status: string;
  payment_date: string;
  remark?: string;
}

interface SalaryDetail extends SalaryRecord {
  income_items: Array<{name: string; amount: number}>;
  deduction_items: Array<{name: string; amount: number}>;
  summary: {
    gross_salary: number;
    total_deduction: number;
    net_salary: number;
  };
}

interface AnnualSummary {
  total_gross: number;
  total_deduction: number;
  total_net: number;
  average_monthly: number;
}

interface MonthlyData {
  month: number;
  gross_salary: number;
  total_deduction: number;
  net_salary: number;
  status: string;
}

interface Statistics {
  year: number;
  total_records: number;
  annual_summary: AnnualSummary;
  monthly_data: MonthlyData[];
  income_breakdown: Record<string, number>;
  deduction_breakdown: Record<string, number>;
}

// 当前激活的标签页
const activeTab = ref('records')

// 加载状态
const loading = ref(false)

// 筛选表单
const filterForm = reactive({
  year: null as number | null,
  month: null as number | null
})

// 分页信息
const pagination = reactive({
  page: 1,
  size: 10,
  total: 0
})

// 薪资记录数据
const salaryRecords = ref<SalaryRecord[]>([])

// 可选年份
const availableYears = ref<number[]>([])

// 统计数据
const statisticsYear = ref(new Date().getFullYear())
const statistics = ref<Statistics>({
  year: new Date().getFullYear(),
  total_records: 0,
  annual_summary: {
    total_gross: 0,
    total_deduction: 0,
    total_net: 0,
    average_monthly: 0
  },
  monthly_data: [],
  income_breakdown: {},
  deduction_breakdown: {}
})

// 薪资详情对话框
const showDetailDialog = ref(false)
const selectedRecord = ref<SalaryDetail | null>(null)

// 调试数据
const rawResponseData = ref<any>(null)

// 图表引用
const monthlyChartRef = ref<HTMLElement | null>(null)
const incomeChartRef = ref<HTMLElement | null>(null)
const deductionChartRef = ref<HTMLElement | null>(null)

// 工具函数
const formatMoney = (amount: number) => {
  if (!amount) return '0.00'
  return amount.toLocaleString('zh-CN', { minimumFractionDigits: 2, maximumFractionDigits: 2 })
}

const formatDate = (dateStr: string) => {
  if (!dateStr) return '-'
  return new Date(dateStr).toLocaleDateString()
}

const getSalaryStatusType = (status: string) => {
  const statusMap: Record<string, string> = {
    '已发放': 'success',
    '待发放': 'warning',
    '已撤销': 'danger'
  }
  return statusMap[status] || 'info'
}

// API 调用函数
const loadAvailableYears = async () => {
  try {
    const response = await request.get('/api/v1/user/salary/years')
    console.log('可用年份数据:', response)
    if (response && typeof response === 'object' && Array.isArray(response.years)) {
      availableYears.value = response.years
      if (!filterForm.year && availableYears.value.length > 0) {
        filterForm.year = availableYears.value[0]
      }
    }
  } catch (error: any) {
    console.error('加载年份列表失败:', error)
    ElMessage.error(error.response?.data?.detail || '加载年份列表失败')
  }
}

const loadSalaryRecords = async () => {
  loading.value = true
  
  try {
    const params = {
      year: filterForm.year,
      month: filterForm.month,
      skip: (pagination.page - 1) * pagination.size,
      limit: pagination.size
    }
    
    const response = await request.get('/api/v1/user/salary/records', { params })
    console.log('薪资记录数据:', response)
    rawResponseData.value = response
    
    if (response && typeof response === 'object') {
      salaryRecords.value = Array.isArray(response.records) ? response.records : []
      pagination.total = typeof response.total === 'number' ? response.total : 0
    } else {
      salaryRecords.value = []
      pagination.total = 0
    }
  } catch (error: any) {
    console.error('加载薪资记录失败:', error)
    ElMessage.error(error.response?.data?.detail || '加载薪资记录失败')
  } finally {
    loading.value = false
  }
}

const loadSalaryStatistics = async () => {
  try {
    const response = await request.get('/api/v1/user/salary/statistics', {
      params: { year: statisticsYear.value }
    })
    console.log('薪资统计数据:', response)
    
    if (response && typeof response === 'object') {
      // 确保数据结构完整
      statistics.value = {
        year: typeof response.year === 'number' ? response.year : statisticsYear.value,
        total_records: typeof response.total_records === 'number' ? response.total_records : 0,
        annual_summary: response.annual_summary && typeof response.annual_summary === 'object' ? {
          total_gross: Number(response.annual_summary.total_gross || 0),
          total_deduction: Number(response.annual_summary.total_deduction || 0),
          total_net: Number(response.annual_summary.total_net || 0),
          average_monthly: Number(response.annual_summary.average_monthly || 0)
        } : {
          total_gross: 0,
          total_deduction: 0,
          total_net: 0,
          average_monthly: 0
        },
        monthly_data: Array.isArray(response.monthly_data) ? response.monthly_data : [],
        income_breakdown: response.income_breakdown && typeof response.income_breakdown === 'object' ? response.income_breakdown : {},
        deduction_breakdown: response.deduction_breakdown && typeof response.deduction_breakdown === 'object' ? response.deduction_breakdown : {}
      }
      
      // 更新图表
      nextTick(() => {
        renderMonthlyChart()
        renderIncomeChart()
        renderDeductionChart()
      })
    }
  } catch (error: any) {
    console.error('加载薪资统计失败:', error)
    ElMessage.error(error.response?.data?.detail || '加载薪资统计失败')
  }
}

const viewSalaryDetail = async (record: SalaryRecord) => {
  try {
    const response = await request.get(`/api/v1/user/salary/records/${record.id}`)
    console.log('薪资详情数据:', response)
    
    if (response) {
      selectedRecord.value = response
      showDetailDialog.value = true
    }
  } catch (error: any) {
    console.error('加载薪资详情失败:', error)
    ElMessage.error(error.response?.data?.detail || '加载薪资详情失败')
  }
}

const downloadPayslip = async (record: SalaryRecord) => {
  try {
    const response = await request.post(`/api/v1/user/salary/records/${record.id}/download-payslip`)
    console.log('下载工资条响应:', response)
    
    if (response && response.download_url) {
      // 创建一个临时链接来下载文件
      const link = document.createElement('a')
      link.href = response.download_url
      link.download = response.filename || `工资条_${record.period}.pdf`
      document.body.appendChild(link)
      link.click()
      document.body.removeChild(link)
      
      ElMessage.success('工资条下载成功')
    } else if (response && response.message) {
      ElMessage.success(response.message)
    } else {
      ElMessage.warning('下载链接不可用')
    }
  } catch (error: any) {
    console.error('下载工资条失败:', error)
    ElMessage.error(error.response?.data?.detail || '下载工资条失败')
  }
}

// 重置筛选条件
const resetFilter = () => {
  filterForm.year = null
  filterForm.month = null
  pagination.page = 1
  loadSalaryRecords()
}

// 图表渲染函数
const renderMonthlyChart = () => {
  if (!monthlyChartRef.value || !statistics.value.monthly_data || statistics.value.monthly_data.length === 0) return
  
  const chart = echarts.init(monthlyChartRef.value)
  
  const months = statistics.value.monthly_data.map((item) => `${item.month}月`)
  const grossSalary = statistics.value.monthly_data.map((item) => item.gross_salary)
  const netSalary = statistics.value.monthly_data.map((item) => item.net_salary)
  
  const option = {
    title: {
      text: `${statisticsYear.value}年月度薪资趋势`,
      left: 'center'
    },
    tooltip: {
      trigger: 'axis',
      formatter: (params: any) => {
        let tooltip = `${params[0].axisValue}<br/>`
        params.forEach((param: any) => {
          tooltip += `${param.seriesName}: ¥${formatMoney(param.value)}<br/>`
        })
        return tooltip
      }
    },
    legend: {
      data: ['应发工资', '实发工资'],
      top: 30
    },
    xAxis: {
      type: 'category',
      data: months
    },
    yAxis: {
      type: 'value',
      axisLabel: {
        formatter: (value: number) => `¥${(value / 1000).toFixed(0)}k`
      }
    },
    series: [
      {
        name: '应发工资',
        type: 'line',
        data: grossSalary,
        smooth: true,
        itemStyle: {
          color: '#409EFF'
        }
      },
      {
        name: '实发工资',
        type: 'line',
        data: netSalary,
        smooth: true,
        itemStyle: {
          color: '#67C23A'
        }
      }
    ]
  }
  
  chart.setOption(option)
}

const renderIncomeChart = () => {
  if (!incomeChartRef.value || !statistics.value.income_breakdown) return
  
  const chart = echarts.init(incomeChartRef.value)
  
  const nameMap: Record<string, string> = {
    base_salary: '基本工资',
    overtime_pay: '加班费',
    bonus: '奖金',
    performance_bonus: '绩效奖金',
    attendance_bonus: '全勤奖',
    transportation_allowance: '交通补贴',
    meal_allowance: '餐补'
  }
  
  const data = Object.entries(statistics.value.income_breakdown).map(([key, value]) => {
    return {
      name: nameMap[key as keyof typeof nameMap] || key,
      value: value as number
    }
  }).filter(item => (item.value as number) > 0)
  
  const option = {
    title: {
      text: '年度收入构成',
      left: 'center'
    },
    tooltip: {
      trigger: 'item',
      formatter: '{a} <br/>{b}: ¥{c} ({d}%)'
    },
    legend: {
      orient: 'vertical',
      left: 'left',
      top: 50
    },
    series: [
      {
        name: '收入构成',
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

const renderDeductionChart = () => {
  if (!deductionChartRef.value || !statistics.value.deduction_breakdown) return
  
  const chart = echarts.init(deductionChartRef.value)
  
  const nameMap: Record<string, string> = {
    deduction: '其他扣款',
    social_security: '社保公积金',
    late_deduction: '迟到扣款',
    absence_deduction: '缺勤扣款',
    personal_tax: '个人所得税'
  }
  
  const data = Object.entries(statistics.value.deduction_breakdown).map(([key, value]) => {
    return {
      name: nameMap[key as keyof typeof nameMap] || key,
      value: value as number
    }
  }).filter(item => (item.value as number) > 0)
  
  const option = {
    title: {
      text: '年度扣款构成',
      left: 'center'
    },
    tooltip: {
      trigger: 'item',
      formatter: '{a} <br/>{b}: ¥{c} ({d}%)'
    },
    legend: {
      orient: 'vertical',
      left: 'left',
      top: 50
    },
    series: [
      {
        name: '扣款构成',
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

// 监听统计年份变化
watch(() => statisticsYear.value, () => {
  loadSalaryStatistics()
})

// 组件挂载时加载数据
onMounted(async () => {
  console.log('薪资组件已挂载，开始加载数据')
  await loadAvailableYears()
  loadSalaryRecords()
  loadSalaryStatistics()
})
</script>

<style scoped lang="scss">
.user-salary-container {
  padding: 20px;
}

.salary-header {
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

.net-salary {
  font-weight: bold;
  color: #67C23A;
}

// 统计页面样式
.statistics-section {
  .year-selector {
    margin-bottom: 20px;
    text-align: center;
  }
  
  .summary-cards {
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
  
  .chart-card {
    margin-bottom: 30px;
  }
  
  .pie-charts {
    .el-card {
      margin-bottom: 20px;
    }
  }
  
  .chart-container {
    height: 300px;
    width: 100%;
  }
}

// 薪资详情对话框样式
.salary-detail {
  .detail-section {
    margin-bottom: 30px;
    
    h4 {
      color: #333;
      margin-bottom: 15px;
      padding-bottom: 8px;
      border-bottom: 2px solid #409EFF;
    }
  }
  
  .summary-box {
    text-align: center;
    padding: 15px;
    border: 1px solid #dcdfe6;
    border-radius: 4px;
    
    .summary-title {
      color: #666;
      font-size: 14px;
      margin-bottom: 8px;
    }
    
    .summary-amount {
      font-size: 20px;
      font-weight: bold;
      
      &.income {
        color: #409EFF;
      }
      
      &.deduction {
        color: #F56C6C;
      }
      
      &.net {
        color: #67C23A;
      }
    }
  }
}

.dialog-footer {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
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
  .user-salary-container {
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
  
  .summary-cards {
    .el-col {
      margin-bottom: 15px;
    }
  }
  
  .chart-container {
    height: 250px;
  }
  
  .salary-detail {
    .summary-box {
      margin-bottom: 15px;
    }
  }
}
</style> 