import os
from dotenv import load_dotenv

# 載入 .env 檔中的環境變數
load_dotenv()

class Config:
    """專案組態設定"""
    SECRET_KEY = os.environ.get('SECRET_KEY', 'default-dev-secret-key-999')
    
    # 預設資料庫存放在 instance/database.db
    # SQLAlchemy 的 sqlite:/// 後接相對路徑時，會自動指向 Flask app 的 instance 資料夾
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL', 'sqlite:///database.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
