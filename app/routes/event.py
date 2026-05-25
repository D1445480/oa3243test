from flask import Blueprint, render_template, redirect, url_for, request, flash
from flask_login import login_required, current_user
from app.models.event import Event

event_bp = Blueprint('event', __name__)

@event_bp.route('/publish', methods=['GET', 'POST'])
@login_required
def publish():
    """
    [GET] 顯示發布活動表單頁面 (templates/event_publish.html)
    [POST] 接收表單欄位：title, category, start_time, end_time, location, description, registration_link, contact_info
    
    處理邏輯：
    1. 驗證當前使用者角色是否為 'organizer'，若非則拒絕存取 (Redirect 或 403)。
    2. 接收並驗證表單欄位（開始時間不可晚於結束時間）。
    3. 呼叫 Event.create(...) 存入資料庫，並設定 organizer_id = current_user.id。
    4. 成功後重導向至活動管理後台 `/event/manage`。
    """
    pass

@event_bp.route('/manage')
@login_required
def manage():
    """
    [GET] 主辦單位管理後台 (templates/event_manage.html)
    
    處理邏輯：
    1. 驗證當前使用者角色是否為 'organizer'，若非則拒絕存取。
    2. 呼叫 Event.get_by_organizer(current_user.id) 取得該主辦發布的所有活動。
    3. 渲染 event_manage.html 並傳入活動列表。
    """
    pass

@event_bp.route('/edit/<int:event_id>', methods=['GET', 'POST'])
@login_required
def edit(event_id):
    """
    [GET] 顯示編輯活動表單頁面 (templates/event_publish.html，複用發布頁或專用編輯頁)
    [POST] 接收修改後的活動欄位資訊
    
    處理邏輯：
    1. 查詢活動是否存在，且 organizer_id 是否等於當前登入使用者的 id (防止越權修改)。
    2. 若驗證失敗或不是擁有者，回傳 403/404 或重導向。
    3. [POST] 接收表單變更並呼叫 event.update(...)。
    4. 成功後重導向至管理後台 `/event/manage`。
    """
    pass

@event_bp.route('/delete/<int:event_id>', methods=['POST'])
@login_required
def delete(event_id):
    """
    [POST] 刪除 (下架) 指定活動
    
    處理邏輯：
    1. 查詢活動是否存在，且 organizer_id 是否等於當前登入使用者的 id。
    2. 驗證為擁有者後，呼叫 event.delete()。
    3. 設定 flash 成功訊息，重導向至 `/event/manage`。
    """
    pass
