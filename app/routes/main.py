from flask import Blueprint, render_template

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def index():
    """
    處理首頁請求
    
    邏輯：
    1. 取得即將到來的最新活動 (最多 6 筆)
    2. 取得所有分類 (供導覽列使用)
    3. 渲染 index.html
    """
    pass
