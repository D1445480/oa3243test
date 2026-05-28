from datetime import datetime, timedelta
import logging
from app.models import db
from app.models.category import Category

# 設定 logger
logger = logging.getLogger(__name__)

class Event(db.Model):
    """
    校園活動模型
    """
    __tablename__ = 'events'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    title = db.Column(db.String(150), nullable=False)
    description = db.Column(db.Text, nullable=True)
    start_time = db.Column(db.DateTime, nullable=False)
    end_time = db.Column(db.DateTime, nullable=False)
    location = db.Column(db.String(150), nullable=False)
    registration_link = db.Column(db.String(255), nullable=True)
    contact_info = db.Column(db.String(150), nullable=True)
    organizer_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    category_id = db.Column(db.Integer, db.ForeignKey('categories.id', ondelete='CASCADE'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # 關聯：指向分類
    category = db.relationship('Category', backref=db.backref('events_list', lazy=True))

    @property
    def event_date(self):
        """
        為與組員(d1445480)的簡訊發送與日誌功能保持相容，提供 event_date 作為 start_time 的讀寫屬性
        """
        return self.start_time

    @event_date.setter
    def event_date(self, value):
        self.start_time = value
        # 預設結束時間為開始時間後 2 小時
        if not self.end_time:
            self.end_time = value + timedelta(hours=2)

    # === CRUD 與查詢輔助方法 ===

    @classmethod
    def create(cls, title, category_id, start_time, end_time, location, description, registration_link, contact_info, organizer_id):
        """
        發布新活動，若發生資料庫錯誤則自動進行 Rollback
        """
        try:
            event = cls(
                title=title,
                category_id=category_id,
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
        except Exception as e:
            db.session.rollback()
            logger.error(f"建立活動失敗: {str(e)}")
            raise e

    @classmethod
    def get_by_id(cls, event_id):
        """
        依 ID 查詢單一活動詳情
        """
        try:
            return cls.query.get(event_id)
        except Exception as e:
            logger.error(f"查詢活動詳情失敗 (ID: {event_id}): {str(e)}")
            return None

    @classmethod
    def get_all(cls, category=None, search_query=None):
        """
        取得所有活動列表，支援分類篩選與關鍵字搜尋，依建立時間降冪排序。
        category 參數可以是英文識別碼 (如 'lecture') 或中文分類名稱。
        """
        try:
            query = cls.query
            
            # 分類篩選
            if category:
                # 建立英文到中文的轉換映射
                mapping = {
                    'lecture': '學術講座',
                    'club': '社團活動',
                    'competition': '運動競賽',
                    'job': '工讀公告',
                    'announcement': '系所通知'
                }
                chinese_name = mapping.get(category, category)  # 若傳入的就是中文，則直接使用
                query = query.join(Category).filter(Category.name == chinese_name)
                
            # 關鍵字搜尋 (標題、描述、地點)
            if search_query:
                query = query.filter(
                    (cls.title.like(f"%{search_query}%")) |
                    (cls.description.like(f"%{search_query}%")) |
                    (cls.location.like(f"%{search_query}%"))
                )
                
            return query.order_by(cls.created_at.desc()).all()
        except Exception as e:
            logger.error(f"查詢活動列表失敗: {str(e)}")
            return []

    @classmethod
    def get_by_organizer(cls, organizer_id):
        """
        查詢特定主辦單位發布的所有活動
        """
        try:
            return cls.query.filter_by(organizer_id=organizer_id).order_by(cls.created_at.desc()).all()
        except Exception as e:
            logger.error(f"查詢主辦單位活動失敗 (Organizer ID: {organizer_id}): {str(e)}")
            return []

    def update(self, **kwargs):
        """
        更新活動欄位資訊，若發生資料庫錯誤則自動進行 Rollback
        """
        try:
            for key, value in kwargs.items():
                if hasattr(self, key):
                    setattr(self, key, value)
            db.session.commit()
            return self
        except Exception as e:
            db.session.rollback()
            logger.error(f"更新活動失敗 (ID: {self.id}): {str(e)}")
            raise e

    def delete(self):
        """
        刪除活動 (下架)，若發生資料庫錯誤則自動進行 Rollback
        """
        try:
            db.session.delete(self)
            db.session.commit()
            return True
        except Exception as e:
            db.session.rollback()
            logger.error(f"刪除活動失敗 (ID: {self.id}): {str(e)}")
            raise e

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
        return f"<Event {self.title}>"
