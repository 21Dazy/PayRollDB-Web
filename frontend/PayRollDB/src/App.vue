<script setup lang="ts">
import { RouterView } from 'vue-router'
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
  overflow-x: hidden;
  position: relative;
}

body {
  overflow-y: auto;
  -webkit-overflow-scrolling: touch;
  min-height: 100vh;
  /* 移动端100vh问题的修复 */
  min-height: -webkit-fill-available;
}

/* 修复Safari中的100vh问题 */
@supports (-webkit-touch-callout: none) {
  body {
    min-height: -webkit-fill-available;
  }
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
