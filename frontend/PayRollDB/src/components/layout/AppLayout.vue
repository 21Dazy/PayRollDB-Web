<template>
  <div class="app-layout">
    <app-header class="app-header" />
    <div class="main-container">
      <app-sidebar class="app-sidebar" />
      <div class="main-content">
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
import { ref, watch } from 'vue'
import { useRoute } from 'vue-router'
import AppHeader from './AppHeader.vue'
import AppSidebar from './AppSidebar.vue'

// 路由
const route = useRoute()

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
  const newBreadcrumb: BreadcrumbItem[] = [
    { title: '首页', path: '/dashboard' }
  ]
  
  if (route.meta.title) {
    newBreadcrumb.push({
      title: route.meta.title as string,
      path: route.path
    })
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
    
    .app-sidebar {
      width: 220px;
      height: 100%;
      overflow-y: auto;
      overflow-x: hidden;
      transition: width 0.3s;
      
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