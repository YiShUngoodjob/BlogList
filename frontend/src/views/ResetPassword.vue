<template>
  <div class="reset-password-page">
    <div class="reset-card glass-card">
      <div class="card-header">
        <el-button class="back-btn" text @click="goToLogin">
          <el-icon><ArrowLeft /></el-icon>
          返回登录
        </el-button>
        <h2>忘记密码</h2>
        <p class="subtitle">通过邮箱和邀请码重置密码</p>
      </div>

      <el-form
        ref="formRef"
        :model="form"
        :rules="rules"
        class="reset-form"
        label-position="top"
      >
        <el-form-item label="注册邮箱" prop="email">
          <el-input
            v-model="form.email"
            placeholder="请输入注册时使用的邮箱"
            :prefix-icon="Message"
          />
        </el-form-item>

        <el-form-item label="邀请码" prop="invite_code">
          <el-input
            v-model="form.invite_code"
            placeholder="请输入注册时使用的邀请码"
            :prefix-icon="Key"
          />
        </el-form-item>

        <el-form-item label="验证码" prop="code">
          <div class="code-row">
            <el-input
              v-model="form.code"
              placeholder="请输入6位验证码"
              :prefix-icon="CircleCheck"
              maxlength="6"
            />
            <el-button
              :disabled="countdown > 0"
              @click="sendCode"
              class="send-code-btn"
            >
              {{ countdown > 0 ? `${countdown}s` : '获取验证码' }}
            </el-button>
          </div>
        </el-form-item>

        <el-form-item label="新密码" prop="new_password">
          <el-input
            v-model="form.new_password"
            type="password"
            placeholder="6-20位，包含字母和数字"
            :prefix-icon="Lock"
            show-password
          />
        </el-form-item>

        <el-form-item label="确认新密码" prop="confirm_password">
          <el-input
            v-model="form.confirm_password"
            type="password"
            placeholder="请再次输入新密码"
            :prefix-icon="Lock"
            show-password
          />
        </el-form-item>

        <el-button
          type="primary"
          :loading="loading"
          class="submit-btn"
          @click="handleSubmit"
        >
          确认重置
        </el-button>
      </el-form>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { ArrowLeft, Message, Key, CircleCheck, Lock } from '@element-plus/icons-vue'
import { resetPasswordAPI } from '../api'

const router = useRouter()
const formRef = ref(null)
const loading = ref(false)
const countdown = ref(0)
let countdownTimer = null

const form = reactive({
  email: '',
  invite_code: '',
  code: '',
  new_password: '',
  confirm_password: ''
})

const validatePassword = (rule, value, callback) => {
  if (!value) {
    callback(new Error('请输入密码'))
  } else if (value.length < 6) {
    callback(new Error('密码至少6位'))
  } else if (!/^(?=.*[a-zA-Z])(?=.*\d)/.test(value)) {
    callback(new Error('密码必须包含字母和数字'))
  } else {
    callback()
  }
}

const validateConfirmPassword = (rule, value, callback) => {
  if (!value) {
    callback(new Error('请确认密码'))
  } else if (value !== form.new_password) {
    callback(new Error('两次输入的密码不一致'))
  } else {
    callback()
  }
}

const rules = {
  email: [
    { required: true, message: '请输入邮箱', trigger: 'blur' },
    { type: 'email', message: '请输入正确的邮箱格式', trigger: 'blur' }
  ],
  invite_code: [
    { required: true, message: '请输入邀请码', trigger: 'blur' }
  ],
  code: [
    { required: true, message: '请输入验证码', trigger: 'blur' },
    { len: 6, message: '验证码为6位', trigger: 'blur' }
  ],
  new_password: [
    { validator: validatePassword, trigger: 'blur' }
  ],
  confirm_password: [
    { validator: validateConfirmPassword, trigger: 'blur' }
  ]
}

const sendCode = async () => {
  if (!form.email) {
    ElMessage.warning('请先输入邮箱')
    return
  }
  if (!form.invite_code) {
    ElMessage.warning('请先输入邀请码')
    return
  }

  try {
    await resetPasswordAPI.sendCode({
      email: form.email,
      invite_code: form.invite_code
    })
    ElMessage.success('验证码已发送到您的邮箱')
    countdown.value = 60
    countdownTimer = setInterval(() => {
      countdown.value--
      if (countdown.value <= 0) {
        clearInterval(countdownTimer)
      }
    }, 1000)
  } catch (err) {
    ElMessage.error(err.response?.data?.message || '发送失败')
  }
}

const handleSubmit = async () => {
  if (!formRef.value) return

  await formRef.value.validate(async (valid) => {
    if (!valid) return

    loading.value = true
    try {
      await resetPasswordAPI.resetPassword({
        email: form.email,
        code: form.code,
        new_password: form.new_password,
        confirm_password: form.confirm_password
      })
      ElMessage.success('密码重置成功，请使用新密码登录')
      router.push('/login')
    } catch (err) {
      ElMessage.error(err.response?.data?.message || '重置失败')
    } finally {
      loading.value = false
    }
  })
}

const goToLogin = () => {
  router.push('/login')
}

onUnmounted(() => {
  if (countdownTimer) {
    clearInterval(countdownTimer)
  }
})
</script>

<style scoped>
.reset-password-page {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 20px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}

.reset-card {
  width: 100%;
  max-width: 420px;
  padding: 40px;
}

.card-header {
  text-align: center;
  margin-bottom: 30px;
}

.back-btn {
  position: absolute;
  left: 20px;
  top: 20px;
}

.card-header h2 {
  margin: 0 0 10px 0;
  font-size: 24px;
  color: var(--text-primary);
}

.subtitle {
  color: var(--text-secondary);
  font-size: 14px;
  margin: 0;
}

.reset-form {
  margin-top: 20px;
}

.code-row {
  display: flex;
  gap: 10px;
}

.code-row .el-input {
  flex: 1;
}

.send-code-btn {
  width: 120px;
  flex-shrink: 0;
}

.submit-btn {
  width: 100%;
  height: 44px;
  font-size: 16px;
  margin-top: 10px;
}

:deep(.el-form-item__label) {
  font-weight: 500;
}
</style>
