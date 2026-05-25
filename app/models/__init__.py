from flask_sqlalchemy import SQLAlchemy

# 初始化 db 實例，後續在 appFactory (app/__init__.py) 中呼叫 db.init_app(app)
db = SQLAlchemy()

# 匯出各模型，方便外部直接從 app.models 匯入
from app.models.user import User
from app.models.event import Event
from app.models.favorite import Favorite
