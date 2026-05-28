from datetime import datetime
import logging
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from app.models import db

# 設定 logger
logger = logging.getLogger(__name__)

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
    phone = db.Column(db.String(20), nullable=True)
    receive_sms = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # 關聯：一個主辦單位可以發布多個活動 (1對多)
    published_events = db.relationship('Event', backref='organizer', lazy=True, cascade="all, delete-orphan")

    def set_password(self, password):
        """加密並設定密碼"""
        self.password_hash = generate_password_hash(password, method='pbkdf2:sha256')

    def check_password(self, password):
        """檢查密碼是否正確"""
        return check_password_hash(self.password_hash, password)

    # === CRUD 輔助方法 ===

    @classmethod
    def create(cls, username, email, password, role, phone=None, receive_sms=False):
        """
        註冊新使用者，若發生資料庫錯誤則自動進行 Rollback
        """
        try:
            user = cls(
                username=username,
                email=email,
                role=role,
                phone=phone,
                receive_sms=receive_sms
            )
            user.set_password(password)
            db.session.add(user)
            db.session.commit()
            return user
        except Exception as e:
            db.session.rollback()
            logger.error(f"建立使用者失敗: {str(e)}")
            raise e

    @classmethod
    def get_by_id(cls, user_id):
        """
        依 ID 查詢使用者
        """
        try:
            return cls.query.get(int(user_id))
        except Exception as e:
            logger.error(f"依 ID 查詢使用者失敗 (ID: {user_id}): {str(e)}")
            return None

    @classmethod
    def get_by_username(cls, username):
        """
        依使用者名稱查詢使用者 (登入驗證時使用)
        """
        try:
            return cls.query.filter_by(username=username).first()
        except Exception as e:
            logger.error(f"依帳號查詢使用者失敗 (Username: {username}): {str(e)}")
            return None

    @classmethod
    def get_by_email(cls, email):
        """
        依 Email 查詢使用者
        """
        try:
            return cls.query.filter_by(email=email).first()
        except Exception as e:
            logger.error(f"依 Email 查詢使用者失敗 (Email: {email}): {str(e)}")
            return None

    @classmethod
    def get_all(cls):
        """
        取得所有使用者列表
        """
        try:
            return cls.query.all()
        except Exception as e:
            logger.error(f"查詢所有使用者失敗: {str(e)}")
            return []

    def update(self, **kwargs):
        """
        更新使用者資料，若失敗則進行 Rollback
        """
        try:
            for key, value in kwargs.items():
                if key == 'password':
                    self.set_password(value)
                elif hasattr(self, key):
                    setattr(self, key, value)
            db.session.commit()
            return self
        except Exception as e:
            db.session.rollback()
            logger.error(f"更新使用者資料失敗 (ID: {self.id}): {str(e)}")
            raise e

    def delete(self):
        """
        刪除使用者帳號，若失敗則進行 Rollback
        """
        try:
            db.session.delete(self)
            db.session.commit()
            return True
        except Exception as e:
            db.session.rollback()
            logger.error(f"刪除使用者失敗 (ID: {self.id}): {str(e)}")
            raise e

    def __repr__(self):
        return f"<User {self.username} ({self.role})>"
