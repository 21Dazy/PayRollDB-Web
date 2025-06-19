import { ref, computed } from 'vue'
import { defineStore } from 'pinia'
import { get, post, put, del } from '@/utils/request'

// 薪资项目类型定义
export interface SalaryItem {
  id: number;
  name: string;
  type: 'addition' | 'deduction';
  is_percentage: boolean;
  is_system: boolean;
}

// 薪资明细类型定义
export interface SalaryDetail {
  id: number;
  item: SalaryItem;
  amount: number;
  created_at?: string;
  updated_at?: string;
}

// 薪资记录类型定义
export interface SalaryRecord {
  id: number;
  year: number;
  month: number;
  employeeId: string | number;
  employeeName: string;
  departmentId: number;
  departmentName: string;
  positionName?: string;
  baseSalary: number;
  overtimePay: number;
  bonus: number;
  performanceBonus: number;
  attendanceBonus: number;
  transportationAllowance: number;
  mealAllowance: number;
  deduction: number;
  socialSecurity: number;
  lateDeduction: number;
  absenceDeduction: number;
  personalTax: number;
  netSalary: number;
  status: 'pending' | 'paid';
  paymentDate: string | null;
  remark?: string;
  createdAt?: string;
  updatedAt?: string;
  details?: SalaryDetail[];
  employee?: any; // 员工信息
}

// 查询参数接口
export interface QueryParams {
  year?: number;
  month?: number;
  department_id?: number;
  employee_id?: string;
  keyword?: string;
  status?: string;
  skip?: number;
  limit?: number;
}

export const useSalariesStore = defineStore('salaries', () => {
  // 状态
  const salaryRecords = ref<SalaryRecord[]>([])
  const currentSalaryRecord = ref<SalaryRecord | null>(null)
  const totalCount = ref(0)
  const isLoading = ref(false)
  const error = ref<string | null>(null)

  // 获取薪资记录列表
  async function getSalaryRecordsForDisplay(params: QueryParams = {}) {
    isLoading.value = true
    error.value = null
    
    try {
      // 直接传递参数，不要嵌套在params对象中
      const response = await get('/api/v1/salaries/records', params)
      
      if (Array.isArray(response)) {
        // 确保所有数值字段都有默认值
        salaryRecords.value = response.map((record: any) => ({
          ...record,
          baseSalary: record.baseSalary || 0,
          overtimePay: record.overtimePay || 0,
          bonus: record.bonus || 0,
          performanceBonus: record.performanceBonus || 0,
          attendanceBonus: record.attendanceBonus || 0,
          transportationAllowance: record.transportationAllowance || 0,
          mealAllowance: record.mealAllowance || 0,
          deduction: record.deduction || 0,
          lateDeduction: record.lateDeduction || 0,
          absenceDeduction: record.absenceDeduction || 0,
          socialSecurity: record.socialSecurity || 0,
          personalTax: record.personalTax || 0,
          netSalary: record.netSalary || 0
        }))
        totalCount.value = response.length
      } else if (response && response.items) {
        // 确保所有数值字段都有默认值
        salaryRecords.value = response.items.map((record: any) => ({
          ...record,
          baseSalary: record.baseSalary || 0,
          overtimePay: record.overtimePay || 0,
          bonus: record.bonus || 0,
          performanceBonus: record.performanceBonus || 0,
          attendanceBonus: record.attendanceBonus || 0,
          transportationAllowance: record.transportationAllowance || 0,
          mealAllowance: record.mealAllowance || 0,
          deduction: record.deduction || 0,
          lateDeduction: record.lateDeduction || 0,
          absenceDeduction: record.absenceDeduction || 0,
          socialSecurity: record.socialSecurity || 0,
          personalTax: record.personalTax || 0,
          netSalary: record.netSalary || 0
        }))
        totalCount.value = response.total || response.items.length
      } else {
        console.error('无效的薪资数据格式:', response)
        salaryRecords.value = []
        totalCount.value = 0
      }
      
      return salaryRecords.value
    } catch (err) {
      console.error('获取薪资记录失败:', err)
      error.value = '获取薪资记录失败'
      throw err
    } finally {
      isLoading.value = false
    }
  }

  // 获取单个薪资记录详情
  async function getSalaryRecord(id: number) {
    isLoading.value = true
    error.value = null
    
    try {
      console.log(`正在获取薪资记录详情, ID: ${id}`)
      
      // 先清空当前记录，避免显示旧数据
      currentSalaryRecord.value = null
      
      const response = await get(`/api/v1/salaries/records/${id}`)
      
      // 验证响应数据
      if (!response) {
        console.error('获取薪资记录详情失败: 服务器返回空数据')
        error.value = '获取薪资记录详情失败: 服务器返回空数据'
        return null
      }
      
      // 检查详情数据
      if (!response.details || !Array.isArray(response.details)) {
        console.warn('薪资记录详情中缺少明细数据或格式不正确')
        // 确保details字段存在且为数组
        response.details = response.details || []
      } else {
        // 处理详情数据，确保格式正确
        const processedDetails = []
        
        // 检查每个明细项的结构
        for (let i = 0; i < response.details.length; i++) {
          let detail = response.details[i]
          console.log(`原始薪资明细项 ${i + 1}:`, JSON.stringify(detail))
          
          // 处理可能的数组嵌套问题
          if (Array.isArray(detail)) {
            console.warn(`明细项 ${i + 1} 是数组格式，取第一个元素`)
            detail = detail[0]
          }
          
          if (!detail) continue
          
          // 检查并修复item字段
          if (!detail.item || typeof detail.item !== 'object') {
            console.error(`明细项 ${i + 1} 缺少item对象或格式错误`)
            continue
          }
          
          // 检查item对象的必要字段
          if (!detail.item.type) {
            console.error(`明细项 ${i + 1} 的item对象缺少type属性`)
            continue
          }
          
          if (!detail.item.name) {
            console.warn(`明细项 ${i + 1} 的item对象缺少name属性，使用默认名称`)
            detail.item.name = '未命名项目'
          }
          
          // 确保amount是数字类型
          if (typeof detail.amount !== 'number') {
            console.warn(`明细项 ${i + 1} 的amount不是数字类型，尝试转换: ${detail.amount}`)
            detail.amount = parseFloat(detail.amount) || 0
          }
          
          // 确保created_at和updated_at字段存在
          if (!detail.created_at) {
            console.warn(`明细项 ${i + 1} 缺少created_at字段，使用当前时间`)
            detail.created_at = new Date().toISOString()
          }
          
          if (!detail.updated_at) {
            console.warn(`明细项 ${i + 1} 缺少updated_at字段，使用当前时间`)
            detail.updated_at = new Date().toISOString()
          }
          
          // 添加到处理后的详情列表
          processedDetails.push(detail)
        }
        
        // 替换原始详情数据
        response.details = processedDetails
        console.log('处理后的薪资详情数据:', JSON.stringify(processedDetails))
      }
      
      console.log('获取薪资记录详情成功:', JSON.stringify(response))
      
      // 处理员工信息
      if (response.employee) {
        // 确保前端能够正确访问员工信息
        const employeeData = response.employee
        
        // 将employee对象中的信息复制到记录的顶层属性中
        response.employeeId = employeeData.id
        response.employeeName = employeeData.name
        
        // 处理部门和职位信息
        if (employeeData.department) {
          response.departmentId = employeeData.department.id
          response.departmentName = employeeData.department.name
        }
        
        if (employeeData.position) {
          response.positionId = employeeData.position.id
          response.positionName = employeeData.position.name
        }
        
        console.log('处理后的员工信息:', {
          id: response.employeeId,
          name: response.employeeName,
          department: response.departmentName,
          position: response.positionName
        })
      }
      
      // 确保薪资发放日期正确处理
      if (response.status === 'paid' && !response.paymentDate && response.payment_date) {
        console.log('转换薪资发放日期:', response.payment_date)
        response.paymentDate = response.payment_date
      }
      
      console.log('设置当前记录, ID:', response.id)
      currentSalaryRecord.value = response
      return response
    } catch (err) {
      console.error('获取薪资记录详情失败:', err)
      error.value = '获取薪资记录详情失败'
      currentSalaryRecord.value = null
      throw err
    } finally {
      isLoading.value = false
    }
  }

  // 删除薪资记录
  async function deleteSalaryRecord(id: number) {
    isLoading.value = true
    error.value = null
    
    try {
      await del(`/api/v1/salaries/records/${id}`)
      
      // 更新本地状态
      const index = salaryRecords.value.findIndex(record => record.id === id)
      if (index !== -1) {
        salaryRecords.value.splice(index, 1)
        totalCount.value--
      }
      
      return true
    } catch (err) {
      console.error('删除薪资记录失败:', err)
      error.value = '删除薪资记录失败'
      throw err
    } finally {
      isLoading.value = false
    }
  }

  // 薪资发放
  async function paySalary(id: number) {
    isLoading.value = true
    error.value = null
    
    try {
      // 使用pay接口，需要包装id到请求体中
      const paymentDate = new Date().toISOString()
      const response = await post('/api/v1/salaries/pay', { 
        record_ids: [id],
        payment_date: paymentDate
      })
      
      // 更新本地状态
      const index = salaryRecords.value.findIndex(record => record.id === id)
      if (index !== -1) {
        salaryRecords.value[index].status = 'paid'
        salaryRecords.value[index].paymentDate = paymentDate
      }
      
      // 如果当前记录就是被发放的记录，也更新它
      if (currentSalaryRecord.value && currentSalaryRecord.value.id === id) {
        currentSalaryRecord.value.status = 'paid'
        currentSalaryRecord.value.paymentDate = paymentDate
      }
      
      return response
    } catch (err) {
      console.error('薪资发放失败:', err)
      error.value = '薪资发放失败'
      throw err
    } finally {
      isLoading.value = false
    }
  }

  // 批量薪资发放
  async function batchPaySalaries(recordIds: number[]) {
    isLoading.value = true
    error.value = null
    
    try {
      const response = await post('/api/v1/salaries/pay', { 
        record_ids: recordIds,
        payment_date: new Date().toISOString()
      })
      
      // 更新本地状态
      recordIds.forEach(id => {
        const index = salaryRecords.value.findIndex(record => record.id === id)
        if (index !== -1) {
          salaryRecords.value[index].status = 'paid'
          salaryRecords.value[index].paymentDate = new Date().toISOString()
        }
      })
      
      return response
    } catch (err) {
      console.error('批量薪资发放失败:', err)
      error.value = '批量薪资发放失败'
      throw err
    } finally {
      isLoading.value = false
    }
  }

  // 生成薪资记录
  async function generateSalaryRecords(year: number, month: number, department_id?: number) {
    isLoading.value = true
    error.value = null
    
    try {
      // 调用薪资核算接口
      const params = {
        year,
        month,
        department_id
      }
      
      const response = await post('/api/v1/salaries/generate', params)
      
      // 刷新列表
      await getSalaryRecordsForDisplay({ year, month, department_id })
      
      return response
    } catch (err) {
      console.error('薪资核算失败:', err)
      error.value = '薪资核算失败'
      throw err
    } finally {
      isLoading.value = false
    }
  }

  // 手动创建薪资记录
  async function createSalaryRecord(recordData: Partial<SalaryRecord>) {
    isLoading.value = true
    error.value = null
    
    try {
      const response = await post('/api/v1/salaries/records', recordData)
      
      // 更新本地状态
      salaryRecords.value.push(response)
      totalCount.value++
      
      return response
    } catch (err) {
      console.error('创建薪资记录失败:', err)
      error.value = '创建薪资记录失败'
      throw err
    } finally {
      isLoading.value = false
    }
  }

  // 更新薪资记录
  async function updateSalaryRecord(id: number, recordData: Partial<SalaryRecord>) {
    isLoading.value = true
    error.value = null
    
    try {
      const response = await put(`/api/v1/salaries/records/${id}`, recordData)
      
      // 更新本地状态
      const index = salaryRecords.value.findIndex(record => record.id === id)
      if (index !== -1) {
        salaryRecords.value[index] = { ...salaryRecords.value[index], ...response }
      }
      
      return response
    } catch (err) {
      console.error('更新薪资记录失败:', err)
      error.value = '更新薪资记录失败'
      throw err
    } finally {
      isLoading.value = false
    }
  }

  // 导出薪资报表
  async function exportSalaryRecords(params: any) {
    isLoading.value = true
    error.value = null
    
    try {
      const response = await get('/api/v1/salaries/export', { 
        params,
        responseType: 'blob'
      })
      
      return response
    } catch (err) {
      console.error('导出薪资报表失败:', err)
      error.value = '导出薪资报表失败'
      throw err
    } finally {
      isLoading.value = false
    }
  }

  // 获取薪资统计数据
  async function getSalarySummary(year: number, month?: number) {
    isLoading.value = true
    error.value = null
    
    try {
      const params = { year, month }
      const response = await get('/api/v1/salaries/summary', { params })
      return response
    } catch (err) {
      console.error('获取薪资统计数据失败:', err)
      error.value = '获取薪资统计数据失败'
      throw err
    } finally {
      isLoading.value = false
    }
  }

  return {
    salaryRecords,
    currentSalaryRecord,
    totalCount,
    isLoading,
    error,
    getSalaryRecordsForDisplay,
    getSalaryRecord,
    deleteSalaryRecord,
    paySalary,
    batchPaySalaries,
    generateSalaryRecords,
    createSalaryRecord,
    updateSalaryRecord,
    exportSalaryRecords,
    getSalarySummary
  }
}) 