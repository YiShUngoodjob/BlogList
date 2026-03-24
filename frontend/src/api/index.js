import axios from 'axios'

const API_BASE_URL = 'http://localhost:5000/api'

const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json'
  }
})

// 添加 token 到请求头
api.interceptors.request.use(
  config => {
    const token = localStorage.getItem('token')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  error => {
    return Promise.reject(error)
  }
)

// 处理响应错误
api.interceptors.response.use(
  response => response,
  error => {
    if (error.response?.status === 401) {
      localStorage.removeItem('token')
      localStorage.removeItem('user')
      window.location.href = '/login'
    }
    return Promise.reject(error)
  }
)

// 认证相关
export const authAPI = {
  // 发送验证码
  sendCode(data) {
    return api.post('/send-code', data)
  },

  // 注册（需要邮箱、验证码、邀请码）
  register(data) {
    return api.post('/register', data)
  },

  login(data) {
    return api.post('/login', data)
  },

  getCurrentUser() {
    return api.get('/me')
  }
}

// 用户相关
export const userAPI = {
  getAllUsers(params) {
    return api.get('/users', { params })
  },
  getUser(id) {
    return api.get(`/users/${id}`)
  },
  updateProfile(data) {
    return api.put('/profile', data)
  },
  uploadAvatar(formData) {
    return api.post('/avatar', formData, {
      headers: {
        'Content-Type': 'multipart/form-data'
      }
    })
  }
}

// 私信相关
export const messageAPI = {
  getConversationList() {
    return api.get('/messages')
  },
  getConversation(userId, params) {
    return api.get(`/messages/${userId}`, { params })
  },
  sendMessage(data) {
    return api.post('/messages', data)
  },
  updateMessageStatus(messageId, status) {
    return api.put(`/messages/${messageId}/status`, { status })
  },
  getUnreadCount() {
    return api.get('/messages/unread')
  }
}

export default api
