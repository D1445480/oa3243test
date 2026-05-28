from app.routes.auth import auth_bp
from app.routes.main import main_bp
from app.routes.event import event_bp
from app.routes.favorite import favorite_bp
from app.routes.events import events_bp  # 組員(d1445480)的活動路由

def register_blueprints(app):
    """
    將所有模組的 Blueprint 註冊到 Flask 實例中
    """
    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(main_bp)  # 首頁與詳情頁使用根路徑
    app.register_blueprint(event_bp, url_prefix='/event')
    app.register_blueprint(favorite_bp, url_prefix='/favorite')
    app.register_blueprint(events_bp, url_prefix='/events')  # 註冊組員的活動路由，以保持相容性
