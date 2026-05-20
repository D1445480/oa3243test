from flask import Blueprint, request, render_template

events_bp = Blueprint('events', __name__, url_prefix='/events')

@events_bp.route('/')
def list_events():
    """
    處理活動列表請求 (支援分類篩選)
    
    輸入：URL Query Parameter `category` (選填)
    邏輯：
    1. 取得所有分類 (供篩選器使用)
    2. 若有 category 參數，則過濾活動
    3. 否則取得所有活動
    4. 渲染 events/list.html
    """
    pass

@events_bp.route('/search')
def search_events():
    """
    處理活動搜尋請求
    
    輸入：URL Query Parameter `q` (關鍵字)
    邏輯：
    1. 取得所有分類 (供篩選器使用)
    2. 根據關鍵字 (q) 模糊搜尋標題與內容
    3. 渲染 events/list.html
    """
    pass

@events_bp.route('/<int:id>')
def event_detail(id):
    """
    處理單一活動詳細資訊請求
    
    輸入：活動 ID
    邏輯：
    1. 透過 ID 取得 Event，若無則 404
    2. 渲染 events/detail.html
    """
    pass

@events_bp.route('/new', methods=['GET', 'POST'])
def create_event():
    """
    處理新增活動
    
    邏輯：
    1. GET: 回傳 events/form.html 供填寫
    2. POST: 驗證欄位，存入資料庫，並重導向至首頁或列表頁
    """
    pass

@events_bp.route('/<int:id>/edit', methods=['GET', 'POST'])
def edit_event(id):
    """
    處理編輯活動
    
    邏輯：
    1. 驗證權限與取得 Event
    2. GET: 回傳 events/form.html，並帶入預設資料
    3. POST: 更新欄位資料，存入資料庫，並重導向
    """
    pass

@events_bp.route('/<int:id>/delete', methods=['POST'])
def delete_event(id):
    """
    處理刪除活動
    
    邏輯：
    1. 驗證權限與取得 Event
    2. 從資料庫刪除
    3. 重導向至活動列表
    """
    pass
