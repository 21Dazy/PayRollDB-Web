<template>
  <div class="app-header">
    <div class="logo">
      <h1>薪资管理系统</h1>
    </div>
    <div class="menu">
      <el-menu 
        :default-active="activeMenu" 
        mode="horizontal" 
        :ellipsis="false"
        background-color="#1989fa"
        text-color="#ffffff"
        active-text-color="#ffffff"
        @select="handleSelect"
      >
        <el-sub-menu index="dashboard">
          <template #title>
            <el-icon><HomeFilled /></el-icon>
            <span>工作台</span>
          </template>
          <el-menu-item index="dashboard">首页</el-menu-item>
          <el-menu-item index="notice">公告</el-menu-item>
          <el-menu-item index="todo">待办事项</el-menu-item>
        </el-sub-menu>
        
        <el-sub-menu index="tools">
          <template #title>
            <el-icon><Tools /></el-icon>
            <span>快捷工具</span>
          </template>
          <el-menu-item index="calculator">薪资计算器</el-menu-item>
          <el-menu-item index="schedule">排班工具</el-menu-item>
          <el-menu-item index="export">导出报表</el-menu-item>
        </el-sub-menu>
        
        <el-sub-menu index="help">
          <template #title>
            <el-icon><QuestionFilled /></el-icon>
            <span>帮助中心</span>
          </template>
          <el-menu-item index="guide">使用指南</el-menu-item>
          <el-menu-item index="faq">常见问题</el-menu-item>
          <el-menu-item index="contact">联系我们</el-menu-item>
        </el-sub-menu>
      </el-menu>
    </div>
    <div class="user-info">
      <el-dropdown trigger="click">
        <div class="user-avatar">
          <el-avatar :size="32" :src="userAvatar"></el-avatar>
          <span class="username">{{ username }}</span>
        </div>
        <template #dropdown>
          <el-dropdown-menu>
            <el-dropdown-item @click="handleUserCenter">
              <el-icon><User /></el-icon>个人中心
            </el-dropdown-item>
            <el-dropdown-item @click="handleTheme">
              <el-icon><Brush /></el-icon>主题设置
            </el-dropdown-item>
            <el-dropdown-item @click="handleLogout">
              <el-icon><SwitchButton /></el-icon>退出登录
            </el-dropdown-item>
          </el-dropdown-menu>
        </template>
      </el-dropdown>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { ElMessageBox } from 'element-plus'
import defaultAvatar from '@/assets/avatar.png'
import { useAuthStore } from '@/stores/auth'

// 认证状态管理
const authStore = useAuthStore()

// 用户信息
const username = computed(() => {
  return authStore.user?.full_name || authStore.user?.username || '用户'
})
const userAvatar = ref(defaultAvatar)

// 路由
const router = useRouter()
const route = useRoute()

// 当前激活菜单
const activeMenu = computed(() => {
  return route.meta.activeMenu as string || 'dashboard'
})

// 获取用户信息
onMounted(async () => {
  if (authStore.isAuthenticated && !authStore.user) {
    try {
      await authStore.getCurrentUser()
    } catch (error) {
      console.error('获取用户信息失败', error)
    }
  }
})

// 处理菜单选择
const handleSelect = (key: string) => {
  console.log('选择菜单:', key)
  // 根据key处理不同的路由跳转或功能
  switch (key) {
    case 'dashboard':
      router.push('/dashboard')
      break
    case 'notice':
      router.push('/notice')
      break
    case 'todo':
      router.push('/todo')
      break
    case 'calculator':
      // 可以打开一个计算器弹窗等
      break
    case 'schedule':
      router.push('/tools/schedule')
      break
    case 'export':
      // 处理导出功能
      break
    case 'guide':
      router.push('/help/guide')
      break
    case 'faq':
      router.push('/help/faq')
      break
    case 'contact':
      router.push('/help/contact')
      break
    default:
      break
  }
}

// 处理用户中心点击
const handleUserCenter = () => {
  router.push('/user/profile')
}

// 处理主题设置
const handleTheme = () => {
  // 打开主题设置面板
}

// 处理退出登录
const handleLogout = () => {
  ElMessageBox.confirm('确定要退出登录吗？', '提示', {
    confirmButtonText: '确定',
    cancelButtonText: '取消',
    type: 'warning'
  }).then(() => {
    authStore.logout()
    router.push('/login')
  }).catch(() => {
    // 取消登出操作
  })
}
</script>

<style scoped lang="scss">
.app-header {
  display: flex;
  height: 60px;
  background-color: #1989fa;
  color: #fff;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  z-index: 1001;
  
  .logo {
    padding: 0 16px;
    display: flex;
    align-items: center;
    h1 {
      font-size: 20px;
      margin: 0;
      font-weight: bold;
    }
  }

  .menu {
    flex: 1;
    display: flex;
    
    :deep(.el-menu) {
      border-bottom: none;
    }
    
    :deep(.el-menu-item) {
      &.is-active {
        background-color: #0c70d2 !important;
      }
      &:hover {
        background-color: #0c70d2 !important;
      }
    }
    
    :deep(.el-sub-menu__title) {
      &:hover {
        background-color: #0c70d2 !important;
      }
    }
    
    :deep(.el-sub-menu.is-active .el-sub-menu__title) {
      border-bottom: 2px solid #fff;
    }
  }

  .user-info {
    display: flex;
    align-items: center;
    padding: 0 20px;
    
    .user-avatar {
      display: flex;
      align-items: center;
      cursor: pointer;
      
      .username {
        margin-left: 8px;
        font-size: 14px;
      }
    }
  }
}
</style> 