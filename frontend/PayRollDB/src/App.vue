<script setup lang="ts">
import { RouterView } from 'vue-router'
import { onMounted, watch } from 'vue'
import { useRouter } from 'vue-router'
import { useSystemStore } from '@/stores/system'
import { useAuthStore } from '@/stores/auth'
import { ElMessage } from 'element-plus'

const router = useRouter()
const systemStore = useSystemStore()
const authStore = useAuthStore()

// 检查系统健康状态
async function checkSystemHealth() {
  try {
    const result = await systemStore.checkSystemHealth()
    if (!result.isOnline) {
      console.error('系统不可用:', result.error)
      // 如果在非登录页面，可以提示用户
      if (router.currentRoute.value.path !== '/login') {
        ElMessage.warning('系统连接异常，请稍后再试')
      }
    }
  } catch (error) {
    console.error('健康检查异常:', error)
  }
}

// 初始化应用
onMounted(async () => {
  // 检查系统健康状态
  await checkSystemHealth()
  
  // 如果有token但没有用户信息，尝试获取
  if (authStore.token && !authStore.user) {
    try {
      await authStore.getCurrentUser()
    } catch (error) {
      console.error('获取用户信息失败:', error)
      // 如果获取用户信息失败，可能是token已过期
      if (router.currentRoute.value.path !== '/login') {
        // 尝试自动重新登录
        const success = await authStore.autoRelogin()
        if (!success) {
          // 如果重新登录失败，跳转到登录页
          router.push('/login')
        }
      }
    }
  }
  
  // 设置定期健康检查
  setInterval(checkSystemHealth, 5 * 60 * 1000) // 每5分钟检查一次
})

// 监听路由变化，检查认证状态
watch(() => router.currentRoute.value.path, (path) => {
  // 如果路径不是登录页，并且没有token，跳转到登录页
  if (path !== '/login' && !authStore.token) {
    router.push('/login')
  }
})
</script>

<template>
  <router-view />
</template>

<style>
* {
  box-sizing: border-box;
  margin: 0;
  padding: 0;
}

html, body {
  height: 100%;
  width: 100%;
  font-family: 'PingFang SC', 'Microsoft YaHei', sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  color: #333;
  overflow: hidden;
}

#app {
  height: 100vh;
  width: 100vw;
  overflow: hidden;
}

/* 滚动条样式 */
::-webkit-scrollbar {
  width: 6px;
  height: 6px;
}

::-webkit-scrollbar-track {
  background: #f1f1f1;
  border-radius: 4px;
}

::-webkit-scrollbar-thumb {
  background: #ccc;
  border-radius: 4px;
}

::-webkit-scrollbar-thumb:hover {
  background: #999;
}

/* 响应式设置 */
@media screen and (max-width: 768px) {
  html {
    font-size: 14px;
  }
}

@media screen and (max-width: 480px) {
  html {
    font-size: 12px;
  }
  
  ::-webkit-scrollbar {
    width: 4px;
    height: 4px;
  }
}
</style>
