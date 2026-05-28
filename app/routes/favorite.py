import logging
from flask import Blueprint, render_template, jsonify, redirect, url_for, flash
from flask_login import login_required, current_user
from app.models.favorite import Favorite
from app.models.event import Event

# 設定 logger
logger = logging.getLogger(__name__)

favorite_bp = Blueprint('favorite', __name__)

@favorite_bp.route('/toggle/<int:event_id>', methods=['POST'])
@login_required
def toggle_favorite(event_id):
    """
    [POST] AJAX 接口：切換特定活動的收藏狀態 (登入學生專用)
    
    處理邏輯：
    1. 驗證目前使用者角色是否為 'student'，若非則回傳 JSON 錯誤與 403 狀態碼。
    2. 檢查 event_id 對應的活動是否存在，若不存在則回傳 JSON 錯誤與 404 狀態碼。
    3. 呼叫 Favorite.toggle(current_user.id, event_id)。
    4. 回傳 JSON 格式結果，包含操作動作 (favorited/unfavorited) 與操作訊息。
    """
    # 1. 權限檢查：只有學生可以收藏活動
    if current_user.role != 'student':
        return jsonify({
            'status': 'error',
            'message': '只有學生帳號可以使用收藏功能。'
        }), 403

    # 2. 活動存在性檢查
    event = Event.get_by_id(event_id)
    if not event:
        return jsonify({
            'status': 'error',
            'message': '此活動不存在或已被刪除。'
        }), 404

    # 3. 切換收藏狀態
    try:
        action = Favorite.toggle(user_id=current_user.id, event_id=event_id)
        if action == 'favorited':
            return jsonify({
                'status': 'success',
                'action': 'favorited',
                'message': '已成功將活動加入收藏！'
            }), 200
        else:
            return jsonify({
                'status': 'success',
                'action': 'unfavorited',
                'message': '已取消收藏該活動。'
            }), 200
    except Exception as e:
        logger.error(f"切換收藏失敗 (User: {current_user.id}, Event: {event_id}): {str(e)}")
        return jsonify({
            'status': 'error',
            'message': '系統錯誤，請稍後再試。'
        }), 500


@favorite_bp.route('/my-favorites')
@login_required
def my_favorites():
    """
    [GET] 顯示當前學生帳號已收藏的活動清單頁面 (templates/favorite_list.html)
    
    處理邏輯：
    1. 驗證目前使用者角色是否為 'student'，若非則重導向至首頁並 Flash 錯誤。
    2. 呼叫 Favorite.get_by_user(current_user.id) 取得收藏的活動列表。
    3. 渲染 favorite_list.html，並帶入活動列表。
    """
    # 1. 權限檢查：只有一般學生能有收藏夾頁面
    if current_user.role != 'student':
        flash('只有一般學生可以檢視「我的收藏」頁面。', 'warning')
        return redirect(url_for('main.index'))

    # 2. 獲取收藏活動列表
    try:
        events = Favorite.get_by_user(user_id=current_user.id)
        return render_template('favorite_list.html', events=events)
    except Exception as e:
        logger.error(f"讀取使用者收藏列表失敗 (User: {current_user.id}): {str(e)}")
        flash('讀取收藏清單時發生錯誤，請稍後再試。', 'danger')
        return redirect(url_for('main.index'))
