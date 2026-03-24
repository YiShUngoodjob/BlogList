<template>
  <div class="chat-page">
    <div class="chat-container">
      <div class="chat-sidebar">
        <div class="sidebar-header">
          <h3>私信消息</h3>
        </div>
        <div class="conversation-list">
          <div
            v-for="conv in conversations"
            :key="conv.partner.id"
            class="conversation-item"
            :class="{ active: currentPartner?.id === conv.partner.id }"
            @click="selectConversation(conv)"
          >
            <el-avatar :size="45" :src="conv.partner.avatar_url">
              {{ conv.partner.name?.[0] }}
            </el-avatar>
            <div class="conv-info">
              <div class="conv-header">
                <span class="conv-name">{{ conv.partner.name }}</span>
                <span class="conv-time">{{ formatTime(conv.last_time) }}</span>
              </div>
              <div class="conv-preview">
                <span class="preview-text">{{ conv.last_message?.content || '暂无消息' }}</span>
                <el-badge v-if="conv.unread_count > 0" :value="conv.unread_count" class="unread-badge" />
              </div>
            </div>
          </div>
          <div v-if="conversations.length === 0" class="empty-conv">
            <el-empty description="暂无私信会话" :image-size="80" />
          </div>
        </div>
      </div>

      <div class="chat-main">
        <template v-if="currentPartner">
          <div class="chat-header">
            <el-avatar :size="40" :src="currentPartner.avatar_url">
              {{ currentPartner.name?.[0] }}
            </el-avatar>
            <span class="partner-name">{{ currentPartner.name }}</span>
          </div>

          <div class="message-list" ref="messageListRef">
            <div
              v-for="msg in messages"
              :key="msg.id"
              class="message-item"
              :class="{ mine: msg.sender_id === currentUser.id }"
            >
              <el-avatar v-if="msg.sender_id !== currentUser.id" :size="35" :src="msg.sender?.avatar_url">
                {{ msg.sender?.name?.[0] }}
              </el-avatar>
              <div class="message-content">
                <div class="message-bubble">{{ msg.content }}</div>
                <div class="message-meta">
                  <span class="message-time">{{ formatMessageTime(msg.created_at) }}</span>
                  <span v-if="msg.sender_id === currentUser.id" class="message-status">
                    {{ getStatusText(msg.status) }}
                  </span>
                </div>
              </div>
              <el-avatar v-if="msg.sender_id === currentUser.id" :size="35" :src="currentUser.avatar_url">
                {{ currentUser.name?.[0] }}
              </el-avatar>
            </div>
          </div>

          <div class="chat-input">
            <el-input
              v-model="newMessage"
              type="textarea"
              :rows="2"
              placeholder="输入私信内容..."
              @keydown.enter.exact.prevent="sendMessage"
            />
            <el-button type="primary" :loading="sending" @click="sendMessage">
              <el-icon><Position /></el-icon>
              发送
            </el-button>
          </div>
        </template>

        <div v-else class="no-chat">
          <el-empty description="选择一个会话开始聊天" :image-size="120" />
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, nextTick, watch } from 'vue'
import { useRoute } from 'vue-router'
import { ElMessage } from 'element-plus'
import { Position } from '@element-plus/icons-vue'
import { messageAPI } from '../api'

const route = useRoute()
const conversations = ref([])
const currentPartner = ref(null)
const messages = ref([])
const newMessage = ref('')
const sending = ref(false)
const messageListRef = ref(null)
const currentUser = ref(JSON.parse(localStorage.getItem('user') || '{}'))

const loadConversations = async () => {
  try {
    const res = await messageAPI.getConversationList()
    conversations.value = res.data.conversations
  } catch (err) {
    console.error('Failed to load conversations:', err)
  }
}

const selectConversation = async (conv) => {
  currentPartner.value = conv.partner
  await loadMessages()
}

const loadMessages = async () => {
  if (!currentPartner.value) return
  try {
    const res = await messageAPI.getConversation(currentPartner.value.id)
    messages.value = res.data.messages
    await nextTick()
    scrollToBottom()
    await loadConversations()
  } catch (err) {
    ElMessage.error('加载消息失败')
  }
}

const sendMessage = async () => {
  if (!newMessage.value.trim() || !currentPartner.value || sending.value) return

  sending.value = true
  try {
    const res = await messageAPI.sendMessage({
      receiver_id: currentPartner.value.id,
      content: newMessage.value.trim()
    })
    messages.value.push(res.data.msg)
    newMessage.value = ''
    await nextTick()
    scrollToBottom()
    await loadConversations()
  } catch (err) {
    ElMessage.error(err.response?.data?.message || '发送失败')
  } finally {
    sending.value = false
  }
}

const scrollToBottom = () => {
  if (messageListRef.value) {
    messageListRef.value.scrollTop = messageListRef.value.scrollHeight
  }
}

const formatTime = (time) => {
  if (!time) return ''
  const date = new Date(time)
  const now = new Date()
  const diff = now - date

  if (diff < 60000) return '刚刚'
  if (diff < 3600000) return Math.floor(diff / 60000) + '分钟前'
  if (diff < 86400000) return Math.floor(diff / 3600000) + '小时前'
  if (diff < 604800000) return Math.floor(diff / 86400000) + '天前'
  return date.toLocaleDateString()
}

const formatMessageTime = (time) => {
  if (!time) return ''
  const date = new Date(time)
  return date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
}

const getStatusText = (status) => {
  const statusMap = {
    'sent': '已发送',
    'delivered': '已送达',
    'read': '已读'
  }
  return statusMap[status] || ''
}

onMounted(async () => {
  await loadConversations()
  if (route.query.userId) {
    const conv = conversations.value.find(c => c.partner.id === route.query.userId)
    if (conv) {
      await selectConversation(conv)
    } else {
      try {
        const res = await fetch(`http://localhost:5000/api/users/${route.query.userId}`)
        const data = await res.json()
        currentPartner.value = data
      } catch (err) {
        console.error(err)
      }
    }
  }
})
</script>

<style scoped>
.chat-page {
  min-height: calc(100vh - 120px);
  padding: 20px;
}

.chat-container {
  display: flex;
  height: calc(100vh - 160px);
  background: #fff;
  border-radius: 12px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.1);
  overflow: hidden;
}

.chat-sidebar {
  width: 320px;
  border-right: 1px solid #eee;
  display: flex;
  flex-direction: column;
}

.sidebar-header {
  padding: 20px;
  border-bottom: 1px solid #eee;
}

.sidebar-header h3 {
  margin: 0;
  font-size: 18px;
  color: #333;
}

.conversation-list {
  flex: 1;
  overflow-y: auto;
}

.conversation-item {
  display: flex;
  padding: 15px 20px;
  cursor: pointer;
  transition: background 0.2s;
  border-bottom: 1px solid #f5f5f5;
}

.conversation-item:hover {
  background: #f8f9fa;
}

.conversation-item.active {
  background: #ecf5ff;
}

.conv-info {
  flex: 1;
  margin-left: 12px;
  overflow: hidden;
}

.conv-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 4px;
}

.conv-name {
  font-weight: 500;
  color: #333;
}

.conv-time {
  font-size: 12px;
  color: #999;
}

.conv-preview {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.preview-text {
  font-size: 13px;
  color: #666;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  max-width: 160px;
}

.unread-badge {
  flex-shrink: 0;
}

.empty-conv {
  padding: 40px 0;
}

.chat-main {
  flex: 1;
  display: flex;
  flex-direction: column;
}

.chat-header {
  display: flex;
  align-items: center;
  padding: 15px 20px;
  border-bottom: 1px solid #eee;
}

.partner-name {
  margin-left: 12px;
  font-size: 16px;
  font-weight: 500;
  color: #333;
}

.message-list {
  flex: 1;
  overflow-y: auto;
  padding: 20px;
  display: flex;
  flex-direction: column;
  gap: 15px;
}

.message-item {
  display: flex;
  align-items: flex-start;
  gap: 10px;
}

.message-item.mine {
  flex-direction: row-reverse;
}

.message-content {
  max-width: 60%;
}

.message-bubble {
  padding: 10px 15px;
  border-radius: 8px;
  background: #f0f2f5;
  color: #333;
  line-height: 1.5;
  word-break: break-word;
}

.message-item.mine .message-bubble {
  background: #409eff;
  color: #fff;
}

.message-meta {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-top: 4px;
  font-size: 11px;
  color: #999;
}

.message-item.mine .message-meta {
  justify-content: flex-end;
}

.chat-input {
  display: flex;
  align-items: flex-end;
  gap: 10px;
  padding: 15px 20px;
  border-top: 1px solid #eee;
}

.chat-input .el-textarea {
  flex: 1;
}

.no-chat {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
}
</style>
