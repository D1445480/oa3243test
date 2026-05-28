import logging
from flask import Blueprint, render_template, request, abort
from flask_login import current_user
from app.models import Category
from app.models.event import Event
from app.models.favorite import Favorite

# 設定 logger
logger = logging.getLogger(__name__)

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def index():
    """
    [GET] 首頁活動看板，顯示所有活動列表並支援分類篩選與關鍵字搜尋
    """
    category = request.args.get('category', '').strip()
    search_query = request.args.get('q', '').strip()

    try:
        # 獲取篩選後的活動清單
        events = Event.get_all(category=category or None, search_query=search_query or None)
        
        # 獲取所有資料庫分類，供首頁分類標籤渲染
        categories = Category.query.all()
        
        # 獲取目前學生的收藏清單，以利在卡片上渲染「紅心」
        fav_event_ids = set()
        if current_user.is_authenticated and current_user.role == 'student':
            fav_events = Favorite.get_by_user(current_user.id)
            fav_event_ids = {e.id for e in fav_events if e is not None}
            
        return render_template(
            'index.html', 
            events=events, 
            categories=categories,
            category=category, 
            search_query=search_query,
            fav_event_ids=fav_event_ids
        )
    except Exception as e:
        logger.error(f"載入首頁失敗: {str(e)}")
        return render_template('index.html', events=[], categories=[], category='', search_query='', fav_event_ids=set())


@main_bp.route('/event/detail/<int:event_id>')
def event_detail(event_id):
    """
    [GET] 顯示單一活動的詳細資訊頁面
    """
    try:
        event = Event.get_by_id(event_id)
        if not event:
            abort(404)

        # 判斷登入學生是否已收藏此活動
        is_favorited = False
        if current_user.is_authenticated and current_user.role == 'student':
            is_favorited = Favorite.is_favorited(current_user.id, event_id)

        return render_template('event_detail.html', event=event, is_favorited=is_favorited)
    except Exception as e:
        logger.error(f"載入活動詳情頁出錯 (ID: {event_id}): {str(e)}")
        abort(500)
