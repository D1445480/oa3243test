from flask import Blueprint, render_template
from app.models import Event, Category
from datetime import datetime

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def index():
    """
    處理首頁請求
    """
    # 取得最新即將舉辦的 6 筆活動 (活動時間大於等於今天，依日期升序排序)
    upcoming_events = Event.query.filter(
        Event.event_date >= datetime.utcnow()
    ).order_by(Event.event_date.asc()).limit(6).all()
    
    # 取得所有分類供首頁導覽使用
    categories = Category.query.all()
    
    return render_template('index.html', events=upcoming_events, categories=categories)

