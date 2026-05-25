import logging
from flask import Blueprint, render_template, redirect, url_for, request, flash
from flask_login import login_user, logout_user, login_required, current_user
from app.models.user import User

# 設定 logger
logger = logging.getLogger(__name__)

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    """
    [GET] 顯示註冊表單頁面 (templates/register.html)
    [POST] 接收表單欄位，建立使用者帳號
    """
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))

    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '')
        role = request.form.get('role', 'student')

        # 欄位驗證
        if not username or not email or not password or not role:
            flash('所有欄位皆為必填。', 'danger')
            return render_template('register.html'), 400

        if role not in ['student', 'organizer']:
            flash('不合法的使用者角色。', 'danger')
            return render_template('register.html'), 400

        try:
            # 檢查帳號重複
            if User.get_by_username(username):
                flash('此帳號已被註冊。', 'warning')
                return render_template('register.html'), 400

            if User.get_by_email(email):
                flash('此 Email 已被註冊。', 'warning')
                return render_template('register.html'), 400

            # 建立使用者
            User.create(username=username, email=email, password=password, role=role)
            flash('註冊成功！請登入帳號。', 'success')
            return redirect(url_for('auth.login'))
        except Exception as e:
            logger.error(f"註冊出錯: {str(e)}")
            flash('系統錯誤，註冊失敗。請稍後再試。', 'danger')
            return render_template('register.html'), 500

    return render_template('register.html')


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """
    [GET] 顯示登入表單頁面 (templates/login.html)
    [POST] 驗證登入資訊並建立 Session
    """
    if current_user.is_authenticated:
        if current_user.role == 'organizer':
            return redirect(url_for('event.manage'))
        return redirect(url_for('main.index'))

    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')

        if not username or not password:
            flash('請輸入帳號與密碼。', 'danger')
            return render_template('login.html'), 400

        try:
            user = User.get_by_username(username)
            if not user or not user.check_password(password):
                flash('帳號或密碼錯誤。', 'danger')
                return render_template('login.html'), 401

            # 登入成功，建立 Session
            login_user(user)
            flash(f'登入成功，歡迎回來 {user.username}！', 'success')
            
            # 依角色導向不同頁面
            if user.role == 'organizer':
                return redirect(url_for('event.manage'))
            return redirect(url_for('main.index'))
        except Exception as e:
            logger.error(f"登入出錯: {str(e)}")
            flash('登入過程中發生系統錯誤，請稍後再試。', 'danger')
            return render_template('login.html'), 500

    return render_template('login.html')


@auth_bp.route('/logout', methods=['POST'])
@login_required
def logout():
    """
    [POST] 登出邏輯
    """
    try:
        logout_user()
        flash('您已成功登出。', 'success')
    except Exception as e:
        logger.error(f"登出出錯: {str(e)}")
        flash('登出失敗。', 'danger')
    return redirect(url_for('main.index'))
