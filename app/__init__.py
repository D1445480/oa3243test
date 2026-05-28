import os
from flask import Flask
from flask_login import LoginManager
from config import Config
from app.models import db, Category, User
from app.routes import register_blueprints

# 初始化 LoginManager 擴充套件
login_manager = LoginManager()
login_manager.login_view = 'auth.login'  # 當未登入使用者存取受保護路由時，重導向至登入頁面
login_manager.login_message = '請先登入系統以存取此功能。'
login_manager.login_message_category = 'warning'

@login_manager.user_loader
def load_user(user_id):
    """
    Flask-Login 用來加載當前登入使用者的回呼函式
    """
    return User.get_by_id(user_id)

def create_app(config_class=Config):
    """
    Flask App 工廠函式 (App Factory)
    """
    app = Flask(__name__)
    app.config.from_object(config_class)

    # 初始化資料庫與登入管理套件
    db.init_app(app)
    login_manager.init_app(app)

    # 註冊 Blueprints 路由
    register_blueprints(app)

    # 確保 Flask 的 instance 資料夾存在 (用於存放 SQLite database)
    if not os.path.exists(app.instance_path):
        os.makedirs(app.instance_path)

    # 自動在 app 啟動時建立 SQLite 資料庫與所有資料表，並置入初始分類資料 (Seeding)
    with app.app_context():
        db.create_all()

        # 預設分類種子資料 (與組員的分類相容)
        default_categories = ['學術講座', '社團活動', '運動競賽', '工讀公告', '系所通知', '其他活動']
        for name in default_categories:
            existing = Category.query.filter_by(name=name).first()
            if not existing:
                category = Category(name=name)
                db.session.add(category)
        db.session.commit()

    return app
