import os
from flask import Flask
from app.models import db, Category

def create_app(config_class='config.Config'):
    app = Flask(__name__)
    app.config.from_object(config_class)

    # 確保 instance 資料夾存在
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    # 初始化資料庫
    db.init_app(app)

    # 註冊 Blueprints
    from app.routes.main import main_bp
    from app.routes.events import events_bp
    from app.routes.auth import auth_bp

    app.register_blueprint(main_bp)
    app.register_blueprint(events_bp)
    app.register_blueprint(auth_bp)

    # 自動建立資料庫與初始化預設分類 (Seeding)
    with app.app_context():
        db.create_all()
        
        # 預設分類種子資料
        default_categories = ['學術講座', '社團活動', '運動競賽', '工讀公告', '系所通知', '其他活動']
        for name in default_categories:
            existing = Category.query.filter_by(name=name).first()
            if not existing:
                category = Category(name=name)
                db.session.add(category)
        db.session.commit()

    return app
