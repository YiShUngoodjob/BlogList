# BlogList - 个人博客用户展示平台

一个前后端分离的个人博客用户展示平台，基于 Vue 3 和 Flask 构建。

## 功能特点

- 👤 用户注册与登录
- 📧 邮箱验证码验证
- 🎫 邀请码注册机制
- 👥 用户列表浏览
- ✏️ 个人资料编辑
- 🖼️ 头像上传
- 🎨 响应式界面设计

## 技术栈

### 前端
- Vue 3
- Vite
- Element Plus
- Vue Router
- Axios

### 后端
- Flask
- SQLAlchemy
- JWT 认证
- Flask-CORS

## 项目结构

```
BlogList/
├── backend/           # 后端服务
│   ├── app.py         # Flask 应用主文件
│   ├── models.py      # 数据库模型
│   ├── requirements.txt
│   └── ...
├── frontend/          # 前端应用
│   ├── src/
│   │   ├── views/    # 页面组件
│   │   ├── api/      # API 接口
│   │   └── ...
│   ├── package.json
│   └── ...
└── README.md
```

## 快速开始

### 前提条件

- Node.js 16+
- Python 3.8+

### 1. 克隆项目

```bash
git clone https://github.com/YiShUngoodjob/BlogList.git
cd BlogList
```

### 2. 启动后端

```bash
cd backend

# 创建虚拟环境（可选）
python -m venv venv
# Windows
venv\Scripts\activate
# Linux/Mac
source venv/bin/activate

# 安装依赖
pip install -r requirements.txt

# 启动服务
python app.py
```

后端服务将在 http://localhost:5000 运行

### 3. 启动前端

```bash
cd frontend

# 安装依赖
npm install

# 启动开发服务器
npm run dev
```

前端应用将在 http://localhost:5173 运行

### 4. 访问项目

在浏览器中打开 http://localhost:5173 即可访问应用。

## 配置说明

### 后端环境变量

在 `backend/` 目录下创建 `.env` 文件：

```env
SECRET_KEY=your-secret-key
MAIL_SERVER=smtp.qq.com
MAIL_PORT=587
MAIL_USE_TLS=True
MAIL_USERNAME=your-email@qq.com
MAIL_PASSWORD=your-email-password
MAIL_DEFAULT_SENDER=your-email@qq.com
```

### 邀请码配置

在 `backend/` 目录下创建 `vipcode.json` 文件：

```json
["邀请码1", "邀请码2", "邀请码3"]
```

或者运行生成脚本：

```bash
python generate_codes.py
```

## API 接口

| 接口 | 方法 | 描述 |
|------|------|------|
| `/api/users` | GET | 获取用户列表 |
| `/api/users/<id>` | GET | 获取用户详情 |
| `/api/register` | POST | 用户注册 |
| `/api/login` | POST | 用户登录 |
| `/api/me` | GET | 获取当前用户信息 |
| `/api/profile` | PUT | 更新用户资料 |
| `/api/avatar` | POST | 上传头像 |
| `/api/send-code` | POST | 发送邮箱验证码 |

## 许可证

MIT License
