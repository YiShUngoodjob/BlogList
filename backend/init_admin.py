import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import app, db
from models import User
from werkzeug.security import generate_password_hash

def create_admin():
    with app.app_context():
        # 检查数据库是否有 is_admin 列，如果没有则添加
        from sqlalchemy import inspect
        inspector = inspect(db.engine)
        columns = [col['name'] for col in inspector.get_columns('users')]

        if 'is_admin' not in columns:
            # 添加 is_admin 列到现有数据库
            db.session.execute(db.text('ALTER TABLE users ADD COLUMN is_admin BOOLEAN DEFAULT 0'))
            db.session.commit()
            print('已添加 is_admin 列到数据库')

        admin = User.query.filter_by(username='wysadmin@3300.com').first()
        if admin:
            if not admin.is_admin:
                admin.is_admin = True
                db.session.commit()
                print('已更新现有用户为管理员')
            else:
                print('管理员已存在')
            return

        admin = User(
            username='wysadmin@3300.com',
            password_hash=generate_password_hash('wysadmin3300'),
            name='管理员',
            is_admin=True
        )
        db.session.add(admin)
        db.session.commit()
        print('管理员账号创建成功')

if __name__ == '__main__':
    create_admin()
