import Mock from 'mockjs'

const baseUrl = import.meta.env.VITE_API_BASE_URL || '/api'

// 登录接口
Mock.mock(`${baseUrl}/auth/login`, 'post', (options) => {
  const { username, password } = JSON.parse(options.body)
  if (username && password) {
    return {
      code: 200,
      message: '登录成功',
      data: {
        token: 'mock-token-' + Date.now(),
        userInfo: {
          id: 1,
          username,
          name: username === 'admin' ? '管理员' : '张三',
          avatar: '',
          role: username === 'admin' ? 'admin' : 'employee'
        }
      }
    }
  } else {
    return {
      code: 400,
      message: '用户名或密码错误'
    }
  }
})

// 注册接口
Mock.mock(`${baseUrl}/auth/register`, 'post', () => {
  return {
    code: 200,
    message: '注册成功'
  }
})

// 获取用户信息
Mock.mock(`${baseUrl}/user/info`, 'get', () => {
  return {
    code: 200,
    message: 'success',
    data: {
      id: 1,
      employeeId: 'EMP001',
      name: '张三',
      avatar: '',
      roleName: '研发工程师',
      workYears: 3,
      attendanceRate: 98,
      rank: 'A',
      departmentName: '研发部',
      positionName: '工程师',
      baseSalary: 15000,
      hireDate: '2020-01-01',
      phone: '13800138000',
      email: 'zhangsan@example.com',
      address: '北京市朝阳区XXX路XXX号',
      status: 1,
      bankName: '中国银行',
      bankAccount: '6222021234567890123',
      bankBranch: '北京朝阳支行',
      bankAccountName: '张三'
    }
  }
})

// 获取员工列表
Mock.mock(new RegExp(`${baseUrl}/employee/list(\\?.*)?`), 'get', () => {
  const list = []
  for (let i = 0; i < 10; i++) {
    list.push(Mock.mock({
      id: '@id',
      employeeId: 'EMP@string("number", 3)',
      name: '@cname',
      departmentName: '@pick(["研发部", "市场部", "销售部", "财务部", "人事部"])',
      positionName: '@pick(["总监", "经理", "主管", "工程师", "专员"])',
      baseSalary: '@integer(8000, 30000)',
      hireDate: '@date("yyyy-MM-dd")',
      phone: '1@string("number", 10)',
      status: '@pick([0, 1])'
    }))
  }
  return {
    code: 200,
    message: 'success',
    data: {
      list,
      total: 100,
      page: 1,
      pageSize: 10
    }
  }
})

// 获取薪资列表
Mock.mock(new RegExp(`${baseUrl}/salary/list(\\?.*)?`), 'get', () => {
  const list = []
  for (let i = 0; i < 10; i++) {
    const baseSalary = Mock.Random.integer(8000, 20000)
    const bonus = Mock.Random.integer(1000, 5000)
    const deduction = Mock.Random.integer(0, 1000)
    const socialSecurity = Mock.Random.integer(1000, 3000)
    const netSalary = baseSalary + bonus - deduction - socialSecurity
    
    list.push(Mock.mock({
      id: '@id',
      employeeId: 'EMP@string("number", 3)',
      employeeName: '@cname',
      departmentName: '@pick(["研发部", "市场部", "销售部", "财务部", "人事部"])',
      year: '@integer(2020, 2023)',
      month: '@integer(1, 12)',
      baseSalary,
      bonus,
      deduction,
      socialSecurity,
      netSalary,
      status: '@pick(["pending", "paid"])',
      paymentDate: '@datetime("yyyy-MM-dd HH:mm:ss")'
    }))
  }
  return {
    code: 200,
    message: 'success',
    data: {
      list,
      total: 100,
      page: 1,
      pageSize: 10
    }
  }
})

// 获取考勤记录
Mock.mock(new RegExp(`${baseUrl}/attendance/list(\\?.*)?`), 'get', () => {
  const list = []
  for (let i = 0; i < 10; i++) {
    list.push(Mock.mock({
      id: '@id',
      employeeId: 'EMP@string("number", 3)',
      employeeName: '@cname',
      date: '@date("yyyy-MM-dd")',
      status: '@pick(["正常", "迟到", "早退", "缺勤", "病假", "事假"])',
      checkInTime: '@time("HH:mm:ss")',
      checkOutTime: '@time("HH:mm:ss")',
      overtimeHours: '@float(0, 5, 1, 1)',
      remarks: '@ctitle(5, 10)'
    }))
  }
  return {
    code: 200,
    message: 'success',
    data: {
      list,
      total: 100,
      page: 1,
      pageSize: 10
    }
  }
})

export default Mock 