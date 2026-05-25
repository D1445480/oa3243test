from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from app.models import db

class User(db.Model, UserMixin):
    """
    使用者模型 (支援一般學生與活動主辦單位)
    """
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    role = db.Column(db.String(20), nullable=False)  # 'student' 或 'organizer'
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # 關聯：一個主辦單位可以發布多個活動 (1對多)
    published_events = db.relationship('Event', backref='organizer', lazy=True, cascade="all, delete-orphan")

    def set_password(self, password):
        """加密並設定密碼"""
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        """檢查密碼是否正確"""
        return check_password_hash(self.password_hash, password)

    # === CRUD 輔助方法 ===

    @classmethod
    def create(cls, username, email, password, role):
        """
        註冊新使用者
        """
        user = cls(
            username=username,
            email=email,
            role=role
        )
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
        return user

    @classmethod
    def get_by_id(cls, user_id):
        """
        依 ID 查詢使用者
        """
        return cls.query.get(int(user_id))

    @classmethod
    def get_by_username(cls, username):
        """
        依使用者名稱查詢使用者 (登入驗證時使用)
        """
        return cls.query.filter_by(username=username).first()

    @classmethod
    def get_by_email(cls, email):
        """
        依 Email 查詢使用者
        """
        return cls.query.filter_by(email=email).first()

    @classmethod
    def get_all(cls):
        """
        取得所有使用者列表
        """
        return cls.query.all()

    def update(self, **kwargs):
        """
        更新使用者資料
        """
        for key, value in kwargs.items():
            if key == 'password':
                self.set_password(value)
            elif hasattr(self, key):
                setattr(self, key, value)
        db.session.commit()
        return self

    def delete(self):
        """
        刪除使用者帳號
        """
        db.session.delete(self)
        db.session.commit()

    def __repr__(self):
        return f"<User {self.username} ({self.role})>"
