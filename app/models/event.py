from datetime import datetime
from app.models import db

class Event(db.Model):
    """
    校園活動模型
    """
    __tablename__ = 'events'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    title = db.Column(db.String(150), nullable=False)
    category = db.Column(db.String(50), nullable=False)  # 'lecture', 'club', 'competition', 'job', 'announcement'
    start_time = db.Column(db.DateTime, nullable=False)
    end_time = db.Column(db.DateTime, nullable=False)
    location = db.Column(db.String(150), nullable=False)
    description = db.Column(db.Text, nullable=True)
    registration_link = db.Column(db.String(255), nullable=True)
    contact_info = db.Column(db.String(150), nullable=True)
    organizer_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # === CRUD 與查詢輔助方法 ===

    @classmethod
    def create(cls, title, category, start_time, end_time, location, description, registration_link, contact_info, organizer_id):
        """
        發布新活動
        """
        event = cls(
            title=title,
            category=category,
            start_time=start_time,
            end_time=end_time,
            location=location,
            description=description,
            registration_link=registration_link,
            contact_info=contact_info,
            organizer_id=organizer_id
        )
        db.session.add(event)
        db.session.commit()
        return event

    @classmethod
    def get_by_id(cls, event_id):
        """
        依 ID 查詢單一活動詳情
        """
        return cls.query.get(event_id)

    @classmethod
    def get_all(cls, category=None, search_query=None):
        """
        取得所有活動列表，支援分類篩選與關鍵字搜尋
        """
        query = cls.query
        
        # 分類篩選
        if category:
            query = query.filter(cls.category == category)
            
        # 關鍵字搜尋 (標題、描述、地點)
        if search_query:
            query = query.filter(
                (cls.title.like(f"%{search_query}%")) |
                (cls.description.like(f"%{search_query}%")) |
                (cls.location.like(f"%{search_query}%"))
            )
            
        # 依建立時間排序 (由新到舊)
        return query.order_by(cls.created_at.desc()).all()

    @classmethod
    def get_by_organizer(cls, organizer_id):
        """
        查詢特定主辦單位發布的所有活動
        """
        return cls.query.filter_by(organizer_id=organizer_id).order_by(cls.created_at.desc()).all()

    def update(self, **kwargs):
        """
        更新活動欄位資訊
        """
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)
        db.session.commit()
        return self

    def delete(self):
        """
        刪除活動 (下架)
        """
        db.session.delete(self)
        db.session.commit()

    @property
    def status(self):
        """
        動態判定活動狀態 ('upcoming' 未開始, 'ongoing' 進行中, 'ended' 已結束)
        """
        now = datetime.utcnow()
        if now < self.start_time:
            return 'upcoming'
        elif self.start_time <= now <= self.end_time:
            return 'ongoing'
        else:
            return 'ended'

    def __repr__(self):
        return f"<Event {self.title} (Category: {self.category})>"
