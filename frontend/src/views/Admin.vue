<script setup>
import { ref, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { adminAPI } from '../api/index'

const loading = ref(false)
const users = ref([])
const total = ref(0)
const currentPage = ref(1)
const editDialogVisible = ref(false)
const editingUser = ref(null)
const editForm = ref({
  name: '',
  school: '',
  job: '',
  bio: '',
  skills: [],
  experience: [],
  hobbies: ''
})

const loadUsers = async () => {
  loading.value = true
  try {
    const res = await adminAPI.getAllUsers({ page: currentPage.value, per_page: 20 })
    users.value = res.data.users
    total.value = res.data.total
  } catch (err) {
    ElMessage.error('加载用户列表失败')
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  loadUsers()
})

const handlePageChange = (page) => {
  currentPage.value = page
  loadUsers()
}

const handleDelete = async (user) => {
  try {
    await ElMessageBox.confirm(
      `确定要删除用户 "${user.name}" 吗？此操作不可恢复。`,
      '删除确认',
      {
        confirmButtonText: '确定删除',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )
    await adminAPI.deleteUser(user.id)
    ElMessage.success('删除成功')
    loadUsers()
  } catch (err) {
    if (err !== 'cancel') {
      ElMessage.error('删除失败')
    }
  }
}

const handleEdit = (user) => {
  editingUser.value = user
  editForm.value = {
    name: user.name || '',
    school: user.school || '',
    job: user.job || '',
    bio: user.bio || '',
    skills: user.skills || [],
    experience: user.experience || [],
    hobbies: user.hobbies || ''
  }
  editDialogVisible.value = true
}

const submitEdit = async () => {
  try {
    await adminAPI.updateUser(editingUser.value.id, editForm.value)
    ElMessage.success('更新成功')
    editDialogVisible.value = false
    loadUsers()
  } catch (err) {
    ElMessage.error('更新失败')
  }
}

const addExperience = () => {
  editForm.value.experience.push({
    company: '',
    position: '',
    period: '',
    description: ''
  })
}

const removeExperience = (index) => {
  editForm.value.experience.splice(index, 1)
}
</script>

<template>
  <div class="admin-container">
    <div class="admin-card">
      <h2 class="page-title">用户管理</h2>

      <el-table :data="users" v-loading="loading" style="width: 100%">
        <el-table-column prop="name" label="姓名" width="120" />
        <el-table-column prop="username" label="邮箱" min-width="180" />
        <el-table-column prop="school" label="学校" width="150" />
        <el-table-column prop="job" label="职业" width="120" />
        <el-table-column prop="created_at" label="注册时间" width="180">
          <template #default="{ row }">
            {{ row.created_at ? new Date(row.created_at).toLocaleDateString() : '-' }}
          </template>
        </el-table-column>
        <el-table-column label="操作" width="180" fixed="right">
          <template #default="{ row }">
            <el-button type="primary" size="small" @click="handleEdit(row)">
              编辑
            </el-button>
            <el-button type="danger" size="small" @click="handleDelete(row)">
              删除
            </el-button>
          </template>
        </el-table-column>
      </el-table>

      <div class="pagination">
        <el-pagination
          v-model:current-page="currentPage"
          :page-size="20"
          :total="total"
          layout="prev, pager, next"
          @current-change="handlePageChange"
        />
      </div>
    </div>

    <!-- 编辑弹窗 -->
    <el-dialog
      v-model="editDialogVisible"
      title="编辑用户信息"
      width="600px"
      :close-on-click-modal="false"
    >
      <el-form :model="editForm" label-width="80px">
        <el-form-item label="姓名">
          <el-input v-model="editForm.name" maxlength="20" />
        </el-form-item>
        <el-form-item label="学校">
          <el-input v-model="editForm.school" maxlength="50" />
        </el-form-item>
        <el-form-item label="职业">
          <el-input v-model="editForm.job" maxlength="30" />
        </el-form-item>
        <el-form-item label="简介">
          <el-input v-model="editForm.bio" type="textarea" maxlength="200" rows="3" />
        </el-form-item>
        <el-form-item label="技能">
          <el-select
            v-model="editForm.skills"
            multiple
            filterable
            allow-create
            default-first-option
            placeholder="输入技能后回车添加"
            style="width: 100%"
          >
            <el-option
              v-for="skill in editForm.skills"
              :key="skill"
              :label="skill"
              :value="skill"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="工作经历">
          <div v-for="(exp, index) in editForm.experience" :key="index" class="experience-item">
            <el-input v-model="exp.company" placeholder="公司" style="width: 30%" />
            <el-input v-model="exp.position" placeholder="职位" style="width: 20%" />
            <el-input v-model="exp.period" placeholder="时间段" style="width: 20%" />
            <el-button type="danger" text @click="removeExperience(index)">删除</el-button>
          </div>
          <el-button type="primary" text @click="addExperience">+ 添加</el-button>
        </el-form-item>
        <el-form-item label="爱好">
          <el-input v-model="editForm.hobbies" type="textarea" rows="2" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="editDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="submitEdit">保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<style scoped>
.admin-container {
  min-height: 100vh;
  padding: 24px;
  background: var(--bg-color);
}

.admin-card {
  background: var(--card-bg);
  backdrop-filter: blur(var(--blur-amount));
  -webkit-backdrop-filter: blur(var(--blur-amount));
  border-radius: 16px;
  padding: 24px;
  box-shadow: 0 4px 24px rgba(0, 0, 0, 0.08);
}

.page-title {
  margin: 0 0 24px 0;
  font-size: 24px;
  font-weight: 600;
  color: var(--text-primary);
}

.pagination {
  margin-top: 24px;
  display: flex;
  justify-content: center;
}

.experience-item {
  display: flex;
  gap: 8px;
  margin-bottom: 8px;
}
</style>