from flask import Blueprint, request, render_template, redirect, url_for, session, flash, abort
from app.models import db, Event, Category, Bookmark, User
from app.utils.sms import notify_users_of_new_event
from datetime import datetime

events_bp = Blueprint('events', __name__, url_prefix='/events')

@events_bp.route('/')
def list_events():
    """
    處理活動列表請求 (支援分類篩選)
    """
    category_id = request.args.get('category', type=int)
    categories = Category.query.all()
    
    if category_id:
        selected_category = Category.query.get_or_404(category_id)
        events = Event.query.filter_by(category_id=category_id).order_by(Event.event_date.asc()).all()
    else:
        selected_category = None
        events = Event.query.order_by(Event.event_date.asc()).all()
        
    return render_template('events/list.html', events=events, categories=categories, selected_category=selected_category)

@events_bp.route('/search')
def search_events():
    """
    處理活動搜尋請求
    """
    query = request.args.get('q', '')
    categories = Category.query.all()
    
    if query:
        events = Event.query.filter(
            (Event.title.like(f'%{query}%')) | 
            (Event.description.like(f'%{query}%'))
        ).order_by(Event.event_date.asc()).all()
    else:
        events = []
        
    return render_template('events/list.html', events=events, categories=categories, query=query)

@events_bp.route('/<int:id>')
def event_detail(id):
    """
    處理單一活動詳細資訊請求
    """
    event = Event.query.get_or_404(id)
    
    # 檢查目前使用者是否已收藏此活動
    is_bookmarked = False
    if 'user_id' in session:
        bookmark = Bookmark.query.filter_by(user_id=session['user_id'], event_id=id).first()
        is_bookmarked = bookmark is not None
        
    return render_template('events/detail.html', event=event, is_bookmarked=is_bookmarked)

@events_bp.route('/new', methods=['GET', 'POST'])
def create_event():
    """
    處理新增活動
    """
    # 驗證是否登入，且角色為主辦單位
    if 'user_id' not in session:
        flash('請先登入帳號！', 'warning')
        return redirect(url_for('auth.login'))
        
    if session.get('role') != 'organizer':
        flash('只有活動主辦單位有權限發布活動！', 'danger')
        return redirect(url_for('main.index'))
        
    categories = Category.query.all()
    
    if request.method == 'POST':
        title = request.form.get('title')
        description = request.form.get('description')
        event_date_str = request.form.get('event_date')
        location = request.form.get('location')
        category_id = request.form.get('category_id', type=int)
        
        if not title or not description or not event_date_str or not location or not category_id:
            flash('所有欄位皆為必填！', 'danger')
            return render_template('events/form.html', categories=categories, action='new')
            
        try:
            # 解析日期，HTML datetime-local 格式為 'YYYY-MM-DDTHH:MM'
            event_date = datetime.strptime(event_date_str, '%Y-%m-%dT%H:%M')
            
            # 建立活動
            new_event = Event(
                title=title,
                description=description,
                event_date=event_date,
                location=location,
                organizer_id=session['user_id'],
                category_id=category_id
            )
            db.session.add(new_event)
            db.session.commit()
            
            # 實作最新活動簡訊通知
            try:
                sms_count = notify_users_of_new_event(new_event)
                if sms_count > 0:
                    flash(f'活動發布成功！已發送簡訊通知 {sms_count} 位訂閱使用者。', 'success')
                else:
                    flash('活動發布成功！', 'success')
            except Exception as sms_err:
                # 簡訊發送失敗不應阻礙活動發布成功
                flash(f'活動發布成功！(但簡訊發送失敗：{str(sms_err)})', 'warning')
            
            return redirect(url_for('events.event_detail', id=new_event.id))
        except Exception as e:
            db.session.rollback()
            flash(f'發布失敗，請重試。錯誤資訊：{str(e)}', 'danger')
            return render_template('events/form.html', categories=categories, action='new')
            
    return render_template('events/form.html', categories=categories, action='new')

@events_bp.route('/<int:id>/edit', methods=['GET', 'POST'])
def edit_event(id):
    """
    處理編輯活動
    """
    if 'user_id' not in session:
        flash('請先登入帳號！', 'warning')
        return redirect(url_for('auth.login'))
        
    event = Event.query.get_or_404(id)
    
    # 驗證是否為該活動的發布者
    if event.organizer_id != session['user_id']:
        flash('您無權編輯他人發布的活動！', 'danger')
        return redirect(url_for('events.event_detail', id=id))
        
    categories = Category.query.all()
    
    if request.method == 'POST':
        title = request.form.get('title')
        description = request.form.get('description')
        event_date_str = request.form.get('event_date')
        location = request.form.get('location')
        category_id = request.form.get('category_id', type=int)
        
        if not title or not description or not event_date_str or not location or not category_id:
            flash('所有欄位皆為必填！', 'danger')
            return render_template('events/form.html', event=event, categories=categories, action='edit')
            
        try:
            event.title = title
            event.description = description
            event.event_date = datetime.strptime(event_date_str, '%Y-%m-%dT%H:%M')
            event.location = location
            event.category_id = category_id
            
            db.session.commit()
            flash('活動修改成功！', 'success')
            return redirect(url_for('events.event_detail', id=id))
        except Exception as e:
            db.session.rollback()
            flash(f'修改失敗，請重試。錯誤資訊：{str(e)}', 'danger')
            return render_template('events/form.html', event=event, categories=categories, action='edit')
            
    return render_template('events/form.html', event=event, categories=categories, action='edit')

@events_bp.route('/<int:id>/delete', methods=['POST'])
def delete_event(id):
    """
    處理刪除活動
    """
    if 'user_id' not in session:
        flash('請先登入帳號！', 'warning')
        return redirect(url_for('auth.login'))
        
    event = Event.query.get_or_404(id)
    
    # 驗證是否為發布者
    if event.organizer_id != session['user_id']:
        flash('您無權刪除他人發布的活動！', 'danger')
        return redirect(url_for('events.event_detail', id=id))
        
    try:
        db.session.delete(event)
        db.session.commit()
        flash('活動已成功刪除。', 'success')
        return redirect(url_for('main.index'))
    except Exception as e:
        db.session.rollback()
        flash(f'刪除失敗：{str(e)}', 'danger')
        return redirect(url_for('events.event_detail', id=id))

@events_bp.route('/<int:id>/bookmark', methods=['POST'])
def toggle_bookmark(id):
    """
    學生收藏與取消收藏活動
    """
    if 'user_id' not in session:
        flash('請先登入帳號以收藏活動！', 'warning')
        return redirect(url_for('auth.login'))
        
    event = Event.query.get_or_404(id)
    user_id = session['user_id']
    
    bookmark = Bookmark.query.filter_by(user_id=user_id, event_id=id).first()
    
    try:
        if bookmark:
            db.session.delete(bookmark)
            db.session.commit()
            flash('已將此活動移出您的收藏清單！', 'info')
        else:
            new_bookmark = Bookmark(user_id=user_id, event_id=id)
            db.session.add(new_bookmark)
            db.session.commit()
            flash('活動已成功加入收藏！', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'收藏操作失敗：{str(e)}', 'danger')
        
    return redirect(url_for('events.event_detail', id=id))

