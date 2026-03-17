<script setup>
import { ref, onMounted, computed } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { authAPI, userAPI } from '../api'

const router = useRouter()
const loading = ref(false)
const saving = ref(false)

// 表单数据
const form = ref({
  name: '',
  school: '',
  job: '',
  bio: '',
  skills: [],
  experience: [],
  hobbies: ''
})

const newSkill = ref('')
const avatarFile = ref(null)
const avatarPreview = ref('')

// 工作经历表单
const experienceForm = ref({
  company: '',
  position: '',
  period: '',
  description: ''
})
const showExpDialog = ref(false)
const editingExpIndex = ref(-1)

// 检查是否已登录
onMounted(async () => {
  const token = localStorage.getItem('token')
  if (!token) {
    ElMessage.warning('请先登录')
    router.push('/login')
    return
  }

  await loadUserData()
})

const loadUserData = async () => {
  loading.value = true
  try {
    const { data } = await authAPI.getCurrentUser()
    form.value = {
      name: data.name || '',
      school: data.school || '',
      job: data.job || '',
      bio: data.bio || '',
      skills: data.skills || [],
      experience: data.experience || [],
      hobbies: data.hobbies || ''
    }
    if (data.avatar_url) {
      avatarPreview.value = 'http://localhost:5000' + data.avatar_url
    }
  } catch (error) {
    console.error(error)
  } finally {
    loading.value = false
  }
}

// 处理头像选择
const handleAvatarChange = (event) => {
  const file = event.target.files[0]
  if (!file) return false

  const isImage = file.type.startsWith('image/')
  const isLt5M = file.size / 1024 / 1024 < 5

  if (!isImage) {
    ElMessage.error('只能上传图片文件')
    return false
  }
  if (!isLt5M) {
    ElMessage.error('图片大小不能超过 5MB')
    return false
  }

  avatarFile.value = file
  avatarPreview.value = URL.createObjectURL(file)
  return false
}

// 添加技能
const addSkill = () => {
  const skill = newSkill.value.trim()
  if (!skill) return

  if (skill.length > 10) {
    ElMessage.warning('每个技能不能超过10个字符')
    return
  }

  if (form.value.skills.length >= 10) {
    ElMessage.warning('最多添加10个技能')
    return
  }

  if (!form.value.skills.includes(skill)) {
    form.value.skills.push(skill)
  }
  newSkill.value = ''
}

// 删除技能
const removeSkill = (index) => {
  form.value.skills.splice(index, 1)
}

// 添加工作经历
const addExperience = () => {
  if (!experienceForm.value.company || !experienceForm.value.position) {
    ElMessage.warning('请填写公司和职位')
    return
  }

  if (editingExpIndex.value >= 0) {
    form.value.experience[editingExpIndex.value] = { ...experienceForm.value }
    editingExpIndex.value = -1
  } else {
    form.value.experience.push({ ...experienceForm.value })
  }

  experienceForm.value = { company: '', position: '', period: '', description: '' }
  showExpDialog.value = false
}

// 编辑工作经历
const editExperience = (index) => {
  experienceForm.value = { ...form.value.experience[index] }
  editingExpIndex.value = index
  showExpDialog.value = true
}

// 删除工作经历
const removeExperience = (index) => {
  form.value.experience.splice(index, 1)
}

// 保存个人信息
const handleSave = async () => {
  if (!form.value.name) {
    ElMessage.warning('请填写姓名')
    return
  }

  saving.value = true
  try {
    // 先上传头像
    if (avatarFile.value) {
      const formData = new FormData()
      formData.append('avatar', avatarFile.value)
      const uploadRes = await userAPI.uploadAvatar(formData)
      // 更新本地头像预览
      avatarPreview.value = 'http://localhost:5000' + uploadRes.data.avatar_url
    }

    // 保存个人信息
    const { data } = await userAPI.updateProfile(form.value)
    localStorage.setItem('user', JSON.stringify(data.user))
    ElMessage.success('保存成功')
    router.push('/')
  } catch (error) {
    console.error(error)
    ElMessage.error(error.response?.data?.message || '保存失败')
  } finally {
    saving.value = false
  }
}

// 获取名字首字
const getInitial = computed(() => {
  if (form.value.name) {
    return form.value.name.charAt(0)
  }
  return '?'
})
</script>

<template>
  <div class="profile-edit-container">
    <div class="container">
      <div class="glass-card profile-card">
        <h1 class="page-title">编辑个人资料</h1>

        <div v-loading="loading">
          <!-- 头像上传 -->
          <div class="avatar-section">
            <div class="avatar-wrapper" @click="$refs.avatarInput.click()">
              <img v-if="avatarPreview" :src="avatarPreview" class="avatar avatar-lg" />
              <div v-else class="avatar-placeholder avatar-lg">
                {{ getInitial }}
              </div>
              <div class="avatar-overlay">
                <el-icon><Camera /></el-icon>
              </div>
            </div>
            <input
              ref="avatarInput"
              type="file"
              accept="image/jpeg,image/png,image/gif"
              style="display: none"
              @change="handleAvatarChange"
            />
            <p class="avatar-hint">点击上传头像 (JPG, PNG, GIF ≤ 5MB)</p>
          </div>

          <!-- 基本信息 -->
          <div class="form-section">
            <h3 class="section-title">基本信息</h3>
            <el-form label-width="80px">
              <el-form-item label="姓名">
                <el-input v-model="form.name" placeholder="必填" maxlength="20" />
              </el-form-item>
              <el-form-item label="学校">
                <el-input v-model="form.school" placeholder="选填" maxlength="50" />
              </el-form-item>
              <el-form-item label="职业">
                <el-input v-model="form.job" placeholder="选填" maxlength="30" />
              </el-form-item>
              <el-form-item label="简介">
                <el-input
                  v-model="form.bio"
                  type="textarea"
                  :rows="3"
                  placeholder="介绍一下自己吧"
                  maxlength="200"
                  show-word-limit
                />
              </el-form-item>
            </el-form>
          </div>

          <!-- 技能 -->
          <div class="form-section">
            <h3 class="section-title">技能</h3>
            <div class="skills-input">
              <el-input
                v-model="newSkill"
                placeholder="输入技能，按回车添加"
                maxlength="10"
                @keyup.enter="addSkill"
              >
                <template #append>
                  <el-button @click="addSkill">添加</el-button>
                </template>
              </el-input>
            </div>
            <div class="skills-list">
              <span
                v-for="(skill, index) in form.skills"
                :key="index"
                class="skill-tag"
              >
                {{ skill }}
                <el-icon class="remove-btn" @click="removeSkill(index)"><Close /></el-icon>
              </span>
            </div>
            <p class="hint">最多10个技能，每个不超过10个字符</p>
          </div>

          <!-- 工作经历 -->
          <div class="form-section">
            <div class="section-header">
              <h3 class="section-title">工作经历</h3>
              <el-button size="small" @click="showExpDialog = true">
                <el-icon><Plus /></el-icon> 添加
              </el-button>
            </div>
            <div class="experience-list">
              <div
                v-for="(exp, index) in form.experience"
                :key="index"
                class="experience-item glass-card"
              >
                <div class="exp-content">
                  <div class="exp-header">
                    <span class="exp-position">{{ exp.position }}</span>
                    <span class="exp-period">{{ exp.period }}</span>
                  </div>
                  <div class="exp-company">{{ exp.company }}</div>
                  <div class="exp-description" v-if="exp.description">{{ exp.description }}</div>
                </div>
                <div class="exp-actions">
                  <el-icon @click="editExperience(index)"><Edit /></el-icon>
                  <el-icon @click="removeExperience(index)"><Delete /></el-icon>
                </div>
              </div>
              <div v-if="form.experience.length === 0" class="empty-exp">
                暂无工作经历
              </div>
            </div>
          </div>

          <!-- 爱好 -->
          <div class="form-section">
            <h3 class="section-title">爱好</h3>
            <el-input
              v-model="form.hobbies"
              type="textarea"
              :rows="2"
              placeholder="写下你的爱好吧"
            />
          </div>

          <!-- 保存按钮 -->
          <div class="form-actions">
            <el-button size="large" @click="router.push('/')">取消</el-button>
            <el-button type="primary" size="large" :loading="saving" @click="handleSave">
              保存并展示
            </el-button>
          </div>
        </div>
      </div>
    </div>

    <!-- 工作经历弹窗 -->
    <el-dialog v-model="showExpDialog" title="添加工作经历" width="500px">
      <el-form :model="experienceForm" label-width="80px">
        <el-form-item label="公司" required>
          <el-input v-model="experienceForm.company" placeholder="公司名称" />
        </el-form-item>
        <el-form-item label="职位" required>
          <el-input v-model="experienceForm.position" placeholder="职位名称" />
        </el-form-item>
        <el-form-item label="时间段">
          <el-input v-model="experienceForm.period" placeholder="例如：2020-至今" />
        </el-form-item>
        <el-form-item label="描述">
          <el-input
            v-model="experienceForm.description"
            type="textarea"
            :rows="3"
            placeholder="工作描述"
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showExpDialog = false">取消</el-button>
        <el-button type="primary" @click="addExperience">确定</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script>
import { Camera, Close, Plus, Edit, Delete } from '@element-plus/icons-vue'
export default {
  components: { Camera, Close, Plus, Edit, Delete }
}
</script>

<style scoped>
.profile-edit-container {
  min-height: calc(100vh - 65px);
  padding: 20px;
}

.container {
  max-width: 700px;
  margin: 0 auto;
}

.profile-card {
  padding: 30px;
}

.page-title {
  text-align: center;
  margin-bottom: 30px;
  font-size: 24px;
}

/* 头像 */
.avatar-section {
  text-align: center;
  margin-bottom: 30px;
}

.avatar-wrapper {
  position: relative;
  width: 120px;
  height: 120px;
  margin: 0 auto;
  cursor: pointer;
  border-radius: 50%;
}

.avatar-lg {
  width: 120px;
  height: 120px;
  font-size: 48px;
}

.avatar-overlay {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  border-radius: 50%;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  opacity: 0;
  transition: opacity 0.3s;
  color: white;
  font-size: 24px;
}

.avatar-wrapper:hover .avatar-overlay {
  opacity: 1;
}

.avatar-hint {
  margin-top: 10px;
  font-size: 12px;
  color: var(--text-light);
}

/* 表单区域 */
.form-section {
  margin-bottom: 30px;
}

.section-title {
  font-size: 16px;
  margin-bottom: 15px;
  color: var(--text-primary);
  border-left: 3px solid #667eea;
  padding-left: 10px;
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 15px;
}

.section-header .section-title {
  margin-bottom: 0;
}

/* 技能 */
.skills-input {
  margin-bottom: 15px;
}

.skills-list {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.skill-tag {
  display: inline-flex;
  align-items: center;
  padding: 6px 12px;
  background: rgba(102, 126, 234, 0.1);
  border: 1px solid rgba(102, 126, 234, 0.3);
  border-radius: 20px;
  font-size: 13px;
  color: #667eea;
}

.remove-btn {
  margin-left: 6px;
  cursor: pointer;
  font-size: 12px;
}

.remove-btn:hover {
  color: #f56c6c;
}

.hint {
  margin-top: 8px;
  font-size: 12px;
  color: var(--text-light);
}

/* 工作经历 */
.experience-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.experience-item {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  padding: 15px;
}

.exp-content {
  flex: 1;
}

.exp-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 5px;
}

.exp-position {
  font-weight: 600;
  color: var(--text-primary);
}

.exp-period {
  font-size: 12px;
  color: var(--text-light);
}

.exp-company {
  color: var(--text-secondary);
  margin-bottom: 5px;
}

.exp-description {
  font-size: 13px;
  color: var(--text-secondary);
  margin-top: 8px;
}

.exp-actions {
  display: flex;
  gap: 10px;
  color: var(--text-light);
  cursor: pointer;
}

.exp-actions:hover {
  color: #667eea;
}

.empty-exp {
  text-align: center;
  padding: 20px;
  color: var(--text-light);
  background: rgba(255, 255, 255, 0.3);
  border-radius: 8px;
}

/* 操作按钮 */
.form-actions {
  display: flex;
  justify-content: center;
  gap: 15px;
  margin-top: 30px;
  padding-top: 20px;
  border-top: 1px solid #eee;
}
</style>
