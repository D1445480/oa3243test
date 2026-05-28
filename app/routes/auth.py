import logging
from flask import Blueprint, render_template, redirect, url_for, request, flash, session
from flask_login import login_user, logout_user, login_required, current_user
from app.models import db, User

# 設定 logger
logger = logging.getLogger(__name__)

auth_bp = Blueprint('auth', __name__, url_prefix='/auth')

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    """
    [GET] 顯示註冊頁面 (templates/register.html)
    [POST] 處理使用者註冊，支援手機與簡訊訂閱欄位
    """
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))

    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '')
        role = request.form.get('role', 'student')
        phone = request.form.get('phone', '').strip()
        receive_sms = True if request.form.get('receive_sms') else False

        # 欄位驗證
        if not username or not email or not password:
            flash('請填寫所有必填欄位！', 'danger')
            return render_template('register.html')

        try:
            # 檢查重複註冊
            if User.get_by_username(username):
                flash('此帳號已被註冊！', 'danger')
                return render_template('register.html')

            if User.get_by_email(email):
                flash('此 Email 已被註冊！', 'danger')
                return render_template('register.html')

            # 建立使用者
            User.create(
                username=username,
                email=email,
                password=password,
                role=role,
                phone=phone if phone else None,
                receive_sms=receive_sms
            )
            flash('註冊成功！請登入您的帳號。', 'success')
            return redirect(url_for('auth.login'))
        except Exception as e:
            db.session.rollback()
            logger.error(f"註冊出錯: {str(e)}")
            flash('系統錯誤，註冊失敗。請稍後再試。', 'danger')
            return render_template('register.html')

    return render_template('register.html')


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """
    [GET] 顯示登入頁面 (templates/login.html)
    [POST] 驗證登入，並同步寫入 Flask-Login 與傳統 Session 以利與組員相容
    """
    if current_user.is_authenticated:
        if current_user.role == 'organizer':
            return redirect(url_for('event.manage'))
        return redirect(url_for('main.index'))

    if request.method == 'POST':
        # 兼容帳密：組員表單可能使用 email，我們表單可能使用 username
        username = request.form.get('username', '').strip()
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '')

        identifier = username or email
        if not identifier or not password:
            flash('請輸入帳號或電子郵件與密碼。', 'danger')
            return render_template('login.html')

        try:
            # 支援以 username 或 email 登入
            user = User.query.filter((User.username == identifier) | (User.email == identifier)).first()
            if not user or not user.check_password(password):
                flash('帳號或密碼錯誤，請重試！', 'danger')
                return render_template('login.html')

            # 建立 Flask-Login 的 Session
            login_user(user)
            
            # 同步寫入 session dict，使組員(d1445480)的 events.py 能無縫讀取身份
            session['user_id'] = user.id
            session['username'] = user.username
            session['role'] = user.role
            
            flash(f'歡迎回來，{user.username}！', 'success')
            
            if user.role == 'organizer':
                return redirect(url_for('event.manage'))
            return redirect(url_for('main.index'))
        except Exception as e:
            logger.error(f"登入出錯: {str(e)}")
            flash('登入過程中發生系統錯誤，請稍後再試。', 'danger')
            return render_template('login.html')

    return render_template('login.html')


@auth_bp.route('/logout', methods=['GET', 'POST'])
def logout():
    """
    [GET/POST] 登出邏輯，同時清除 Flask-Login 與 Session dict
    """
    try:
        logout_user()
        session.clear()
        flash('您已成功登出。', 'success')
    except Exception as e:
        logger.error(f"登出出錯: {str(e)}")
        flash('登出失敗。', 'danger')
    return redirect(url_for('main.index'))
