<template>
  <div class="not-found">
    <div class="not-found-content">
      <h1>404</h1>
      <h2>页面不存在</h2>
      <p>您访问的页面不存在或已被删除</p>
      <el-button type="primary" @click="backToHome">返回首页</el-button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { useRouter } from 'vue-router'

const router = useRouter()

const backToHome = () => {
  router.push('/')
}
</script>

<style scoped lang="scss">
.not-found {
  height: 100vh;
  display: flex;
  justify-content: center;
  align-items: center;
  background-color: #f5f5f5;

  .not-found-content {
    text-align: center;
    
    h1 {
      font-size: 120px;
      font-weight: bold;
      color: #409eff;
      margin: 0;
      line-height: 1.2;
    }
    
    h2 {
      font-size: 30px;
      color: #303133;
      margin: 0 0 20px 0;
    }
    
    p {
      font-size: 16px;
      color: #909399;
      margin-bottom: 30px;
    }
  }
}
</style> 