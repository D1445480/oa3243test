import os
import sys
from datetime import datetime
from app import create_app
from app.models import db, User, Event, Category
from app.utils.sms import notify_users_of_new_event

def run_test():
    print("🚀 [TEST] Starting SMS Notification Integration Test...", file=sys.stderr)
    
    # 1. 建立測試環境 App，使用獨立的測試 SQLite 資料庫
    test_db_path = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'instance', 'test_database.db')
    if os.path.exists(test_db_path):
        try:
            os.remove(test_db_path)
        except OSError:
            pass
            
    class TestConfig:
        SECRET_KEY = 'test-secret'
        SQLALCHEMY_DATABASE_URI = f"sqlite:///{test_db_path}"
        SQLALCHEMY_TRACK_MODIFICATIONS = False
        TWILIO_ACCOUNT_SID = None  # 強制使用 Mock 模擬發送
        TWILIO_AUTH_TOKEN = None
        TWILIO_PHONE_NUMBER = None

    app = create_app(config_class=TestConfig)
    
    with app.app_context():
        # 確保資料表全新建立
        db.drop_all()
        db.create_all()
        
        # 建立預設分類
        cat = Category(name="學術講座")
        db.session.add(cat)
        db.session.commit()
        
        print("\n📝 [TEST] Step 1: Creating test users...", file=sys.stderr)
        
        # 建立主辦單位
        organizer = User(username="主辦單位A", email="org@test.com", role="organizer")
        organizer.set_password("password123")
        db.session.add(organizer)
        
        # 建立訂閱簡訊的學生 A
        student_a = User(
            username="學生王大同 (已訂閱)", 
            email="student_a@test.com", 
            role="student",
            phone="0912-345-678",
            receive_sms=True
        )
        student_a.set_password("password123")
        db.session.add(student_a)
        
        # 建立未訂閱簡訊的學生 B
        student_b = User(
            username="學生李小華 (未訂閱)", 
            email="student_b@test.com", 
            role="student",
            phone="0987-654-321",
            receive_sms=False
        )
        student_b.set_password("password123")
        db.session.add(student_b)
        
        db.session.commit()
        print("✅ [TEST] Test users created successfully.", file=sys.stderr)
        
        print("\n📝 [TEST] Step 2: Creating a new event...", file=sys.stderr)
        # 建立新活動
        test_event = Event(
            title="國立大學AI與機器學習應用研討會",
            description="本研討會將邀請產學界專家，分享AI在不同領域的創新應用與未來趨勢，名額有限，報名從速！",
            event_date=datetime(2026, 6, 20, 14, 0),
            location="圖書館國際會議廳",
            organizer_id=organizer.id,
            category_id=cat.id
        )
        db.session.add(test_event)
        db.session.commit()
        print(f"✅ [TEST] Event '{test_event.title}' created and committed to DB.", file=sys.stderr)
        
        print("\n📝 [TEST] Step 3: Triggering SMS notification service...", file=sys.stderr)
        # 觸發簡訊發送
        success_sent = notify_users_of_new_event(test_event)
        
        print(f"\n📊 [TEST] Results: Notification triggered for {success_sent} user(s).", file=sys.stderr)
        
        # 斷言驗證
        assert success_sent == 1, f"Expected 1 subscriber to receive notification, but got {success_sent}"
        print("🎉 [TEST] Integration Test Passed successfully! Mock SMS triggered exactly for Student A.", file=sys.stderr)

if __name__ == '__main__':
    try:
        run_test()
        sys.exit(0)
    except AssertionError as ae:
        print(f"❌ [TEST ERROR] Assertion failed: {str(ae)}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"❌ [TEST ERROR] Unexpected exception: {str(e)}", file=sys.stderr)
        sys.exit(1)
