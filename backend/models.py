from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import uuid

db = SQLAlchemy()


class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    username = db.Column(db.String(50), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    name = db.Column(db.String(20), nullable=False)
    avatar_url = db.Column(db.String(500), nullable=True)
    school = db.Column(db.String(50), nullable=True)
    job = db.Column(db.String(30), nullable=True)
    bio = db.Column(db.Text, nullable=True)
    skills = db.Column(db.Text, nullable=True)  # JSON 存储
    experience = db.Column(db.Text, nullable=True)  # JSON 存储
    hobbies = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    is_admin = db.Column(db.Boolean, default=False, nullable=False)

    def to_dict(self):
        import json
        return {
            'id': self.id,
            'username': self.username,
            'name': self.name,
            'avatar_url': self.avatar_url,
            'school': self.school,
            'job': self.job,
            'bio': self.bio,
            'skills': json.loads(self.skills) if self.skills else [],
            'experience': json.loads(self.experience) if self.experience else [],
            'hobbies': self.hobbies,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'is_admin': self.is_admin
        }

    def to_list_item(self):
        """列表页展示用的简化数据"""
        return {
            'id': self.id,
            'name': self.name,
            'avatar_url': self.avatar_url,
            'job': self.job,
            'school': self.school,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }


class Message(db.Model):
    __tablename__ = 'messages'

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    sender_id = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=False)
    receiver_id = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=False)
    content = db.Column(db.Text, nullable=False)
    status = db.Column(db.String(20), default='sent')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    read_at = db.Column(db.DateTime, nullable=True)

    sender = db.relationship('User', foreign_keys=[sender_id], backref='sent_messages')
    receiver = db.relationship('User', foreign_keys=[receiver_id], backref='received_messages')

    def to_dict(self):
        return {
            'id': self.id,
            'sender_id': self.sender_id,
            'receiver_id': self.receiver_id,
            'content': self.content,
            'status': self.status,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'read_at': self.read_at.isoformat() if self.read_at else None,
            'sender': self.sender.to_list_item() if self.sender else None,
            'receiver': self.receiver.to_list_item() if self.receiver else None
        }
