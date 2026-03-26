import os
import json
import random
import string
import smtplib
from email.mime.text import MIMEText
from datetime import datetime, timedelta
from functools import wraps

from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from dotenv import load_dotenv
import jwt

from models import db, User, Message

# 加载环境变量
load_dotenv()

app = Flask(__name__)
CORS(app, resources={r"/api/*": {"origins": "*"}})

# 配置
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'your-secret-key-change-in-production')
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///blog.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = os.path.join(os.path.dirname(__file__), 'uploads')
app.config['MAX_CONTENT_LENGTH'] = 5 * 1024 * 1024  # 5MB

# 邮箱配置
app.config['MAIL_SERVER'] = os.environ.get('MAIL_SERVER', 'smtp.qq.com')
app.config['MAIL_PORT'] = int(os.environ.get('MAIL_PORT', 587))
app.config['MAIL_USE_TLS'] = os.environ.get('MAIL_USE_TLS', 'True') == 'True'
app.config['MAIL_USERNAME'] = os.environ.get('MAIL_USERNAME')
app.config['MAIL_PASSWORD'] = os.environ.get('MAIL_PASSWORD')
app.config['MAIL_DEFAULT_SENDER'] = os.environ.get('MAIL_DEFAULT_SENDER')

# 确保上传目录存在
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# 允许的文件扩展名
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

# 验证码和邀请码存储（生产环境应使用 Redis）
verification_codes = {}  # {email: {code: xxx, expires: datetime, type: 'register'|'reset'}}
reset_password_codes = {}  # {email: {code: xxx, expires: datetime}}

db.init_app(app)

with app.app_context():
    db.create_all()


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def load_invite_codes():
    """加载邀请码"""
    try:
        code_file = os.path.join(os.path.dirname(__file__), 'vipcode.json')
        with open(code_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        return []


def check_invite_code(code):
    """检查邀请码是否有效"""
    valid_codes = load_invite_codes()
    return code in valid_codes


def send_verification_email(email, code):
    """发送验证码邮件"""
    try:
        msg = MIMEText(f'您的注册验证码是：{code}，5分钟内有效。', 'plain', 'utf-8')
        msg['Subject'] = '个人博客注册验证码'
        msg['From'] = app.config['MAIL_DEFAULT_SENDER']
        msg['To'] = email

        server = smtplib.SMTP(app.config['MAIL_SERVER'], app.config['MAIL_PORT'])
        server.starttls()
        server.login(app.config['MAIL_USERNAME'], app.config['MAIL_PASSWORD'])
        server.sendmail(app.config['MAIL_DEFAULT_SENDER'], email, msg.as_string())
        server.quit()
        return True
    except Exception as e:
        print(f"发送邮件失败: {e}")
        return False


def generate_code(length=6):
    """生成随机数字验证码"""
    return ''.join(random.choices(string.digits, k=length))


def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        if 'Authorization' in request.headers:
            auth_header = request.headers['Authorization']
            if auth_header.startswith('Bearer '):
                token = auth_header.split(' ')[1]

        if not token:
            return jsonify({'message': 'Token is missing'}), 401

        try:
            data = jwt.decode(token, app.config['SECRET_KEY'], algorithms=['HS256'])
            current_user = db.session.get(User, data['user_id'])
            if not current_user:
                return jsonify({'message': 'User not found'}), 401
        except jwt.ExpiredSignatureError:
            return jsonify({'message': 'Token has expired'}), 401
        except jwt.InvalidTokenError:
            return jsonify({'message': 'Invalid token'}), 401

        return f(current_user, *args, **kwargs)

    return decorated


def admin_required(f):
    @wraps(f)
    def decorated(current_user, *args, **kwargs):
        if not current_user.is_admin:
            return jsonify({'message': 'Admin access required'}), 403
        return f(current_user, *args, **kwargs)
    return decorated


# ============ 注册相关接口 ============

@app.route('/api/send-code', methods=['POST'])
def send_verification_code():
    """发送验证码到邮箱"""
    data = request.get_json()
    email = data.get('email')

    if not email:
        return jsonify({'message': '邮箱不能为空'}), 400

    # 验证邮箱格式
    import re
    if not re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', email):
        return jsonify({'message': '邮箱格式不正确'}), 400

    # 检查邮箱是否已注册
    if User.query.filter_by(username=email).first():
        return jsonify({'message': '该邮箱已被注册'}), 400

    # 生成验证码
    code = generate_code(6)

    # 存储验证码，设置5分钟过期
    verification_codes[email] = {
        'code': code,
        'expires': datetime.utcnow() + timedelta(minutes=5)
    }

    # 发送邮件
    if send_verification_email(email, code):
        return jsonify({'message': '验证码已发送'}), 200
    else:
        return jsonify({'message': '发送失败，请稍后重试'}), 500


@app.route('/api/register', methods=['POST'])
def register():
    data = request.get_json()

    email = data.get('email')
    code = data.get('code')
    invite_code = data.get('inviteCode')
    password = data.get('password')
    name = data.get('name')

    # 验证必要字段
    if not email or not code or not invite_code or not password or not name:
        return jsonify({'message': '缺少必要字段'}), 400

    # 验证邮箱格式
    import re
    if not re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', email):
        return jsonify({'message': '邮箱格式不正确'}), 400

    # 验证验证码
    if email not in verification_codes:
        return jsonify({'message': '请先获取验证码'}), 400

    stored = verification_codes[email]
    if datetime.utcnow() > stored['expires']:
        del verification_codes[email]
        return jsonify({'message': '验证码已过期'}), 400

    if stored['code'] != code:
        return jsonify({'message': '验证码错误'}), 400

    # 验证邀请码
    if not check_invite_code(invite_code):
        return jsonify({'message': '邀请码无效'}), 400

    # 检查邮箱是否已注册
    if User.query.filter_by(username=email).first():
        return jsonify({'message': '该邮箱已被注册'}), 400

    # 验证名字长度
    if len(name) > 20:
        return jsonify({'message': '姓名必须20个字符以内'}), 400

    # 创建用户
    user = User(
        username=email,
        password_hash=generate_password_hash(password),
        name=name
    )

    db.session.add(user)
    db.session.commit()

    # 清除验证码
    del verification_codes[email]

    # 生成 token
    token = jwt.encode({
        'user_id': user.id,
        'exp': datetime.utcnow() + timedelta(days=7)
    }, app.config['SECRET_KEY'], algorithm='HS256')

    return jsonify({
        'message': '注册成功',
        'token': token,
        'user': user.to_dict()
    }), 201


# ============ 登录接口 ============

@app.route('/api/login', methods=['POST'])
def login():
    data = request.get_json()

    if not data or not data.get('username') or not data.get('password'):
        return jsonify({'message': 'Missing username or password'}), 400

    user = User.query.filter_by(username=data['username']).first()

    if not user or not check_password_hash(user.password_hash, data['password']):
        return jsonify({'message': 'Invalid username or password'}), 401

    token = jwt.encode({
        'user_id': user.id,
        'exp': datetime.utcnow() + timedelta(days=7)
    }, app.config['SECRET_KEY'], algorithm='HS256')

    return jsonify({
        'message': 'Login successful',
        'token': token,
        'user': user.to_dict()
    })


@app.route('/api/me', methods=['GET'])
@token_required
def get_current_user(current_user):
    return jsonify(current_user.to_dict())


# ============ 用户信息接口 ============

@app.route('/api/users', methods=['GET'])
def get_all_users():
    """获取所有用户列表（公开）"""
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)

    pagination = User.query.order_by(User.updated_at.desc()).paginate(
        page=page, per_page=per_page, error_out=False
    )

    users = [user.to_list_item() for user in pagination.items]

    return jsonify({
        'users': users,
        'total': pagination.total,
        'pages': pagination.pages,
        'current_page': page
    })


@app.route('/api/users/<user_id>', methods=['GET'])
def get_user(user_id):
    """获取单个用户详情（公开）"""
    user = db.session.get(User, user_id)
    if not user:
        return jsonify({'message': 'User not found'}), 404
    return jsonify(user.to_dict())


@app.route('/api/profile', methods=['PUT'])
@token_required
def update_profile(current_user):
    """更新当前用户信息"""
    # 刷新用户数据，确保获取最新内容
    db.session.refresh(current_user)

    data = request.get_json()

    if data.get('name'):
        if len(data['name']) > 20:
            return jsonify({'message': 'Name must be 20 characters or less'}), 400
        current_user.name = data['name']

    if data.get('school'):
        if len(data['school']) > 50:
            return jsonify({'message': 'School must be 50 characters or less'}), 400
        current_user.school = data['school']

    if data.get('job'):
        if len(data['job']) > 30:
            return jsonify({'message': 'Job must be 30 characters or less'}), 400
        current_user.job = data['job']

    if data.get('bio') is not None:
        if len(data['bio']) > 200:
            return jsonify({'message': 'Bio must be 200 characters or less'}), 400
        current_user.bio = data['bio']

    if data.get('skills') is not None:
        import json as json_module
        if len(data['skills']) > 10:
            return jsonify({'message': 'Maximum 10 skills allowed'}), 400
        for skill in data['skills']:
            if len(skill) > 10:
                return jsonify({'message': 'Each skill must be 10 characters or less'}), 400
        current_user.skills = json_module.dumps(data['skills'])

    if data.get('experience') is not None:
        import json as json_module
        current_user.experience = json_module.dumps(data['experience'])

    if data.get('hobbies') is not None:
        current_user.hobbies = data['hobbies']

    current_user.updated_at = datetime.utcnow()
    db.session.commit()

    return jsonify({
        'message': 'Profile updated successfully',
        'user': current_user.to_dict()
    })


@app.route('/api/avatar', methods=['POST'])
@token_required
def upload_avatar(current_user):
    """上传头像"""
    if 'avatar' not in request.files:
        return jsonify({'message': 'No file provided'}), 400

    file = request.files['avatar']

    if file.filename == '':
        return jsonify({'message': 'No file selected'}), 400

    if not allowed_file(file.filename):
        return jsonify({'message': 'Invalid file type. Allowed: JPG, PNG, GIF'}), 400

    # 生成唯一文件名
    ext = file.filename.rsplit('.', 1)[1].lower()
    filename = f"{current_user.id}_{datetime.now().timestamp()}.{ext}"
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)

    file.save(filepath)

    # 删除旧头像
    if current_user.avatar_url:
        old_path = os.path.join(app.config['UPLOAD_FOLDER'], current_user.avatar_url.split('/')[-1])
        if os.path.exists(old_path):
            os.remove(old_path)

    # 更新数据库
    current_user.avatar_url = f"/api/uploads/{filename}"
    db.session.commit()

    return jsonify({
        'message': 'Avatar uploaded successfully',
        'avatar_url': current_user.avatar_url
    })


@app.route('/api/uploads/<filename>')
def serve_upload(filename):
    """提供上传的文件"""
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)


@app.route('/api/messages/<user_id>', methods=['GET'])
@token_required
def get_conversation(current_user, user_id):
    """获取与指定用户的聊天记录"""
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 50, type=int)

    messages = Message.query.filter(
        ((Message.sender_id == current_user.id) & (Message.receiver_id == user_id)) |
        ((Message.sender_id == user_id) & (Message.receiver_id == current_user.id))
    ).order_by(Message.created_at.asc()).paginate(
        page=page, per_page=per_page, error_out=False
    )

    Message.query.filter(
        (Message.sender_id == user_id) &
        (Message.receiver_id == current_user.id) &
        (Message.status != 'read')
    ).update({'status': 'read', 'read_at': datetime.utcnow()})
    db.session.commit()

    return jsonify({
        'messages': [msg.to_dict() for msg in messages.items],
        'total': messages.total,
        'pages': messages.pages,
        'current_page': page
    })


@app.route('/api/messages', methods=['GET'])
@token_required
def get_conversation_list(current_user):
    """获取会话列表（与每个用户的最后一条消息）"""
    from sqlalchemy import or_, func

    subquery = db.session.query(
        Message.receiver_id.label('partner_id'),
        func.max(Message.created_at).label('last_time')
    ).filter(Message.sender_id == current_user.id).group_by(Message.receiver_id).union(
        db.session.query(
            Message.sender_id.label('partner_id'),
            func.max(Message.created_at).label('last_time')
        ).filter(Message.receiver_id == current_user.id).group_by(Message.sender_id)
    ).subquery()

    conversations = db.session.query(User, subquery.c.last_time).join(
        subquery, User.id == subquery.c.partner_id
    ).order_by(subquery.c.last_time.desc()).all()

    result = []
    for user, last_time in conversations:
        last_msg = Message.query.filter(
            or_(
                (Message.sender_id == current_user.id) & (Message.receiver_id == user.id),
                (Message.sender_id == user.id) & (Message.receiver_id == current_user.id)
            )
        ).order_by(Message.created_at.desc()).first()

        unread_count = Message.query.filter(
            (Message.sender_id == user.id) &
            (Message.receiver_id == current_user.id) &
            (Message.status != 'read')
        ).count()

        result.append({
            'partner': user.to_list_item(),
            'last_message': last_msg.to_dict() if last_msg else None,
            'last_time': last_time.isoformat() if last_time else None,
            'unread_count': unread_count
        })

    return jsonify({'conversations': result})


@app.route('/api/messages', methods=['POST'])
@token_required
def send_message(current_user):
    """发送私信"""
    data = request.get_json()
    receiver_id = data.get('receiver_id')
    content = data.get('content')

    if not receiver_id or not content:
        return jsonify({'message': 'Missing receiver_id or content'}), 400

    receiver = db.session.get(User, receiver_id)
    if not receiver:
        return jsonify({'message': 'Receiver not found'}), 404

    if len(content) > 1000:
        return jsonify({'message': 'Message too long (max 1000 characters)'}), 400

    message = Message(
        sender_id=current_user.id,
        receiver_id=receiver_id,
        content=content,
        status='sent'
    )

    db.session.add(message)
    db.session.commit()

    return jsonify({
        'message': 'Message sent',
        'msg': message.to_dict()
    }), 201


@app.route('/api/messages/<message_id>/status', methods=['PUT'])
@token_required
def update_message_status(current_user, message_id):
    """更新消息状态（送达/已读）"""
    data = request.get_json()
    status = data.get('status')

    if status not in ['delivered', 'read']:
        return jsonify({'message': 'Invalid status'}), 400

    message = db.session.get(Message, message_id)
    if not message:
        return jsonify({'message': 'Message not found'}), 404

    if message.receiver_id != current_user.id:
        return jsonify({'message': 'Unauthorized'}), 403

    message.status = status
    if status == 'read':
        message.read_at = datetime.utcnow()

    db.session.commit()

    return jsonify({'message': 'Status updated', 'msg': message.to_dict()})


@app.route('/api/messages/unread', methods=['GET'])
@token_required
def get_unread_count(current_user):
    """获取未读消息数量"""
    count = Message.query.filter(
        (Message.receiver_id == current_user.id) &
        (Message.status != 'read')
    ).count()

    return jsonify({'unread_count': count})


# ============ 忘记密码接口 ============

@app.route('/api/reset-password/send-code', methods=['POST'])
def send_reset_password_code():
    """发送密码重置验证码"""
    data = request.get_json()
    email = data.get('email')
    invite_code = data.get('invite_code')

    if not email or not invite_code:
        return jsonify({'message': '邮箱和邀请码不能为空'}), 400

    import re
    if not re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', email):
        return jsonify({'message': '邮箱格式不正确'}), 400

    user = User.query.filter_by(username=email).first()
    if not user:
        return jsonify({'message': '该邮箱未注册'}), 400

    if not check_invite_code(invite_code):
        return jsonify({'message': '邀请码无效'}), 400

    code = generate_code(6)
    reset_password_codes[email] = {
        'code': code,
        'expires': datetime.utcnow() + timedelta(minutes=5)
    }

    try:
        msg = MIMEText(f'您的密码重置验证码是：{code}，5分钟内有效。', 'plain', 'utf-8')
        msg['Subject'] = '密码重置验证码'
        msg['From'] = app.config['MAIL_DEFAULT_SENDER']
        msg['To'] = email

        server = smtplib.SMTP(app.config['MAIL_SERVER'], app.config['MAIL_PORT'])
        server.starttls()
        server.login(app.config['MAIL_USERNAME'], app.config['MAIL_PASSWORD'])
        server.sendmail(app.config['MAIL_DEFAULT_SENDER'], email, msg.as_string())
        server.quit()
        return jsonify({'message': '验证码已发送'}), 200
    except Exception as e:
        print(f"发送邮件失败: {e}")
        return jsonify({'message': '发送失败，请稍后重试'}), 500


@app.route('/api/reset-password', methods=['POST'])
def reset_password():
    """重置密码"""
    data = request.get_json()
    email = data.get('email')
    code = data.get('code')
    new_password = data.get('new_password')
    confirm_password = data.get('confirm_password')

    if not email or not code or not new_password or not confirm_password:
        return jsonify({'message': '所有字段都不能为空'}), 400

    if new_password != confirm_password:
        return jsonify({'message': '两次输入的密码不一致'}), 400

    if len(new_password) < 6:
        return jsonify({'message': '密码长度至少6位'}), 400

    if not re.match(r'^(?=.*[a-zA-Z])(?=.*\d)[a-zA-Z\d@$!%*?&]{6,20}$', new_password):
        return jsonify({'message': '密码必须包含字母和数字'}), 400

    if email not in reset_password_codes:
        return jsonify({'message': '请先获取验证码'}), 400

    stored = reset_password_codes[email]
    if datetime.utcnow() > stored['expires']:
        del reset_password_codes[email]
        return jsonify({'message': '验证码已过期'}), 400

    if stored['code'] != code:
        return jsonify({'message': '验证码错误'}), 400

    user = User.query.filter_by(username=email).first()
    if not user:
        return jsonify({'message': '用户不存在'}), 404

    user.password_hash = generate_password_hash(new_password)
    db.session.commit()

    del reset_password_codes[email]

    return jsonify({'message': '密码重置成功'}), 200


# ============ 管理员接口 ============

@app.route('/api/admin/users', methods=['GET'])
@token_required
@admin_required
def get_all_users_admin(current_user):
    """获取所有用户列表（管理员专用）"""
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 50, type=int)

    pagination = User.query.order_by(User.created_at.desc()).paginate(
        page=page, per_page=per_page, error_out=False
    )

    users = [user.to_dict() for user in pagination.items]

    return jsonify({
        'users': users,
        'total': pagination.total,
        'pages': pagination.pages,
        'current_page': page
    })


@app.route('/api/admin/users/<user_id>', methods=['DELETE'])
@token_required
@admin_required
def delete_user_admin(current_user, user_id):
    """删除指定用户（管理员专用）"""
    user = db.session.get(User, user_id)
    if not user:
        return jsonify({'message': 'User not found'}), 404

    # 不能删除自己
    if user.id == current_user.id:
        return jsonify({'message': 'Cannot delete yourself'}), 400

    # 删除关联的消息
    Message.query.filter(
        (Message.sender_id == user.id) | (Message.receiver_id == user.id)
    ).delete()

    db.session.delete(user)
    db.session.commit()

    return jsonify({'message': 'User deleted successfully'})


@app.route('/api/admin/users/<user_id>', methods=['PUT'])
@token_required
@admin_required
def update_user_admin(current_user, user_id):
    """编辑指定用户信息（管理员专用）"""
    user = db.session.get(User, user_id)
    if not user:
        return jsonify({'message': 'User not found'}), 404

    data = request.get_json()

    if data.get('name'):
        if len(data['name']) > 20:
            return jsonify({'message': 'Name must be 20 characters or less'}), 400
        user.name = data['name']

    if data.get('school'):
        if len(data['school']) > 50:
            return jsonify({'message': 'School must be 50 characters or less'}), 400
        user.school = data['school']

    if data.get('job'):
        if len(data['job']) > 30:
            return jsonify({'message': 'Job must be 30 characters or less'}), 400
        user.job = data['job']

    if data.get('bio') is not None:
        if len(data['bio']) > 200:
            return jsonify({'message': 'Bio must be 200 characters or less'}), 400
        user.bio = data['bio']

    if data.get('skills') is not None:
        import json as json_module
        if len(data['skills']) > 10:
            return jsonify({'message': 'Maximum 10 skills allowed'}), 400
        for skill in data['skills']:
            if len(skill) > 10:
                return jsonify({'message': 'Each skill must be 10 characters or less'}), 400
        user.skills = json_module.dumps(data['skills'])

    if data.get('experience') is not None:
        import json as json_module
        user.experience = json_module.dumps(data['experience'])

    if data.get('hobbies') is not None:
        user.hobbies = data['hobbies']

    user.updated_at = datetime.utcnow()
    db.session.commit()

    return jsonify({
        'message': 'User updated successfully',
        'user': user.to_dict()
    })


if __name__ == '__main__':
    app.run(debug=True, port=5000)
