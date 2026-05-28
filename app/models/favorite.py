from datetime import datetime
import logging
from app.models import db

# 設定 logger
logger = logging.getLogger(__name__)

class Favorite(db.Model):
    """
    活動收藏關係模型 (學生與活動的多對多關聯表，對應 bookmarks 資料表)
    """
    __tablename__ = 'bookmarks'

    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), primary_key=True)
    event_id = db.Column(db.Integer, db.ForeignKey('events.id', ondelete='CASCADE'), primary_key=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # 設定關聯，使我們可以透過 Favorite 物件直接存取 User 與 Event 物件
    user = db.relationship('User', backref=db.backref('favorites_relation', lazy='dynamic', cascade="all, delete-orphan"))
    event = db.relationship('Event', backref=db.backref('favorited_by_relation', lazy='dynamic', cascade="all, delete-orphan"))

    # === CRUD 與狀態切換方法 ===

    @classmethod
    def toggle(cls, user_id, event_id):
        """
        切換收藏狀態：
        若該活動已收藏，則將其取消收藏；
        若未收藏，則將其加入收藏。
        回傳值為：('favorited' 或 'unfavorited')
        """
        try:
            existing_fav = cls.query.filter_by(user_id=user_id, event_id=event_id).first()
            
            if existing_fav:
                db.session.delete(existing_fav)
                db.session.commit()
                return 'unfavorited'
            else:
                new_fav = cls(user_id=user_id, event_id=event_id)
                db.session.add(new_fav)
                db.session.commit()
                return 'favorited'
        except Exception as e:
            db.session.rollback()
            logger.error(f"切換活動收藏狀態失敗 (User ID: {user_id}, Event ID: {event_id}): {str(e)}")
            raise e

    @classmethod
    def is_favorited(cls, user_id, event_id):
        """
        檢查特定使用者是否已收藏該活動
        """
        try:
            if not user_id:
                return False
            return cls.query.filter_by(user_id=user_id, event_id=event_id).first() is not None
        except Exception as e:
            logger.error(f"檢查收藏狀態失敗 (User ID: {user_id}, Event ID: {event_id}): {str(e)}")
            return False

    @classmethod
    def get_by_user(cls, user_id):
        """
        取得特定使用者收藏的所有活動 (Event 物件) 列表，依收藏時間降冪排序
        """
        try:
            relations = cls.query.filter_by(user_id=user_id).order_by(cls.created_at.desc()).all()
            # 回傳 Event 實例列表 (過濾掉已被刪除的活動以防出錯)
            return [rel.event for rel in relations if rel.event is not None]
        except Exception as e:
            logger.error(f"查詢使用者收藏清單失敗 (User ID: {user_id}): {str(e)}")
            return []

    def __repr__(self):
        return f"<Favorite User:{self.user_id} -> Event:{self.event_id}>"

# 建立 Bookmark 別名，使組員(d1445480)的簡訊與事件管理功能能無縫存取此模型
Bookmark = Favorite
