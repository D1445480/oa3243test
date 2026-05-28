from flask_sqlalchemy import SQLAlchemy

# 初始化 db 實例
db = SQLAlchemy()

# 匯出各模型，方便外部直接從 app.models 匯入
from app.models.user import User
from app.models.category import Category
from app.models.event import Event
from app.models.favorite import Favorite, Bookmark
