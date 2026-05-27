from flask import Blueprint, request, render_template, redirect, url_for, session, flash
from app.models import db, User

auth_bp = Blueprint('auth', __name__, url_prefix='/auth')

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    """
    處理使用者註冊
    """
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        role = request.form.get('role', 'student')
        phone = request.form.get('phone')
        receive_sms = True if request.form.get('receive_sms') else False

        if not username or not email or not password:
            flash('請填寫所有必填欄位！', 'danger')
            return render_template('auth/register.html')

        # 檢查 email 是否已註冊
        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            flash('此 Email 已被註冊！', 'danger')
            return render_template('auth/register.html')

        try:
            # 建立使用者
            new_user = User(
                username=username,
                email=email,
                role=role,
                phone=phone if phone else None,
                receive_sms=receive_sms
            )
            new_user.set_password(password)
            db.session.add(new_user)
            db.session.commit()
            
            flash('註冊成功！請登入您的帳號。', 'success')
            return redirect(url_for('auth.login'))
        except Exception as e:
            db.session.rollback()
            flash(f'註冊失敗，請重試。錯誤資訊：{str(e)}', 'danger')
            return render_template('auth/register.html')

    return render_template('auth/register.html')

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """
    處理使用者登入
    """
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')

        if not email or not password:
            flash('請填寫 Email 與密碼！', 'danger')
            return render_template('auth/login.html')

        user = User.query.filter_by(email=email).first()
        if user and user.check_password(password):
            # 寫入 Session
            session['user_id'] = user.id
            session['username'] = user.username
            session['role'] = user.role
            flash(f'歡迎回來，{user.username}！', 'success')
            return redirect(url_for('main.index'))
        else:
            flash('Email 或密碼錯誤，請重試！', 'danger')
            return render_template('auth/login.html')

    return render_template('auth/login.html')

@auth_bp.route('/logout')
def logout():
    """
    處理使用者登出
    """
    session.clear()
    flash('您已成功登出。', 'info')
    return redirect(url_for('main.index'))

