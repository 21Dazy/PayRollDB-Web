<template>
  <div class="app-sidebar" :class="{ 'collapsed': isCollapse }">
    <el-menu
      :default-active="activeMenu"
      :collapse="isCollapse"
      :collapse-transition="false"
      class="sidebar-menu"
      unique-opened
      background-color="#001529"
      text-color="#fff"
      active-text-color="#409EFF"
      @select="handleSelect"
    >
      <el-menu-item index="dashboard">
        <el-icon><DataBoard /></el-icon>
        <template #title>首页</template>
      </el-menu-item>
      
      <el-sub-menu v-for="menu in sideMenus" :key="menu.key" :index="menu.key">
        <template #title>
          <el-icon v-if="menu.icon"><component :is="menu.icon" /></el-icon>
          <span>{{ menu.title }}</span>
        </template>
        <el-menu-item 
          v-for="subMenu in menu.children" 
          :key="subMenu.key" 
          :index="subMenu.key"
        >
          {{ subMenu.title }}
        </el-menu-item>
      </el-sub-menu>
    </el-menu>
    
    <div class="collapse-btn" @click="toggleCollapse">
      <el-icon :size="20" v-if="isCollapse"><Expand /></el-icon>
      <el-icon :size="20" v-else><Fold /></el-icon>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { 
  Calendar, 
  Money, 
  User, 
  Setting, 
  PieChart, 
  Expand, 
  Fold, 
  DataBoard,
  OfficeBuilding,
  Suitcase
} from '@element-plus/icons-vue'

// 侧边栏菜单
const sideMenus = ref([
  {
    key: 'salary',
    title: '薪资管理',
    icon: 'Money',
    children: [
      { key: 'salary-list', title: '薪资列表' },
      { key: 'salary-pay', title: '薪资发放' },
      { key: 'salary-items', title: '薪资项目' },
      { key: 'salary-config', title: '薪资配置' },
      { key: 'salary-statistics', title: '薪资统计' }
    ]
  },
  {
    key: 'employee',
    title: '员工管理',
    icon: 'User',
    children: [
      { key: 'employee-list', title: '员工列表' },
      { key: 'employee-add', title: '添加员工' }
    ]
  },
  {
    key: 'department',
    title: '部门管理',
    icon: 'OfficeBuilding',
    children: [
      { key: 'department-list', title: '部门列表' },
      { key: 'department-add', title: '添加部门' }
    ]
  },
  {
    key: 'position',
    title: '职位管理',
    icon: 'Suitcase',
    children: [
      { key: 'position-list', title: '职位列表' },
      { key: 'position-add', title: '添加职位' }
    ]
  },
  {
    key: 'attendance',
    title: '考勤管理',
    icon: 'Calendar',
    children: [
      { key: 'attendance-record', title: '考勤记录' },
      { key: 'attendance-statistics', title: '考勤统计' },
      { key: 'attendance-config', title: '考勤设置' }
    ]
  },
  {
    key: 'report',
    title: '报表统计',
    icon: 'PieChart',
    children: [
      { key: 'report-salary', title: '薪资报表' },
      { key: 'report-attendance', title: '考勤报表' },
      { key: 'report-department', title: '部门报表' }
    ]
  },
  {
    key: 'system',
    title: '系统设置',
    icon: 'Setting',
    children: [
      { key: 'system-user', title: '用户管理' },
      { key: 'system-role', title: '角色管理' },
      { key: 'system-menu', title: '菜单管理' },
      { key: 'system-param', title: '参数设置' },
      { key: 'system-log', title: '操作日志' }
    ]
  }
])

// 路由
const router = useRouter()
const route = useRoute()

// 当前激活菜单
const activeMenu = computed(() => {
  const currentPath = route.path
  
  if (currentPath === '/dashboard') {
    return 'dashboard'
  }
  
  // 从路径提取菜单key
  const pathSegments = currentPath.split('/').filter(segment => segment !== '')
  
  if (pathSegments.length >= 2) {
    const mainRoute = pathSegments[0]
    const subRoute = pathSegments[1]
    
    // 如果是查看、编辑等详情页面，只返回主路由
    if (pathSegments.length > 2 && ['view', 'edit', 'detail'].includes(subRoute)) {
      return `${mainRoute}-list`
    }
    
    return `${mainRoute}-${subRoute}`
  }
  
  return 'dashboard'
})

// 是否折叠
const isCollapse = ref(false)

// 定义emit
const emit = defineEmits(['update:collapsed'])

// 切换折叠状态并触发事件
const toggleCollapse = () => {
  isCollapse.value = !isCollapse.value
  emit('update:collapsed', isCollapse.value)
}

// 处理菜单选择
const handleSelect = (key: string) => {
  if (key === 'dashboard') {
    router.push('/dashboard')
    return
  }
  
  // 将菜单键转换为路由路径
  const menuParts = key.split('-')
  
  if (menuParts.length === 1) {
    // 如果是一级菜单，添加默认子路由
    router.push(`/${menuParts[0]}/list`)
  } else {
    // 如果是二级菜单，构建路由
    const mainRoute = menuParts[0]
    const subRoute = menuParts[1]
    router.push(`/${mainRoute}/${subRoute}`)
  }
}
</script>

<style scoped lang="scss">
.app-sidebar {
  height: 100%;
  position: relative;
  background-color: #001529;
  transition: width 0.3s;
  width: 220px;
  
  &.collapsed {
    width: 64px;
    
    .collapse-btn {
      width: 64px;
    }
  }
  
  .sidebar-menu {
    height: calc(100% - 40px); /* 减去底部折叠按钮的高度 */
    border-right: none;
    overflow-y: auto;
    overflow-x: hidden;
  }
  
  .collapse-btn {
    position: absolute;
    bottom: 0;
    left: 0;
    width: 100%;
    text-align: center;
    color: #fff;
    background-color: #0c2135;
    cursor: pointer;
    height: 40px;
    display: flex;
    align-items: center;
    justify-content: center;
    z-index: 100;
    border-top: 1px solid #132436;
    box-shadow: 0 -2px 5px rgba(0, 0, 0, 0.15);
    
    &:hover {
      background-color: #163a5a;
    }
  }
  
  :deep(.el-menu) {
    border-right: none;
  }
  
  :deep(.el-menu--collapse) {
    width: 64px;
  }
  
  :deep(.el-sub-menu__title) {
    &:hover {
      background-color: #0c2135 !important;
    }
  }
  
  :deep(.el-menu-item) {
    &:hover {
      background-color: #0c2135 !important;
    }
    
    &.is-active {
      background-color: #0c2135 !important;
    }
  }
}
</style> 