from flask import Blueprint, render_template, redirect, url_for, request, flash
from flask_login import login_user, logout_user, login_required, current_user

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    """
    [GET] 顯示註冊表單頁面 (templates/register.html)
    [POST] 接收表單欄位：username, email, password, role，並呼叫 User.create 建立帳號
    
    處理邏輯：
    1. 驗證必填欄位與格式是否正確。
    2. 檢查 username 與 email 是否已被註冊。
    3. 成功後設定 flash 訊息並重導向至 /auth/login。
    4. 失敗時顯示錯誤並重新渲染註冊頁。
    """
    pass

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """
    [GET] 顯示登入表單頁面 (templates/login.html)
    [POST] 接收表單欄位：username, password，並驗證密碼
    
    處理邏輯：
    1. 查詢使用者是否存在。
    2. 驗證密碼雜湊。
    3. 驗證成功使用 login_user(user) 建立登入 Session，並依角色重導向：
       - 'student': 重導向至首頁 '/'
       - 'organizer': 重導向至管理後台 '/event/manage'
    4. 驗證失敗顯示錯誤並重新渲染登入頁。
    """
    pass

@auth_bp.route('/logout', methods=['POST'])
@login_required
def logout():
    """
    [POST] 登出當前帳號
    
    處理邏輯：
    1. 呼叫 logout_user() 清除 Session。
    2. 設定 flash 成功訊息。
    3. 重導向至首頁 '/'。
    """
    pass
