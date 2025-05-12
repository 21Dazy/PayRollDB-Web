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
              <component :is="Component" />
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

// 监听路由变化，更新面包屑
watch(() => route.path, () => {
  updateBreadcrumb()
}, { immediate: true })

// 更新面包屑
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
</script>

<style scoped lang="scss">
.app-layout {
  display: flex;
  flex-direction: column;
  height: 100vh;
  width: 100vw;
  overflow: hidden;
  
  .app-header {
    position: fixed;
    top: 0;
    left: 0;
    right: 0;
    z-index: 1001;
  }
  
  .main-container {
    display: flex;
    flex: 1;
    margin-top: 60px; /* 与header高度一致 */
    height: calc(100vh - 60px);
    overflow: hidden;
    
    .app-sidebar {
      position: fixed;
      left: 0;
      top: 60px; /* 与header高度一致 */
      bottom: 0;
      width: 220px;
      z-index: 1000;
      overflow-y: auto;
      transition: width 0.3s;
    }
    
    .main-content {
      flex: 1;
      margin-left: 220px; /* 与sidebar宽度一致 */
      overflow: auto;
      background-color: #f5f7fa;
      height: 100%;
      
      .breadcrumb-container {
        padding: 16px 20px;
        background-color: #fff;
        box-shadow: 0 1px 4px rgba(0, 21, 41, 0.08);
      }
      
      .page-container {
        padding: 20px;
        min-height: calc(100% - 56px); /* 减去breadcrumb的高度 */
      }
    }
  }
}

// 页面过渡动画
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.2s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}

@media screen and (max-width: 992px) {
  .app-layout {
    .main-container {
      .app-sidebar {
        width: 64px;
      }
      
      .main-content {
        margin-left: 64px;
      }
    }
  }
}

@media screen and (max-width: 768px) {
  .app-layout {
    .main-container {
      .main-content {
        .breadcrumb-container {
          padding: 10px 15px;
        }
        
        .page-container {
          padding: 15px 10px;
        }
      }
    }
  }
}
</style> 