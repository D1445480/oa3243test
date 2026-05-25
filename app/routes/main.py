from flask import Blueprint, render_template, request
from app.models.event import Event

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def index():
    """
    [GET] 首頁活動看板 (templates/index.html)
    
    處理邏輯：
    1. 接收查詢參數：category (分類篩選)、q (關鍵字搜尋)。
    2. 呼叫 Event.get_all(category, search_query) 取得篩選後的活動。
    3. 渲染 index.html，傳入活動清單與當前搜尋條件。
    """
    pass

@main_bp.route('/event/detail/<int:event_id>')
def event_detail(event_id):
    """
    [GET] 活動詳情頁面 (templates/event_detail.html)
    
    處理邏輯：
    1. 呼叫 Event.get_by_id(event_id) 查詢活動。
    2. 若活動不存在，回傳 404 錯誤頁面。
    3. 查詢目前登入使用者是否已收藏此活動，將 is_favorited 狀態傳給模板。
    4. 渲染 event_detail.html。
    """
    pass
