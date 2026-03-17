<script setup>
import { ref, onMounted, watch } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { ElMessage } from 'element-plus'

const router = useRouter()
const route = useRoute()
const isLoggedIn = ref(false)
const currentUser = ref(null)

// 检查登录状态
const checkAuth = () => {
  const token = localStorage.getItem('token')
  const user = localStorage.getItem('user')
  if (token && user) {
    isLoggedIn.value = true
    currentUser.value = JSON.parse(user)
  } else {
    isLoggedIn.value = false
    currentUser.value = null
  }
}

onMounted(() => {
  checkAuth()
})

watch(() => route.path, () => {
  checkAuth()
})

const handleLogout = () => {
  localStorage.removeItem('token')
  localStorage.removeItem('user')
  isLoggedIn.value = false
  currentUser.value = null
  ElMessage.success('已退出登录')
  router.push('/')
}

const goToProfile = () => {
  router.push('/profile')
}

const goToLogin = () => {
  router.push('/login')
}

const goToRegister = () => {
  router.push('/register')
}

const goHome = () => {
  router.push('/')
}
</script>

<template>
  <div id="app">
    <!-- 导航栏 -->
    <nav class="navbar" v-if="route.path !== '/login' && route.path !== '/register'">
      <div class="navbar-brand" @click="goHome" style="cursor: pointer;">
        个人博客
      </div>
      <div class="navbar-actions">
        <template v-if="isLoggedIn">
          <el-button @click="goToProfile" type="primary">
            <el-icon><User /></el-icon>
            编辑资料
          </el-button>
          <el-button @click="handleLogout">
            <el-icon><SwitchButton /></el-icon>
            退出
          </el-button>
        </template>
        <template v-else>
          <el-button @click="goToLogin">登录</el-button>
          <el-button type="primary" @click="goToRegister">注册</el-button>
        </template>
      </div>
    </nav>

    <!-- 路由内容 -->
    <router-view v-slot="{ Component }">
      <transition name="fade" mode="out-in">
        <component :is="Component" />
      </transition>
    </router-view>
  </div>
</template>

<style scoped>
.navbar {
  padding: 16px 24px;
  background: var(--card-bg);
  backdrop-filter: blur(var(--blur-amount));
  -webkit-backdrop-filter: blur(var(--blur-amount));
  border-bottom: 1px solid var(--border-color);
  display: flex;
  justify-content: space-between;
  align-items: center;
  position: sticky;
  top: 0;
  z-index: 100;
}

.navbar-brand {
  font-size: 20px;
  font-weight: 600;
  color: var(--text-primary);
}

.navbar-actions {
  display: flex;
  gap: 12px;
}
</style>
