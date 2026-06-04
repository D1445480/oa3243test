import logging
from datetime import datetime
from flask import Blueprint, render_template, redirect, url_for, request, flash, abort
from flask_login import login_required, current_user
from app.models import db, Category
from app.models.event import Event

# 設定 logger
logger = logging.getLogger(__name__)

event_bp = Blueprint('event', __name__)

@event_bp.route('/publish', methods=['GET', 'POST'])
@login_required
def publish():
    """
    [GET] 顯示發布活動表單頁面 (templates/event_publish.html)
    [POST] 接收表單欄位並發布新活動 (限活動主辦單位)
    """
    # 權限驗證
    if current_user.role != 'organizer':
        flash('只有活動主辦單位可以發布與管理活動。', 'danger')
        return redirect(url_for('main.index'))

    if request.method == 'POST':
        title = request.form.get('title', '').strip()
        category = request.form.get('category', '').strip()
        start_time_str = request.form.get('start_time', '').strip()
        end_time_str = request.form.get('end_time', '').strip()
        location = request.form.get('location', '').strip()
        description = request.form.get('description', '').strip()
        registration_link = request.form.get('registration_link', '').strip()
        contact_info = request.form.get('contact_info', '').strip()

        # 欄位必填驗證
        if not title or not category or not start_time_str or not end_time_str or not location:
            flash('請填寫所有必填欄位 (名稱、類別、開始/結束時間、地點)。', 'danger')
            return render_template('event_publish.html', event=request.form), 400

        try:
            # 轉換時間格式 (格式通常為 HTML datetime-local 傳回的 YYYY-MM-DDTHH:MM)
            start_time = datetime.fromisoformat(start_time_str)
            end_time = datetime.fromisoformat(end_time_str)
            
            # 時間合理性驗證
            if start_time >= end_time:
                flash('活動結束時間必須晚於開始時間。', 'warning')
                return render_template('event_publish.html', event=request.form), 400

            # 從資料庫獲取或建立對應的分類實體 (對應英文分類欄位)
            mapping = {
                'lecture': '學術講座',
                'club': '社團活動',
                'competition': '運動競賽',
                'job': '工讀公告',
                'announcement': '系所通知'
            }
            chinese_name = mapping.get(category, '其他活動')
            cat = Category.query.filter_by(name=chinese_name).first()
            if not cat:
                cat = Category(name=chinese_name)
                db.session.add(cat)
                db.session.commit()
            category_id = cat.id

            # 建立活動
            event = Event.create(
                title=title,
                category_id=category_id,
                start_time=start_time,
                end_time=end_time,
                location=location,
                description=description or None,
                registration_link=registration_link or None,
                contact_info=contact_info or None,
                organizer_id=current_user.id
            )
            
            # 觸發最新活動簡訊通知
            try:
                from app.utils.sms import notify_users_of_new_event
                sms_count = notify_users_of_new_event(event)
                if sms_count > 0:
                    flash(f'活動發布成功！已發送簡訊通知 {sms_count} 位訂閱使用者。', 'success')
                else:
                    flash('活動發布成功！', 'success')
            except Exception as sms_err:
                logger.error(f"簡訊通知發送失敗: {str(sms_err)}")
                flash(f'活動發布成功！(但簡訊發送失敗：{str(sms_err)})', 'warning')

            return redirect(url_for('event.manage'))
        except ValueError as ve:
            logger.error(f"日期格式轉換出錯: {str(ve)}")
            flash('日期格式不正確，請使用正確的選擇器輸入。', 'danger')
            return render_template('event_publish.html', event=request.form), 400
        except Exception as e:
            logger.error(f"發布活動出錯: {str(e)}")
            flash('發布活動時發生系統錯誤，請稍後再試。', 'danger')
            return render_template('event_publish.html', event=request.form), 500

    # GET 請求，顯示空白發布表單
    return render_template('event_publish.html', event=None)


@event_bp.route('/manage')
@login_required
def manage():
    """
    [GET] 主辦單位管理後台，列出該帳號發布的所有活動
    """
    if current_user.role != 'organizer':
        flash('只有活動主辦單位可以管理活動。', 'danger')
        return redirect(url_for('main.index'))

    try:
        events = Event.get_by_organizer(current_user.id)
        return render_template('event_manage.html', events=events)
    except Exception as e:
        logger.error(f"載入主辦管理頁出錯: {str(e)}")
        flash('讀取活動清單時發生系統錯誤。', 'danger')
        return redirect(url_for('main.index'))


@event_bp.route('/edit/<int:event_id>', methods=['GET', 'POST'])
@login_required
def edit(event_id):
    """
    [GET] 顯示編輯活動表單頁面 (templates/event_publish.html，複用表單)
    [POST] 處理修改活動資訊
    """
    if current_user.role != 'organizer':
        flash('只有活動主辦單位可以編輯活動。', 'danger')
        return redirect(url_for('main.index'))

    event = Event.get_by_id(event_id)
    if not event:
        abort(404)

    # 權限驗證：只能修改自己發布的活動
    if event.organizer_id != current_user.id:
        flash('您無權編輯此活動。', 'danger')
        return redirect(url_for('event.manage'))

    if request.method == 'POST':
        title = request.form.get('title', '').strip()
        category = request.form.get('category', '').strip()
        start_time_str = request.form.get('start_time', '').strip()
        end_time_str = request.form.get('end_time', '').strip()
        location = request.form.get('location', '').strip()
        description = request.form.get('description', '').strip()
        registration_link = request.form.get('registration_link', '').strip()
        contact_info = request.form.get('contact_info', '').strip()

        # 欄位必填驗證
        if not title or not category or not start_time_str or not end_time_str or not location:
            flash('請填寫所有必填欄位。', 'danger')
            return render_template('event_publish.html', event=event), 400

        try:
            start_time = datetime.fromisoformat(start_time_str)
            end_time = datetime.fromisoformat(end_time_str)
            
            if start_time >= end_time:
                flash('活動結束時間必須晚於開始時間。', 'warning')
                return render_template('event_publish.html', event=event), 400

            # 獲取或建立分類
            mapping = {
                'lecture': '學術講座',
                'club': '社團活動',
                'competition': '運動競賽',
                'job': '工讀公告',
                'announcement': '系所通知'
            }
            chinese_name = mapping.get(category, '其他活動')
            cat = Category.query.filter_by(name=chinese_name).first()
            if not cat:
                cat = Category(name=chinese_name)
                db.session.add(cat)
                db.session.commit()
            category_id = cat.id

            # 更新活動
            event.update(
                title=title,
                category_id=category_id,
                start_time=start_time,
                end_time=end_time,
                location=location,
                description=description or None,
                registration_link=registration_link or None,
                contact_info=contact_info or None
            )
            flash('活動修改成功！', 'success')
            return redirect(url_for('event.manage'))
        except ValueError as ve:
            logger.error(f"日期格式轉換出錯: {str(ve)}")
            flash('日期格式不正確，請使用正確的選擇器輸入。', 'danger')
            return render_template('event_publish.html', event=event), 400
        except Exception as e:
            logger.error(f"編輯活動出錯 (ID: {event_id}): {str(e)}")
            flash('更新活動時發生系統錯誤，請稍後再試。', 'danger')
            return render_template('event_publish.html', event=event), 500

    # GET 請求，顯示帶有活動內容的編輯表單
    return render_template('event_publish.html', event=event)


@event_bp.route('/delete/<int:event_id>', methods=['POST'])
@login_required
def delete(event_id):
    """
    [POST] 刪除指定活動
    """
    if current_user.role != 'organizer':
        flash('只有活動主辦單位可以刪除活動。', 'danger')
        return redirect(url_for('main.index'))

    event = Event.get_by_id(event_id)
    if not event:
        abort(404)

    # 權限驗證：只能刪除自己發布的活動
    if event.organizer_id != current_user.id:
        flash('您無權刪除此活動。', 'danger')
        return redirect(url_for('event.manage'))

    try:
        event.delete()
        flash('活動已成功刪除下架。', 'success')
    except Exception as e:
        logger.error(f"刪除活動出錯 (ID: {event_id}): {str(e)}")
        flash('刪除活動時發生系統錯誤，請稍後再試。', 'danger')
        
    return redirect(url_for('event.manage'))
