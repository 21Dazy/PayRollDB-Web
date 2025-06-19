<template>
  <div class="salary-detail">
    <div class="page-header">
      <h2>薪资详情</h2>
      <div class="page-actions">
        <el-button :icon="ArrowLeft" @click="goBack">返回</el-button>
        <el-button type="primary" :icon="Printer" @click="handlePrint">打印</el-button>
        <el-button 
          v-if="salaryData && salaryData.status === 'pending'" 
          type="success" 
          :icon="Check" 
          @click="handlePay"
        >
          发放
        </el-button>
      </div>
    </div>
    
    <div class="detail-content" v-loading="loading">
      <div v-if="salaryData" ref="printSection">
        <div class="detail-header">
          <h1>{{ salaryData.year }}年{{ salaryData.month }}月工资单</h1>
          <div class="print-date">打印日期：{{ new Date().toLocaleDateString() }}</div>
        </div>
        
        <el-descriptions title="基本信息" :column="3" border>
          <el-descriptions-item label="工号">{{ getEmployeeId() }}</el-descriptions-item>
          <el-descriptions-item label="姓名">{{ getEmployeeName() }}</el-descriptions-item>
          <el-descriptions-item label="部门">{{ departmentName }}</el-descriptions-item>
          <el-descriptions-item label="职位">{{ positionName }}</el-descriptions-item>
          <el-descriptions-item label="状态">
            <el-tag :type="salaryData.status === 'paid' ? 'success' : 'warning'">
              {{ salaryData.status === 'paid' ? '已发放' : '待发放' }}
            </el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="发放日期">{{ formatPaymentDate(salaryData.paymentDate) }}</el-descriptions-item>
        </el-descriptions>
        
        <el-row :gutter="20" class="salary-summary">
          <el-col :span="8">
            <div class="summary-card">
              <div class="card-title">应发工资</div>
              <div class="card-value">¥{{ formatNumber(totalIncome) }}</div>
            </div>
          </el-col>
          <el-col :span="8">
            <div class="summary-card">
              <div class="card-title">扣除金额</div>
              <div class="card-value">¥{{ formatNumber(totalDeduction) }}</div>
            </div>
          </el-col>
          <el-col :span="8">
            <div class="summary-card primary">
              <div class="card-title">实发工资</div>
              <div class="card-value">¥{{ formatNumber(calculateNetSalary()) }}</div>
            </div>
          </el-col>
        </el-row>
        
        <div class="salary-details">
          <h3>工资明细</h3>
          
          <el-row :gutter="20">
            <el-col :span="12">
              <div class="detail-section">
                <h4>收入项</h4>
                <el-table :data="incomeItems" border stripe>
                  <el-table-column prop="name" label="项目" />
                  <el-table-column prop="amount" label="金额">
                    <template #default="{ row }">
                      {{ formatCurrency(row.amount) }}
                    </template>
                  </el-table-column>
                  <el-table-column label="占比">
                    <template #default="{ row }">
                      {{ calculatePercentage(row.amount, totalIncome) }}%
                    </template>
                  </el-table-column>
                </el-table>
                <div class="section-total">
                  收入合计：<span>{{ formatCurrency(totalIncome) }}</span>
                </div>
              </div>
            </el-col>
            
            <el-col :span="12">
              <div class="detail-section">
                <h4>扣除项</h4>
                <el-table :data="deductionItems" border stripe>
                  <el-table-column prop="name" label="项目" />
                  <el-table-column prop="amount" label="金额">
                    <template #default="{ row }">
                      {{ formatCurrency(row.amount) }}
                    </template>
                  </el-table-column>
                  <el-table-column label="占比">
                    <template #default="{ row }">
                      {{ calculatePercentage(row.amount, totalDeduction) }}%
                    </template>
                  </el-table-column>
                </el-table>
                <div class="section-total">
                  扣除合计：<span>{{ formatCurrency(totalDeduction) }}</span>
                </div>
              </div>
            </el-col>
          </el-row>
          
          <!-- 薪资占比表格 -->
          <el-row :gutter="20" style="margin-top: 30px;">
            <el-col :span="12">
              <div class="chart-container">
                <h4>收入项占比</h4>
                <el-table :data="incomeItems" border stripe>
                  <el-table-column prop="name" label="项目" />
                  <el-table-column label="金额占比">
                    <template #default="{ row }">
                      {{ calculatePercentage(row.amount, totalIncome) }}%
                    </template>
                  </el-table-column>
                  <el-table-column label="金额">
                    <template #default="{ row }">
                      {{ formatCurrency(row.amount) }}
                    </template>
                  </el-table-column>
                </el-table>
                <el-empty v-if="!loading && (!incomeItems.length)" description="暂无收入项数据" :image-size="80"></el-empty>
              </div>
            </el-col>
            <el-col :span="12">
              <div class="chart-container">
                <h4>扣除项占比</h4>
                <el-table :data="deductionItems" border stripe>
                  <el-table-column prop="name" label="项目" />
                  <el-table-column label="金额占比">
                    <template #default="{ row }">
                      {{ calculatePercentage(row.amount, totalDeduction) }}%
                    </template>
                  </el-table-column>
                  <el-table-column label="金额">
                    <template #default="{ row }">
                      {{ formatCurrency(row.amount) }}
                    </template>
                  </el-table-column>
                </el-table>
                <el-empty v-if="!loading && (!deductionItems.length)" description="暂无扣除项数据" :image-size="80"></el-empty>
              </div>
            </el-col>
          </el-row>
        </div>
        
        <div class="remark">
          <h3>备注</h3>
          <p v-if="salaryData.remark">{{ salaryData.remark }}</p>
          <p v-else>无</p>
        </div>
        
        <div class="signatures">
          <div class="signature-item">
            <div>财务部门（盖章）：</div>
            <div class="signature-line"></div>
          </div>
          <div class="signature-item">
            <div>员工签字：</div>
            <div class="signature-line"></div>
          </div>
          <div class="signature-item">
            <div>日期：</div>
            <div class="signature-line"></div>
          </div>
        </div>
      </div>
      
      <el-empty v-else description="未找到薪资记录" />
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { ArrowLeft, Printer, Check } from '@element-plus/icons-vue'
import { useSalariesStore, type SalaryRecord as BaseSalaryRecord, type SalaryDetail } from '@/stores/salaries'
import { useDepartmentsStore } from '@/stores/departments'
import { usePositionsStore } from '@/stores/positions'

// 扩展SalaryRecord类型，添加可能存在的personalTax属性
interface SalaryRecord extends BaseSalaryRecord {
  personalTax?: number;
  positionId?: number;
}

const route = useRoute()
const router = useRouter()
const salariesStore = useSalariesStore()
const departmentsStore = useDepartmentsStore()
const positionsStore = usePositionsStore()

const salaryId = computed(() => Number(route.params.id))
const loading = ref(false)
const salaryData = computed(() => salariesStore.currentSalaryRecord as SalaryRecord | null)
const printSection = ref<HTMLElement | null>(null)

// 收入项 - 从详情中提取
const incomeItems = computed(() => {
  // 确保数据存在且结构正确
  if (!salaryData.value || !salaryData.value.details || !Array.isArray(salaryData.value.details)) {
    console.warn('薪资详情数据不完整或格式不正确', salaryData.value)
    
    // 如果没有明细数据但有基本工资，则添加一个基本工资项
    if (salaryData.value) {
      const items = [];
      
      // 添加基本工资
      if (typeof salaryData.value.baseSalary === 'number' && salaryData.value.baseSalary > 0) {
        items.push({
          name: '基本工资',
          amount: salaryData.value.baseSalary
        });
      }
      
      // 添加加班费
      if (typeof salaryData.value.overtimePay === 'number' && salaryData.value.overtimePay > 0) {
        items.push({
          name: '加班费',
          amount: salaryData.value.overtimePay
        });
      }
      
      // 添加奖金
      if (typeof salaryData.value.bonus === 'number' && salaryData.value.bonus > 0) {
        items.push({
          name: '奖金',
          amount: salaryData.value.bonus
        });
      }
      
      // 添加绩效奖金
      if (typeof salaryData.value.performanceBonus === 'number' && salaryData.value.performanceBonus > 0) {
        items.push({
          name: '绩效奖金',
          amount: salaryData.value.performanceBonus
        });
      }
      
      // 添加全勤奖
      if (typeof salaryData.value.attendanceBonus === 'number' && salaryData.value.attendanceBonus > 0) {
        items.push({
          name: '全勤奖',
          amount: salaryData.value.attendanceBonus
        });
      }
      
      // 添加交通补贴
      if (typeof salaryData.value.transportationAllowance === 'number' && salaryData.value.transportationAllowance > 0) {
        items.push({
          name: '交通补贴',
          amount: salaryData.value.transportationAllowance
        });
      }
      
      // 添加餐补
      if (typeof salaryData.value.mealAllowance === 'number' && salaryData.value.mealAllowance > 0) {
        items.push({
          name: '餐补',
          amount: salaryData.value.mealAllowance
        });
      }
      
      return items;
    }
    
    return []
  }
  
  try {
    console.log('原始薪资详情数据:', JSON.stringify(salaryData.value.details))
    
    const items = salaryData.value.details
      .filter((detail: any) => {
        // 处理可能的数组嵌套问题
        if (Array.isArray(detail)) {
          console.warn('详情项是数组格式，取第一个元素', detail)
          detail = detail[0]
        }
        
        // 检查item是否存在且类型正确
        const valid = detail && 
          detail.item && 
          typeof detail.item === 'object' && 
          detail.item.type === 'addition' && 
          (typeof detail.amount === 'number' || typeof parseFloat(detail.amount) === 'number') && 
          parseFloat(detail.amount) > 0
        
        if (!valid && detail) {
          console.warn('过滤掉无效的收入项:', JSON.stringify(detail))
        }
        
        return valid
      })
      .map((detail: any) => {
        // 处理可能的数组嵌套问题
        if (Array.isArray(detail)) {
          detail = detail[0]
        }
        
        return {
          name: detail.item?.name || '未命名项目',
          amount: typeof detail.amount === 'number' ? detail.amount : parseFloat(detail.amount) || 0
        }
      })
    
    // 如果明细数据中没有收入项但有相关数据，则添加相应项目
    if (salaryData.value) {
      // 添加基本工资
      if (typeof salaryData.value.baseSalary === 'number' && salaryData.value.baseSalary > 0 && 
          !items.some(item => item.name.includes('基本工资'))) {
        items.push({
          name: '基本工资',
          amount: salaryData.value.baseSalary
        });
      }
      
      // 添加加班费
      if (typeof salaryData.value.overtimePay === 'number' && salaryData.value.overtimePay > 0 && 
          !items.some(item => item.name.includes('加班费'))) {
        items.push({
          name: '加班费',
          amount: salaryData.value.overtimePay
        });
      }
      
      // 添加奖金
      if (typeof salaryData.value.bonus === 'number' && salaryData.value.bonus > 0 && 
          !items.some(item => item.name.includes('奖金') && !item.name.includes('绩效奖金'))) {
        items.push({
          name: '奖金',
          amount: salaryData.value.bonus
        });
      }
      
      // 添加绩效奖金
      if (typeof salaryData.value.performanceBonus === 'number' && salaryData.value.performanceBonus > 0 && 
          !items.some(item => item.name.includes('绩效奖金'))) {
        items.push({
          name: '绩效奖金',
          amount: salaryData.value.performanceBonus
        });
      }
      
      // 添加全勤奖
      if (typeof salaryData.value.attendanceBonus === 'number' && salaryData.value.attendanceBonus > 0 && 
          !items.some(item => item.name.includes('全勤奖'))) {
        items.push({
          name: '全勤奖',
          amount: salaryData.value.attendanceBonus
        });
      }
      
      // 添加交通补贴
      if (typeof salaryData.value.transportationAllowance === 'number' && salaryData.value.transportationAllowance > 0 && 
          !items.some(item => item.name.includes('交通补贴'))) {
        items.push({
          name: '交通补贴',
          amount: salaryData.value.transportationAllowance
        });
      }
      
      // 添加餐补
      if (typeof salaryData.value.mealAllowance === 'number' && salaryData.value.mealAllowance > 0 && 
          !items.some(item => item.name.includes('餐补'))) {
        items.push({
          name: '餐补',
          amount: salaryData.value.mealAllowance
        });
      }
    }
    
    console.log('处理后的收入项:', items)
    return items
  } catch (error) {
    console.error('处理收入项数据时出错:', error)
    return []
  }
})

// 扣除项 - 从详情中提取
const deductionItems = computed(() => {
  // 确保数据存在且结构正确
  if (!salaryData.value || !salaryData.value.details || !Array.isArray(salaryData.value.details)) {
    console.warn('薪资详情数据不完整或格式不正确', salaryData.value)
    
    // 如果没有明细数据但有扣除金额或社保，则添加相应项目
    if (salaryData.value) {
      const items = []
      
      // 添加其他扣除
      if (typeof salaryData.value.deduction === 'number' && salaryData.value.deduction > 0) {
        items.push({
          name: '其他扣除',
          amount: salaryData.value.deduction
        })
      }
      
      // 添加社会保险
      if (typeof salaryData.value.socialSecurity === 'number' && salaryData.value.socialSecurity > 0) {
        items.push({
          name: '社会保险',
          amount: salaryData.value.socialSecurity
        })
      }
      
      // 添加个人所得税
      if (typeof salaryData.value.personalTax === 'number' && salaryData.value.personalTax > 0) {
        items.push({
          name: '个人所得税',
          amount: salaryData.value.personalTax
        })
      }
      
      // 添加迟到扣款
      if (typeof salaryData.value.lateDeduction === 'number' && salaryData.value.lateDeduction > 0) {
        items.push({
          name: '迟到扣款',
          amount: salaryData.value.lateDeduction
        })
      }
      
      // 添加缺勤扣款
      if (typeof salaryData.value.absenceDeduction === 'number' && salaryData.value.absenceDeduction > 0) {
        items.push({
          name: '缺勤扣款',
          amount: salaryData.value.absenceDeduction
        })
      }
      
      return items
    }
    
    return []
  }
  
  try {
    const items = salaryData.value.details
      .filter((detail: any) => {
        // 处理可能的数组嵌套问题
        if (Array.isArray(detail)) {
          console.warn('详情项是数组格式，取第一个元素', detail)
          detail = detail[0]
        }
        
        // 检查item是否存在且类型正确
        const valid = detail && 
          detail.item && 
          typeof detail.item === 'object' && 
          detail.item.type === 'deduction' && 
          (typeof detail.amount === 'number' || typeof parseFloat(detail.amount) === 'number') && 
          parseFloat(detail.amount) > 0
          
        if (!valid && detail) {
          console.warn('过滤掉无效的扣除项:', JSON.stringify(detail))
        }
        
        return valid
      })
      .map((detail: any) => {
        // 处理可能的数组嵌套问题
        if (Array.isArray(detail)) {
          detail = detail[0]
        }
        
        return {
          name: detail.item?.name || '未命名项目',
          amount: typeof detail.amount === 'number' ? detail.amount : parseFloat(detail.amount) || 0
        }
      })
    
    // 如果明细数据中没有扣除项但有相关数据，则添加相应项目
    if (salaryData.value) {
      // 添加其他扣除
      if (typeof salaryData.value.deduction === 'number' && salaryData.value.deduction > 0 && 
          !items.some(item => item.name.includes('扣除') && !item.name.includes('迟到扣款') && !item.name.includes('缺勤扣款'))) {
        items.push({
          name: '其他扣除',
          amount: salaryData.value.deduction
        })
      }
      
      // 添加社会保险
      if (typeof salaryData.value.socialSecurity === 'number' && salaryData.value.socialSecurity > 0 && 
          !items.some(item => item.name.includes('社会保险') || item.name.includes('社保'))) {
        items.push({
          name: '社会保险',
          amount: salaryData.value.socialSecurity
        })
      }
      
      // 添加个人所得税
      if (typeof salaryData.value.personalTax === 'number' && salaryData.value.personalTax > 0 && 
          !items.some(item => item.name.includes('个人所得税'))) {
        items.push({
          name: '个人所得税',
          amount: salaryData.value.personalTax
        })
      }
      
      // 添加迟到扣款
      if (typeof salaryData.value.lateDeduction === 'number' && salaryData.value.lateDeduction > 0 && 
          !items.some(item => item.name.includes('迟到扣款'))) {
        items.push({
          name: '迟到扣款',
          amount: salaryData.value.lateDeduction
        })
      }
      
      // 添加缺勤扣款
      if (typeof salaryData.value.absenceDeduction === 'number' && salaryData.value.absenceDeduction > 0 && 
          !items.some(item => item.name.includes('缺勤扣款'))) {
        items.push({
          name: '缺勤扣款',
          amount: salaryData.value.absenceDeduction
        })
      }
    }
    
    console.log('处理后的扣除项:', items)
    return items
  } catch (error) {
    console.error('处理扣除项数据时出错:', error)
    return []
  }
})

// 总收入
const totalIncome = computed(() => {
  if (!incomeItems.value || !incomeItems.value.length) {
    // 如果没有收入项，尝试从基本数据中计算
    if (salaryData.value) {
      let total = 0;
      
      // 添加基本工资
      if (typeof salaryData.value.baseSalary === 'number') {
        total += salaryData.value.baseSalary;
      }
      
      // 添加加班费
      if (typeof salaryData.value.overtimePay === 'number') {
        total += salaryData.value.overtimePay;
      }
      
      // 添加奖金
      if (typeof salaryData.value.bonus === 'number') {
        total += salaryData.value.bonus;
      }
      
      // 添加绩效奖金
      if (typeof salaryData.value.performanceBonus === 'number') {
        total += salaryData.value.performanceBonus;
      }
      
      // 添加全勤奖
      if (typeof salaryData.value.attendanceBonus === 'number') {
        total += salaryData.value.attendanceBonus;
      }
      
      // 添加交通补贴
      if (typeof salaryData.value.transportationAllowance === 'number') {
        total += salaryData.value.transportationAllowance;
      }
      
      // 添加餐补
      if (typeof salaryData.value.mealAllowance === 'number') {
        total += salaryData.value.mealAllowance;
      }
      
      return total;
    }
    return 0;
  }
  return incomeItems.value.reduce((sum: number, item: {amount: number}) => sum + (item.amount || 0), 0);
});

// 总扣除
const totalDeduction = computed(() => {
  if (!deductionItems.value || !deductionItems.value.length) {
    // 如果没有扣除项，尝试从基本数据中计算
    if (salaryData.value) {
      let total = 0;
      
      // 添加其他扣除
      if (typeof salaryData.value.deduction === 'number') {
        total += salaryData.value.deduction;
      }
      
      // 添加社会保险
      if (typeof salaryData.value.socialSecurity === 'number') {
        total += salaryData.value.socialSecurity;
      }
      
      // 添加个人所得税
      if (typeof salaryData.value.personalTax === 'number') {
        total += salaryData.value.personalTax;
      }
      
      // 添加迟到扣款
      if (typeof salaryData.value.lateDeduction === 'number') {
        total += salaryData.value.lateDeduction;
      }
      
      // 添加缺勤扣款
      if (typeof salaryData.value.absenceDeduction === 'number') {
        total += salaryData.value.absenceDeduction;
      }
      
      return total;
    }
    return 0;
  }
  return deductionItems.value.reduce((sum: number, item: {amount: number}) => sum + (item.amount || 0), 0);
});

// 格式化货币
const formatCurrency = (value: number | string | undefined | null): string => {
  if (value === undefined || value === null) return '¥0.00'
  
  // 确保value是数字
  const numValue = typeof value === 'number' ? value : parseFloat(value) || 0
  return `¥${formatNumber(numValue)}`
}

// 格式化数字
const formatNumber = (value: number | string): string => {
  if (value === undefined || value === null) return '0.00'
  
  // 转换为数字
  const numValue = typeof value === 'number' ? value : parseFloat(value)
  
  if (isNaN(numValue)) return '0.00'
  return numValue.toFixed(2)
}

// 返回列表
const goBack = () => {
  router.push('/salary')
}

// 打印工资单
const handlePrint = () => {
  if (!printSection.value) return
  
  const printContents = printSection.value.innerHTML
  const originalContents = document.body.innerHTML
  
  document.body.innerHTML = `
    <html>
      <head>
        <title>薪资单打印</title>
        <style>
          body { font-family: Arial, sans-serif; }
          .detail-header { text-align: center; margin-bottom: 20px; }
          .detail-header h1 { margin-bottom: 5px; }
          .print-date { font-size: 12px; color: #666; }
          table { width: 100%; border-collapse: collapse; margin: 15px 0; }
          table, th, td { border: 1px solid #ddd; }
          th, td { padding: 8px; text-align: left; }
          .signatures { display: flex; justify-content: space-between; margin-top: 50px; }
          .signature-item { flex: 1; }
          .signature-line { border-bottom: 1px solid #000; margin-top: 20px; }
        </style>
      </head>
      <body>
        ${printContents}
      </body>
    </html>
  `
  
  window.print()
  document.body.innerHTML = originalContents
}

// 发放工资
const handlePay = () => {
  if (!salaryData.value) return
  
  ElMessageBox.confirm(
    `确定要发放 ${salaryData.value.employeeName} ${salaryData.value.year}年${salaryData.value.month}月的工资吗？`,
    '发放确认',
    {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning',
    }
  ).then(async () => {
    try {
      await salariesStore.paySalary(salaryId.value)
      ElMessage.success(`已成功发放 ${salaryData.value?.employeeName} 的工资`)
    } catch (error) {
      console.error('发放工资失败:', error)
      ElMessage.error('发放工资失败')
    }
  }).catch(() => {
    ElMessage.info('已取消发放')
  })
}

// 获取薪资详情
const fetchSalaryDetail = async () => {
  loading.value = true
  
  try {
    // 清空当前数据，避免显示旧数据
    salariesStore.currentSalaryRecord = null
    
    const currentId = salaryId.value
    console.log(`正在获取薪资记录详情, ID: ${currentId}, 路由参数: ${route.params.id}`)
    const result = await salariesStore.getSalaryRecord(currentId)
    console.log(`获取薪资详情成功, ID: ${currentId}`, result ? '数据有效' : '数据无效')
    
    // 检查是否有详情数据
    if (result && result.details && result.details.length > 0) {
      console.log('薪资详情包含 ' + result.details.length + ' 条明细数据')
      
      // 检查每条明细数据的结构
      result.details.forEach((detail: any, index: number) => {
        console.log(`明细项 ${index + 1}:`, JSON.stringify(detail))
        if (!detail.item || typeof detail.item !== 'object') {
          console.error(`明细项 ${index + 1} 缺少item对象或格式错误`)
        }
        if (detail.item && !detail.item.type) {
          console.error(`明细项 ${index + 1} 的item对象缺少type属性`)
        }
        if (typeof detail.amount !== 'number') {
          console.error(`明细项 ${index + 1} 的amount不是数字类型`)
        }
      })
    } else {
      console.warn('薪资详情没有明细数据')
    }
    
    // 处理员工信息
    if (result && result.employee) {
      console.log('处理员工信息:', JSON.stringify(result.employee))
      
      // 确保员工ID和姓名存在
      if (!result.employeeId && result.employee.id) {
        result.employeeId = result.employee.id
      }
      
      if (!result.employeeName && result.employee.name) {
        result.employeeName = result.employee.name
      }
      
      // 处理部门信息
      if (result.employee.department_id && !result.departmentName) {
        if (result.employee.department && result.employee.department.name) {
          result.departmentName = result.employee.department.name
        } else {
          console.warn('员工有部门ID但没有部门名称:', result.employee.department_id)
        }
      }
      
      // 处理职位信息
      if (result.employee.position_id && !result.positionName) {
        if (result.employee.position && result.employee.position.name) {
          result.positionName = result.employee.position.name
        } else {
          console.warn('员工有职位ID但没有职位名称:', result.employee.position_id)
        }
      }
    }
    
    // 处理updated_at字段的警告问题
    if (result && result.details && Array.isArray(result.details)) {
      result.details = result.details.map((detail: any) => {
        // 处理可能的数组嵌套问题
        if (Array.isArray(detail)) {
          detail = detail[0] || {}
        }
        
        // 确保updated_at字段存在
        if (!detail.updated_at && detail.created_at) {
          detail.updated_at = detail.created_at
        }
        
        return detail
      })
    }
    
    return result
  } catch (error) {
    console.error(`获取薪资详情失败, ID: ${salaryId.value}`, error)
    ElMessage.error('获取薪资详情失败')
    return null
  } finally {
    loading.value = false
  }
}

// 计算百分比
const calculatePercentage = (value: number | string | undefined | null, total: number | string | undefined | null): string => {
  // 转换为数字
  const numValue = value === undefined || value === null ? 0 : 
    typeof value === 'number' ? value : parseFloat(value) || 0
  
  const numTotal = total === undefined || total === null ? 0 : 
    typeof total === 'number' ? total : parseFloat(total) || 0
  
  // 检查总数是否为0
  if (numTotal === 0) return '0.00'
  
  // 计算百分比
  return ((numValue / numTotal) * 100).toFixed(2)
}

// 获取员工ID
const getEmployeeId = (): string => {
  if (!salaryData.value) return '-'
  
  // 尝试从不同来源获取员工ID
  if (salaryData.value.employeeId) {
    return String(salaryData.value.employeeId)
  }
  
  if (salaryData.value.employee && salaryData.value.employee.id) {
    return String(salaryData.value.employee.id)
  }
  
  return '-'
}

// 获取员工姓名
const getEmployeeName = (): string => {
  if (!salaryData.value) return '-'
  
  // 尝试从不同来源获取员工姓名
  if (salaryData.value.employeeName) {
    return salaryData.value.employeeName
  }
  
  if (salaryData.value.employee && salaryData.value.employee.name) {
    return salaryData.value.employee.name
  }
  
  return '-'
}

// 部门和职位名称的响应式引用
const departmentName = ref('-')
const positionName = ref('-')

// 初始化
onMounted(async () => {
  try {
    console.log('组件挂载，开始获取薪资详情')
    await fetchSalaryDetail()
    
    // 获取部门和职位名称
    departmentName.value = await getDepartmentName()
    positionName.value = await getPositionName()
  } catch (error) {
    console.error('初始化失败:', error)
  }
})

// 监听路由参数变化，重新获取薪资详情
watch(
  () => route.params.id,
  async (newId) => {
    if (newId) {
      console.log('路由参数变化，重新获取薪资详情:', newId)
      await fetchSalaryDetail()
      
      // 重新获取部门和职位名称
      departmentName.value = await getDepartmentName()
      positionName.value = await getPositionName()
    }
  },
  { immediate: false } // 确保只在参数变化时触发，而不是组件初始化时
)

// 获取部门名称
const getDepartmentName = async (): Promise<string> => {
  if (!salaryData.value) return '-'
  
  // 尝试从不同来源获取部门名称
  if (salaryData.value.departmentName) {
    return salaryData.value.departmentName
  }
  
  // 如果有部门ID，从部门store中获取名称
  if (salaryData.value.departmentId || 
      (salaryData.value.employee && salaryData.value.employee.department_id)) {
    const departmentId = salaryData.value.departmentId || salaryData.value.employee.department_id
    try {
      // 先检查store中是否已有该部门数据
      const departments = departmentsStore.departments
      const department = departments.find(d => d.id === departmentId)
      
      if (department) {
        return department.name
      }
      
      // 如果store中没有，则请求获取
      const result = await departmentsStore.getDepartment(departmentId)
      if (result && result.name) {
        return result.name
      }
    } catch (error) {
      console.error('获取部门信息失败:', error)
    }
    
    return `部门ID: ${departmentId}`
  }
  
  if (salaryData.value.employee && 
      salaryData.value.employee.department && 
      salaryData.value.employee.department.name) {
    return salaryData.value.employee.department.name
  }
  
  return '-'
}

// 获取职位名称
const getPositionName = async (): Promise<string> => {
  if (!salaryData.value) return '-'
  
  // 尝试从不同来源获取职位名称
  if (salaryData.value.positionName) {
    return salaryData.value.positionName
  }
  
  // 如果有职位ID，从职位store中获取名称
  if (salaryData.value.positionId || 
      (salaryData.value.employee && salaryData.value.employee.position_id)) {
    const positionId = salaryData.value.positionId || salaryData.value.employee.position_id
    try {
      // 先检查store中是否已有该职位数据
      const positions = positionsStore.positions
      const position = positions.find(p => p.id === positionId)
      
      if (position) {
        return position.name
      }
      
      // 如果store中没有，则请求获取
      const result = await positionsStore.getPosition(positionId)
      if (result && result.name) {
        return result.name
      }
    } catch (error) {
      console.error('获取职位信息失败:', error)
    }
    
    return `职位ID: ${positionId}`
  }
  
  if (salaryData.value.employee && 
      salaryData.value.employee.position && 
      salaryData.value.employee.position.name) {
    return salaryData.value.employee.position.name
  }
  
  return '-'
}

// 格式化发放日期
const formatPaymentDate = (dateString: string | null | undefined): string => {
  if (!dateString) return '-'
  
  try {
    const date = new Date(dateString)
    if (isNaN(date.getTime())) return '-'
    
    return date.toLocaleDateString('zh-CN', {
      year: 'numeric',
      month: '2-digit',
      day: '2-digit',
      hour: '2-digit',
      minute: '2-digit'
    })
  } catch (error) {
    console.error('日期格式化错误:', error)
    return '-'
  }
}

// 计算实发工资
const calculateNetSalary = () => {
  if (!salaryData.value) return 0
  
  let netSalary = 0
  
  // 计算应发工资
  let totalIncome = 0
  if (incomeItems.value && incomeItems.value.length > 0) {
    totalIncome = incomeItems.value.reduce((sum: number, item: {amount: number}) => sum + (item.amount || 0), 0)
  }
  
  // 计算扣除金额
  let totalDeduction = 0
  if (deductionItems.value && deductionItems.value.length > 0) {
    totalDeduction = deductionItems.value.reduce((sum: number, item: {amount: number}) => sum + (item.amount || 0), 0)
  }
  
  // 计算实发工资
  netSalary = totalIncome - totalDeduction
  
  return netSalary
}
</script>

<style scoped lang="scss">
.salary-detail {
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
  
  .detail-content {
    background-color: #fff;
    padding: 30px;
    border-radius: 4px;
    box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.04);
  }
  
  .detail-header {
    text-align: center;
    margin-bottom: 30px;
    
    h1 {
      font-size: 24px;
      margin-bottom: 10px;
    }
    
    .print-date {
      font-size: 14px;
      color: #999;
    }
  }
  
  .salary-summary {
    margin: 30px 0;
    
    .summary-card {
      background-color: #f7f7f7;
      padding: 20px;
      border-radius: 4px;
      text-align: center;
      
      &.primary {
        background-color: #ecf5ff;
        border: 1px solid #d9ecff;
      }
      
      .card-title {
        font-size: 14px;
        color: #606266;
        margin-bottom: 10px;
      }
      
      .card-value {
        font-size: 24px;
        font-weight: bold;
        color: #303133;
      }
    }
  }
  
  .salary-details {
    margin: 30px 0;
    
    h3 {
      font-size: 18px;
      margin-bottom: 20px;
      font-weight: 600;
    }
    
    h4 {
      font-size: 16px;
      margin-bottom: 15px;
    }
    
    .detail-section {
      margin-bottom: 20px;
      
      .section-total {
        margin-top: 10px;
        text-align: right;
        font-weight: bold;
        
        span {
          font-size: 16px;
          color: #409eff;
        }
      }
    }
  }
  
  .remark {
    margin: 30px 0;
    
    h3 {
      font-size: 18px;
      margin-bottom: 10px;
      font-weight: 600;
    }
    
    p {
      color: #606266;
      line-height: 1.6;
    }
  }
  
  .signatures {
    margin-top: 50px;
    display: flex;
    justify-content: space-between;
    
    .signature-item {
      flex: 1;
      margin: 0 20px;
      
      .signature-line {
        margin-top: 40px;
        border-bottom: 1px solid #dcdfe6;
      }
    }
  }
  
  @media print {
    .page-header, .page-actions {
      display: none;
    }
  }
  
  .chart-container {
    background-color: #fff;
    padding: 20px;
    border-radius: 4px;
    box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.04);
    margin-bottom: 20px;
    
    h4 {
      font-size: 16px;
      margin-bottom: 15px;
      text-align: center;
    }
  }
}
</style> 