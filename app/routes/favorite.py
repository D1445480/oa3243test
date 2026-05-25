from flask import Blueprint, render_template, jsonify, login_required, current_user
from app.models.favorite import Favorite
from app.models.event import Event

favorite_bp = Blueprint('favorite', __name__)

@favorite_bp.route('/toggle/<int:event_id>', methods=['POST'])
@login_required
def toggle_favorite(event_id):
    """
    [POST] AJAX 接口：切換特定活動的收藏狀態 (登入學生專用)
    
    處理邏輯：
    1. 驗證目前使用者角色是否為 'student'，若非則回傳 JSON 錯誤 (如 {status: "error", message: "Only students can favorite events"})。
    2. 檢查 event_id 對應的活動是否存在，若不存在回傳 404。
    3. 呼叫 Favorite.toggle(current_user.id, event_id)。
    4. 回傳 JSON 格式結果，例如：
       - 收藏成功：{status: "success", action: "favorited", message: "已加入收藏"}
       - 取消收藏：{status: "success", action: "unfavorited", message: "已取消收藏"}
    """
    pass

@favorite_bp.route('/my-favorites')
@login_required
def my_favorites():
    """
    [GET] 顯示當前學生帳號已收藏的活動清單頁面 (templates/favorite_list.html)
    
    處理邏輯：
    1. 驗證目前使用者角色是否為 'student'，若非則重導向或顯示 403。
    2. 呼叫 Favorite.get_by_user(current_user.id) 取得收藏的活動列表。
    3. 渲染 favorite_list.html，並帶入活動列表。
    """
    pass
