<template>
  <div class="app-layout">
    <app-header class="app-header" />
    <div class="main-container">
      <app-sidebar class="app-sidebar" :class="{ 'collapsed': sidebarCollapsed }" @update:collapsed="handleSidebarCollapse" />
      <div class="main-content" :style="contentStyle">
        <div class="breadcrumb-container">
          <el-breadcrumb separator="/">
            <el-breadcrumb-item v-for="(item, index) in breadcrumbList" :key="index" :to="item.path">
              {{ item.title }}
            </el-breadcrumb-item>
          </el-breadcrumb>
        </div>
        <div class="page-container">
          <router-view v-slot="{ Component }">
            <transition name="fade" mode="out-in">
              <keep-alive>
                <component :is="Component" />
              </keep-alive>
            </transition>
          </router-view>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, watch, computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import AppHeader from './AppHeader.vue'
import AppSidebar from './AppSidebar.vue'

// 路由
const route = useRoute()
const router = useRouter()

// 侧边栏折叠状态
const sidebarCollapsed = ref(false)

// 处理侧边栏折叠
const handleSidebarCollapse = (collapsed: boolean) => {
  sidebarCollapsed.value = collapsed
}

// 计算主内容区样式
const contentStyle = computed(() => {
  return {
    marginLeft: sidebarCollapsed.value ? '64px' : '220px',
    transition: 'margin-left 0.3s'
  }
})

// 面包屑
interface BreadcrumbItem {
  title: string;
  path: string;
}

const breadcrumbList = ref<BreadcrumbItem[]>([
  { title: '首页', path: '/dashboard' }
])

// 更新面包屑 - 提前声明
const updateBreadcrumb = () => {
  // 获取当前路由信息
  const currentPath = route.path
  const pathSegments = currentPath.split('/').filter(Boolean)
  
  // 重置面包屑
  const newBreadcrumb: BreadcrumbItem[] = []
  
  // 如果当前在首页，只显示首页
  if (currentPath === '/dashboard' || currentPath === '/') {
    newBreadcrumb.push({ title: '首页', path: '/dashboard' })
  } else {
    // 解析当前路径
    let basePath = ''
    pathSegments.forEach((segment, index) => {
      basePath += '/' + segment
      
      // 查找匹配的路由以获取标题
      const matchedRoute = router.getRoutes().find(route => route.path === basePath)
      
      if (matchedRoute && matchedRoute.meta.title) {
        newBreadcrumb.push({
          title: matchedRoute.meta.title as string,
          path: basePath
        })
      } else if (index === 0) {
        // 如果是第一级但没有找到匹配的路由，可能是主模块
        switch (segment) {
          case 'salary':
            newBreadcrumb.push({ title: '薪资管理', path: '/salary' })
            break
          case 'employee':
            newBreadcrumb.push({ title: '员工管理', path: '/employee' })
            break
          case 'attendance':
            newBreadcrumb.push({ title: '考勤管理', path: '/attendance' })
            break
          case 'system':
            newBreadcrumb.push({ title: '系统设置', path: '/system' })
            break
          case 'report':
            newBreadcrumb.push({ title: '报表统计', path: '/report' })
            break
          case 'tools':
            newBreadcrumb.push({ title: '快捷工具', path: '/tools' })
            break
          case 'help':
            newBreadcrumb.push({ title: '帮助中心', path: '/help' })
            break
          case 'user':
            newBreadcrumb.push({ title: '用户中心', path: '/user' })
            break
          default:
            newBreadcrumb.push({ title: segment, path: basePath })
        }
      }
    })
    
    // 如果没有任何面包屑项，则至少显示当前页面标题
    if (newBreadcrumb.length === 0 && route.meta.title) {
      newBreadcrumb.push({
        title: route.meta.title as string,
        path: route.path
      })
    }
  }
  
  breadcrumbList.value = newBreadcrumb
}

// 监听路由变化，更新面包屑
watch(() => route.path, () => {
  updateBreadcrumb()
}, { immediate: true })
</script>

<style scoped lang="scss">
.app-layout {
  height: 100vh;
  display: flex;
  flex-direction: column;
  
  .app-header {
    height: 60px;
    width: 100%;
  }
  
  .main-container {
    flex: 1;
    display: flex;
    overflow: hidden;
    position: relative;
    margin-top: 60px; /* 添加顶部间距，与header高度一致 */
    
    .app-sidebar {
      position: fixed;
      top: 60px;
      left: 0;
      bottom: 0;
      z-index: 999;
      overflow-y: hidden; /* 避免滚动条问题 */
      
      &.collapsed {
        width: 64px;
      }
    }
    
    .main-content {
      flex: 1;
      display: flex;
      flex-direction: column;
      overflow: hidden;
      background-color: #f0f2f5;
      min-height: calc(100vh - 60px);
      
      .breadcrumb-container {
        padding: 16px 24px;
        background-color: #fff;
        box-shadow: 0 1px 4px rgba(0, 21, 41, 0.08);
      }
      
      .page-container {
        flex: 1;
        padding: 24px;
        overflow: auto;
      }
    }
  }
}

// 过渡动画
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.3s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}
</style> 