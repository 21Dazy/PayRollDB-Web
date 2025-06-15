import './assets/main.css'
import './assets/element-fix.css'

import { createApp } from 'vue'
import { createPinia } from 'pinia'
import ElementPlus from 'element-plus'
import 'element-plus/dist/index.css'
import * as ElementPlusIconsVue from '@element-plus/icons-vue'
import zhCn from 'element-plus/es/locale/lang/zh-cn'

// 导入Mock数据，仅在开发环境且VITE_MOCK_ENABLED为true时使用
if (import.meta.env.MODE === 'development' && import.meta.env.VITE_MOCK_ENABLED === 'true') {
  console.log('Mock数据已启用')
  import('./utils/mock')
} else {
  console.log('使用真实API')
}

import App from './App.vue'
import router from './router'

const app = createApp(App)

// 注册所有图标
for (const [key, component] of Object.entries(ElementPlusIconsVue)) {
  app.component(key, component)
}

app.use(createPinia())
app.use(router)
app.use(ElementPlus, {
  locale: zhCn,
})

app.mount('#app')
