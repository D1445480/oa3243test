from flask import Blueprint, request, render_template

auth_bp = Blueprint('auth', __name__, url_prefix='/auth')

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    """
    處理使用者註冊
    
    邏輯：
    1. GET: 渲染 auth/register.html
    2. POST: 驗證 email 是否重複，將密碼 hash 後存入資料庫
    """
    pass

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """
    處理使用者登入
    
    邏輯：
    1. GET: 渲染 auth/login.html
    2. POST: 驗證 email 與密碼，成功則記錄至 session 並重導向
    """
    pass

@auth_bp.route('/logout')
def logout():
    """
    處理使用者登出
    
    邏輯：
    1. 清空 session 資料
    2. 重導向至首頁
    """
    pass
