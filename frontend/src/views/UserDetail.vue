<script setup>
import { ref, onMounted, computed } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { ElMessage } from 'element-plus'
import { userAPI, authAPI } from '../api'

const router = useRouter()
const route = useRoute()
const userId = route.params.id

const user = ref(null)
const loading = ref(true)
const isOwner = ref(false)

// 检查是否是自己的主页
const checkOwner = async () => {
  const token = localStorage.getItem('token')
  if (!token) {
    isOwner.value = false
    return
  }

  try {
    const { data } = await authAPI.getCurrentUser()
    isOwner.value = data.id === userId
  } catch (error) {
    isOwner.value = false
  }
}

onMounted(async () => {
  await loadUser()
  await checkOwner()
})

const loadUser = async () => {
  loading.value = true
  try {
    const { data } = await userAPI.getUser(userId)
    user.value = data
  } catch (error) {
    ElMessage.error('用户不存在')
    router.push('/')
  } finally {
    loading.value = false
  }
}

const goBack = () => {
  router.push('/')
}

const goToEdit = () => {
  router.push('/profile')
}

// 获取头像URL
const getAvatarUrl = computed(() => {
  if (user.value?.avatar_url) {
    return 'http://localhost:5000' + user.value.avatar_url
  }
  return null
})

// 获取名字首字
const getInitial = computed(() => {
  if (user.value?.name) {
    return user.value.name.charAt(0)
  }
  return '?'
})

// 折叠工作经历
const toggleExperience = (index) => {
  const item = document.querySelectorAll('.exp-item')[index]
  item.classList.toggle('expanded')
}
</script>

<template>
  <div class="user-detail-container">
    <div class="container" v-loading="loading">
      <!-- 返回按钮 -->
      <div class="back-button" @click="goBack">
        <el-icon><ArrowLeft /></el-icon>
        <span>返回列表</span>
      </div>

      <template v-if="user">
        <!-- 顶部信息 -->
        <div class="user-header glass-card">
          <div class="header-avatar">
            <img v-if="getAvatarUrl" :src="getAvatarUrl" class="avatar avatar-xl" />
            <div v-else class="avatar-placeholder avatar-xl">
              {{ getInitial }}
            </div>
          </div>
          <div class="header-info">
            <h1 class="user-name">{{ user.name }}</h1>
            <p class="user-school" v-if="user.school">
              <el-icon><School /></el-icon>
              {{ user.school }}
            </p>
            <p class="user-job" v-if="user.job">
              <el-icon><Briefcase /></el-icon>
              {{ user.job }}
            </p>
          </div>
          <div class="header-actions" v-if="isOwner">
            <el-button type="primary" @click="goToEdit">
              <el-icon><Edit /></el-icon>
              编辑资料
            </el-button>
          </div>
        </div>

        <!-- 个人简介 -->
        <div class="glass-card bio-card" v-if="user.bio">
          <h3 class="card-title">个人简介</h3>
          <p class="bio-text">{{ user.bio }}</p>
        </div>

        <!-- 技能 -->
        <div class="glass-card skills-card" v-if="user.skills && user.skills.length > 0">
          <h3 class="card-title">
            <el-icon><Star /></el-icon>
            技能
          </h3>
          <div class="skills-list">
            <span v-for="(skill, index) in user.skills" :key="index" class="skill-tag">
              {{ skill }}
            </span>
          </div>
        </div>

        <!-- 工作经历 -->
        <div class="glass-card experience-card" v-if="user.experience && user.experience.length > 0">
          <h3 class="card-title">
            <el-icon><Calendar /></el-icon>
            工作经历
          </h3>
          <div class="experience-list">
            <div
              v-for="(exp, index) in user.experience"
              :key="index"
              class="exp-item"
            >
              <div class="exp-timeline">
                <div class="timeline-dot"></div>
                <div class="timeline-line"></div>
              </div>
              <div class="exp-content">
                <div class="exp-header">
                  <span class="exp-position">{{ exp.position }}</span>
                  <span class="exp-period" v-if="exp.period">{{ exp.period }}</span>
                </div>
                <div class="exp-company">{{ exp.company }}</div>
                <div class="exp-description" v-if="exp.description">
                  {{ exp.description }}
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- 爱好 -->
        <div class="glass-card hobbies-card" v-if="user.hobbies">
          <h3 class="card-title">
            <el-icon><Flag /></el-icon>
            爱好
          </h3>
          <p class="hobbies-text">{{ user.hobbies }}</p>
        </div>
      </template>
    </div>
  </div>
</template>

<script>
import { ArrowLeft, School, Briefcase, Edit, Star, Calendar, Flag } from '@element-plus/icons-vue'
export default {
  components: { ArrowLeft, School, Briefcase, Edit, Star, Calendar, Flag }
}
</script>

<style scoped>
.user-detail-container {
  min-height: calc(100vh - 65px);
  padding: 20px;
}

.container {
  max-width: 800px;
  margin: 0 auto;
}

/* 返回按钮 */
.back-button {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  color: var(--text-secondary);
  cursor: pointer;
  margin-bottom: 20px;
  padding: 8px 12px;
  border-radius: 8px;
  transition: all 0.3s;
}

.back-button:hover {
  background: rgba(102, 126, 234, 0.1);
  color: #667eea;
}

/* 用户头部 */
.user-header {
  display: flex;
  align-items: center;
  gap: 24px;
  padding: 30px;
  margin-bottom: 20px;
}

.header-avatar {
  flex-shrink: 0;
}

.avatar-xl {
  width: 120px;
  height: 120px;
  font-size: 48px;
}

.header-info {
  flex: 1;
}

.user-name {
  font-size: 28px;
  font-weight: 600;
  color: var(--text-primary);
  margin-bottom: 12px;
}

.user-school,
.user-job {
  display: flex;
  align-items: center;
  gap: 6px;
  color: var(--text-secondary);
  margin-bottom: 6px;
  font-size: 15px;
}

.header-actions {
  flex-shrink: 0;
}

/* 通用卡片样式 */
.glass-card {
  padding: 24px;
  margin-bottom: 20px;
}

.card-title {
  font-size: 16px;
  font-weight: 600;
  color: var(--text-primary);
  margin-bottom: 16px;
  display: flex;
  align-items: center;
  gap: 8px;
}

/* 个人简介 */
.bio-text {
  color: var(--text-secondary);
  line-height: 1.8;
  white-space: pre-wrap;
}

/* 技能 */
.skills-list {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
}

.skill-tag {
  display: inline-block;
  padding: 8px 16px;
  background: rgba(102, 126, 234, 0.1);
  border: 1px solid rgba(102, 126, 234, 0.3);
  border-radius: 20px;
  font-size: 14px;
  color: #667eea;
}

/* 工作经历 */
.experience-list {
  position: relative;
}

.exp-item {
  display: flex;
  gap: 16px;
  padding-bottom: 24px;
  position: relative;
}

.exp-item:last-child {
  padding-bottom: 0;
}

.exp-item:last-child .timeline-line {
  display: none;
}

.exp-timeline {
  display: flex;
  flex-direction: column;
  align-items: center;
  width: 12px;
  flex-shrink: 0;
}

.timeline-dot {
  width: 12px;
  height: 12px;
  background: #667eea;
  border-radius: 50%;
  flex-shrink: 0;
}

.timeline-line {
  width: 2px;
  flex: 1;
  background: #e0e0e0;
  margin-top: 8px;
}

.exp-content {
  flex: 1;
  padding-bottom: 16px;
}

.exp-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 4px;
  flex-wrap: wrap;
  gap: 8px;
}

.exp-position {
  font-weight: 600;
  color: var(--text-primary);
  font-size: 16px;
}

.exp-period {
  font-size: 13px;
  color: var(--text-light);
  background: rgba(102, 126, 234, 0.1);
  padding: 2px 10px;
  border-radius: 12px;
}

.exp-company {
  color: var(--text-secondary);
  font-size: 15px;
  margin-bottom: 8px;
}

.exp-description {
  color: var(--text-secondary);
  font-size: 14px;
  line-height: 1.6;
}

/* 爱好 */
.hobbies-text {
  color: var(--text-secondary);
  line-height: 1.8;
  white-space: pre-wrap;
}

/* 响应式 */
@media (max-width: 768px) {
  .user-header {
    flex-direction: column;
    text-align: center;
  }

  .header-actions {
    margin-top: 16px;
  }

  .avatar-xl {
    width: 100px;
    height: 100px;
    font-size: 40px;
  }

  .user-name {
    font-size: 24px;
  }
}
</style>
