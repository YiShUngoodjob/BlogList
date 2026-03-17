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
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
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
