<script setup>
import { ref, onMounted, computed } from 'vue'
import { useRouter } from 'vue-router'
import { userAPI } from '../api'

const router = useRouter()
const users = ref([])
const loading = ref(false)
const currentPage = ref(1)
const total = ref(0)
const perPage = 10

onMounted(() => {
  loadUsers()
})

const loadUsers = async () => {
  loading.value = true
  try {
    const { data } = await userAPI.getAllUsers({
      page: currentPage.value,
      per_page: perPage
    })
    users.value = data.users
    total.value = data.total
  } catch (error) {
    console.error(error)
  } finally {
    loading.value = false
  }
}

const handlePageChange = (page) => {
  currentPage.value = page
  loadUsers()
}

const goToDetail = (id) => {
  router.push(`/user/${id}`)
}

const goToRegister = () => {
  router.push('/register')
}

// 获取头像URL
const getAvatarUrl = (user) => {
  if (user.avatar_url) {
    return 'http://localhost:5000' + user.avatar_url
  }
  return null
}

// 获取名字首字
const getInitial = (name) => {
  if (name) {
    return name.charAt(0)
  }
  return '?'
}

// 显示信息（职业或学校）
const displayInfo = (user) => {
  return user.job || user.school || ''
}
</script>

<template>
  <div class="user-list-container">
    <div class="container">
      <div class="page-header">
        <h1 class="page-title">发现 TA</h1>
        <p class="page-subtitle">探索世界，发现精彩</p>
      </div>

      <!-- 用户列表 -->
      <div v-loading="loading" class="user-grid">
        <div
          v-for="user in users"
          :key="user.id"
          class="user-card glass-card"
          @click="goToDetail(user.id)"
        >
          <div class="card-avatar">
            <img v-if="getAvatarUrl(user)" :src="getAvatarUrl(user)" class="avatar avatar-md" />
            <div v-else class="avatar-placeholder avatar-md">
              {{ getInitial(user.name) }}
            </div>
          </div>
          <div class="card-info">
            <h3 class="user-name">{{ user.name }}</h3>
            <p class="user-info" v-if="displayInfo(user)">{{ displayInfo(user) }}</p>
          </div>
        </div>
      </div>

      <!-- 空状态 -->
      <div v-if="!loading && users.length === 0" class="empty-state glass-card">
        <el-icon class="empty-icon"><UserFilled /></el-icon>
        <h3>暂无博客，快来创建第一个吧！</h3>
        <p>分享你自己，让更多人认识你</p>
        <el-button type="primary" @click="goToRegister">立即创建</el-button>
      </div>

      <!-- 分页 -->
      <div v-if="total > perPage" class="pagination">
        <el-pagination
          background
          layout="prev, pager, next"
          :total="total"
          :page-size="perPage"
          :current-page="currentPage"
          @current-change="handlePageChange"
        />
      </div>
    </div>
  </div>
</template>

<script>
import { UserFilled } from '@element-plus/icons-vue'
export default {
  components: { UserFilled }
}
</script>

<style scoped>
.user-list-container {
  min-height: calc(100vh - 65px);
  padding: 20px;
}

.container {
  max-width: 1000px;
  margin: 0 auto;
}

/* 页面头部 */
.page-header {
  text-align: center;
  margin-bottom: 40px;
  padding: 40px 0;
}

.page-title {
  font-size: 36px;
  margin-bottom: 10px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.page-subtitle {
  color: var(--text-secondary);
  font-size: 16px;
}

/* 用户卡片网格 */
.user-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: 20px;
}

.user-card {
  padding: 24px;
  display: flex;
  flex-direction: column;
  align-items: center;
  text-align: center;
  cursor: pointer;
  transition: all 0.3s ease;
}

.user-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 12px 40px rgba(0, 0, 0, 0.12);
}

.card-avatar {
  margin-bottom: 16px;
}

.avatar-md {
  width: 80px;
  height: 80px;
  font-size: 32px;
}

.user-name {
  font-size: 18px;
  font-weight: 600;
  color: var(--text-primary);
  margin-bottom: 6px;
}

.user-info {
  font-size: 14px;
  color: var(--text-secondary);
}

/* 空状态 */
.empty-state {
  text-align: center;
  padding: 60px 20px;
  margin-top: 40px;
}

.empty-icon {
  font-size: 64px;
  color: #dcdfe6;
  margin-bottom: 20px;
}

.empty-state h3 {
  font-size: 20px;
  color: var(--text-primary);
  margin-bottom: 10px;
}

.empty-state p {
  color: var(--text-secondary);
  margin-bottom: 20px;
}

/* 分页 */
.pagination {
  display: flex;
  justify-content: center;
  margin-top: 40px;
}

@media (max-width: 768px) {
  .user-grid {
    grid-template-columns: repeat(auto-fill, minmax(240px, 1fr));
  }

  .page-header {
    padding: 20px 0;
  }

  .page-title {
    font-size: 28px;
  }
}
</style>
