import os

class Config:
    # 網站安全金鑰
    SECRET_KEY = os.environ.get('SECRET_KEY', 'campus-events-platform-secret-key-12938')
    
    # 取得目前檔案路徑，並指向專案根目錄的 instance/database.db
    BASE_DIR = os.path.abspath(os.path.dirname(__file__))
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        'DATABASE_URL', 
        f"sqlite:///{os.path.join(BASE_DIR, 'instance', 'database.db')}"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # 簡訊服務設定 (Twilio 預留)
    TWILIO_ACCOUNT_SID = os.environ.get('TWILIO_ACCOUNT_SID')
    TWILIO_AUTH_TOKEN = os.environ.get('TWILIO_AUTH_TOKEN')
    TWILIO_PHONE_NUMBER = os.environ.get('TWILIO_PHONE_NUMBER')
