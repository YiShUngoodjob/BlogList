<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { authAPI } from '../api'

const router = useRouter()
const loading = ref(false)
const sendingCode = ref(false)

const form = ref({
  email: '',
  code: '',
  inviteCode: '',
  password: '',
  name: ''
})

const countdown = ref(0)
let countdownTimer = null

// 发送验证码
const sendCode = async () => {
  if (!form.value.email) {
    ElMessage.warning('请先填写邮箱')
    return
  }

  // 验证邮箱格式
  const emailRegex = /^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$/
  if (!emailRegex.test(form.value.email)) {
    ElMessage.warning('请填写正确的邮箱格式')
    return
  }

  sendingCode.value = true
  try {
    await authAPI.sendCode({ email: form.value.email })
    ElMessage.success('验证码已发送到您的邮箱')

    // 开始倒计时
    countdown.value = 60
    countdownTimer = setInterval(() => {
      countdown.value--
      if (countdown.value <= 0) {
        clearInterval(countdownTimer)
      }
    }, 1000)
  } catch (error) {
    ElMessage.error(error.response?.data?.message || '发送失败，请稍后重试')
  } finally {
    sendingCode.value = false
  }
}

const handleRegister = async () => {
  if (!form.value.email || !form.value.code || !form.value.inviteCode || !form.value.password || !form.value.name) {
    ElMessage.warning('请填写所有必填项')
    return
  }

  if (form.value.name.length > 20) {
    ElMessage.warning('姓名不能超过20个字符')
    return
  }

  loading.value = true
  try {
    const { data } = await authAPI.register({
      email: form.value.email,
      code: form.value.code,
      inviteCode: form.value.inviteCode,
      password: form.value.password,
      name: form.value.name
    })
    localStorage.setItem('token', data.token)
    localStorage.setItem('user', JSON.stringify(data.user))
    ElMessage.success('注册成功')
    router.push('/profile')
  } catch (error) {
    ElMessage.error(error.response?.data?.message || '注册失败')
  } finally {
    loading.value = false
  }
}

const goToLogin = () => {
  router.push('/login')
}
</script>

<template>
  <div class="auth-container">
    <div class="auth-card glass-card">
      <h1 class="auth-title">注册</h1>
      <p class="auth-subtitle">填写信息完成注册</p>

      <el-form :model="form" class="auth-form">
        <el-form-item>
          <el-input
            v-model="form.name"
            placeholder="姓名（必填）"
            size="large"
            maxlength="20"
          />
        </el-form-item>

        <el-form-item>
          <el-input
            v-model="form.email"
            placeholder="邮箱（必填）"
            size="large"
          >
            <template #append>
              <el-button
                @click="sendCode"
                :disabled="countdown > 0 || sendingCode"
              >
                {{ countdown > 0 ? `${countdown}s` : '获取验证码' }}
              </el-button>
            </template>
          </el-input>
        </el-form-item>

        <el-form-item>
          <el-input
            v-model="form.code"
            placeholder="验证码（必填）"
            size="large"
          />
        </el-form-item>

        <el-form-item>
          <el-input
            v-model="form.inviteCode"
            placeholder="邀请码（必填）"
            size="large"
          />
        </el-form-item>

        <el-form-item>
          <el-input
            v-model="form.password"
            type="password"
            placeholder="密码（必填）"
            size="large"
            @keyup.enter="handleRegister"
          />
        </el-form-item>

        <el-form-item>
          <el-button
            type="primary"
            size="large"
            :loading="loading"
            @click="handleRegister"
            class="auth-button"
          >
            注册
          </el-button>
        </el-form-item>
      </el-form>

      <div class="auth-footer">
        已有账号？<span @click="goToLogin">立即登录</span>
      </div>
    </div>
  </div>
</template>

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
  max-width: 420px;
  padding: 40px;
}

.auth-title {
  text-align: center;
  margin-bottom: 8px;
  font-size: 28px;
  color: var(--text-primary);
}

.auth-subtitle {
  text-align: center;
  color: var(--text-secondary);
  margin-bottom: 24px;
  font-size: 14px;
}

.auth-form {
  margin-top: 10px;
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

.auth-footer span {
  color: #667eea;
  cursor: pointer;
  font-weight: 500;
}

.auth-footer span:hover {
  text-decoration: underline;
}
</style>
