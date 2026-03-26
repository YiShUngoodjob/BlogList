import { createApp } from 'vue'
import { createRouter, createWebHistory } from 'vue-router'
import ElementPlus from 'element-plus'
import 'element-plus/dist/index.css'
import * as ElementPlusIconsVue from '@element-plus/icons-vue'
import App from './App.vue'
import './style.css'

// 页面组件
import Login from './views/Login.vue'
import Register from './views/Register.vue'
import ProfileEdit from './views/ProfileEdit.vue'
import UserList from './views/UserList.vue'
import UserDetail from './views/UserDetail.vue'
import Chat from './views/Chat.vue'
import Admin from './views/Admin.vue'
import ResetPassword from './views/ResetPassword.vue'

// 创建路由
const routes = [
  { path: '/', name: 'UserList', component: UserList },
  { path: '/login', name: 'Login', component: Login },
  { path: '/register', name: 'Register', component: Register },
  { path: '/reset-password', name: 'ResetPassword', component: ResetPassword },
  { path: '/profile', name: 'ProfileEdit', component: ProfileEdit },
  { path: '/user/:id', name: 'UserDetail', component: UserDetail },
  { path: '/chat', name: 'Chat', component: Chat },
  { path: '/admin', name: 'Admin', component: Admin }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

const app = createApp(App)

// 注册所有 Element Plus 图标
for (const [key, component] of Object.entries(ElementPlusIconsVue)) {
  app.component(key, component)
}

app.use(router)
app.use(ElementPlus)
app.mount('#app')
