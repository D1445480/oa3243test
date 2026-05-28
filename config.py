import os
from dotenv import load_dotenv

# 載入 .env 檔中的環境變數
load_dotenv()

class Config:
    """專案組態設定"""
    SECRET_KEY = os.environ.get('SECRET_KEY', 'campus-events-platform-secret-key-12938')
    
    # 預設資料庫存放在 instance/database.db
    # SQLAlchemy 的 sqlite:/// 後接相對路徑時，會自動指向 Flask app 的 instance 資料夾
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL', 'sqlite:///database.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # 簡訊服務設定 (Twilio 預留)
    TWILIO_ACCOUNT_SID = os.environ.get('TWILIO_ACCOUNT_SID')
    TWILIO_AUTH_TOKEN = os.environ.get('TWILIO_AUTH_TOKEN')
    TWILIO_PHONE_NUMBER = os.environ.get('TWILIO_PHONE_NUMBER')
