<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { authAPI } from '../api'

const router = useRouter()
const loading = ref(false)
const form = ref({
  username: '',
  password: ''
})

const handleLogin = async () => {
  if (!form.value.username || !form.value.password) {
    ElMessage.warning('请填写用户名和密码')
    return
  }

  loading.value = true
  try {
    const { data } = await authAPI.login(form.value)
    localStorage.setItem('token', data.token)
    localStorage.setItem('user', JSON.stringify(data.user))
    ElMessage.success('登录成功')
    router.push('/')
  } catch (error) {
    ElMessage.error(error.response?.data?.message || '登录失败')
  } finally {
    loading.value = false
  }
}

const goToRegister = () => {
  router.push('/register')
}

const goToResetPassword = () => {
  router.push('/reset-password')
}
</script>

<template>
  <div class="auth-container">
    <div class="auth-card glass-card">
      <h1 class="auth-title">登录</h1>
      <el-form :model="form" class="auth-form">
        <el-form-item>
          <el-input
            v-model="form.username"
            placeholder="用户名"
            size="large"
            :prefix-icon="User"
          />
        </el-form-item>
        <el-form-item>
          <el-input
            v-model="form.password"
            type="password"
            placeholder="密码"
            size="large"
            :prefix-icon="Lock"
            @keyup.enter="handleLogin"
          />
        </el-form-item>
        <el-form-item>
          <el-button
            type="primary"
            size="large"
            :loading="loading"
            @click="handleLogin"
            class="auth-button"
          >
            登录
          </el-button>
        </el-form-item>
      </el-form>
      <div class="auth-footer">
        <span class="forgot-password" @click="goToResetPassword">忘记密码？</span>
        <div class="register-link">
          还没有账号？<span @click="goToRegister">立即注册</span>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { User, Lock } from '@element-plus/icons-vue'
export default {
  components: { User, Lock }
}
</script>

<style scoped>
.auth-container {
  min-height: calc(100vh - 65px);
  display: flex;
  justify-content: center;
  align-items: center;
  padding: 20px;
}

.auth-card {
  width: 100%;
  max-width: 400px;
  padding: 40px;
}

.auth-title {
  text-align: center;
  margin-bottom: 30px;
  font-size: 28px;
  color: var(--text-primary);
}

.auth-form {
  margin-top: 20px;
}

.auth-button {
  width: 100%;
  margin-top: 10px;
}

.auth-footer {
  text-align: center;
  margin-top: 20px;
  color: var(--text-secondary);
}

.forgot-password {
  color: #999;
  cursor: pointer;
  font-size: 14px;
}

.forgot-password:hover {
  color: #667eea;
}

.register-link {
  margin-top: 10px;
}

.auth-footer span {
  color: #667eea;
  cursor: pointer;
  font-weight: 500;
}

.auth-footer span:hover {
  text-decoration: underline;
}
</style>
