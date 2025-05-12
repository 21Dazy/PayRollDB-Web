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
        <el-menu-item v-for="menu in topMenus" :key="menu.key" :index="menu.key">
          <el-icon v-if="menu.icon">
            <component :is="menu.icon" />
          </el-icon>
          <template #title>{{ menu.title }}</template>
        </el-menu-item>
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
import { ref, computed } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import defaultAvatar from '@/assets/avatar.png'

// 顶部菜单
const topMenus = ref([
  { key: 'system', title: '系统管理', icon: 'Setting' },
  { key: 'employee', title: '员工管理', icon: 'User' },
  { key: 'role', title: '角色管理', icon: 'Lock' },
  { key: 'menu', title: '菜单管理', icon: 'Menu' },
  { key: 'salary', title: '薪资管理', icon: 'Money' },
  { key: 'attendance', title: '考勤管理', icon: 'Calendar' },
])

// 用户信息
const username = ref('管理员')
const userAvatar = ref(defaultAvatar)

// 路由
const router = useRouter()
const route = useRoute()

// 当前激活菜单
const activeMenu = computed(() => {
  return route.meta.activeMenu as string || route.path
})

// 处理菜单选择
const handleSelect = (key: string) => {
  console.log(key)
  // 这里可以添加路由跳转逻辑
}

// 处理用户中心点击
const handleUserCenter = () => {
  router.push('/user/profile')
}

// 处理退出登录
const handleLogout = () => {
  // 这里添加登出逻辑
  router.push('/login')
}
</script>

<style scoped lang="scss">
.app-header {
  display: flex;
  height: 60px;
  background-color: #1989fa;
  color: #fff;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);

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