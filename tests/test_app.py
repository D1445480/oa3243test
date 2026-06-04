import unittest
from datetime import datetime, timedelta
from app import create_app
from app.models import db, Category
from app.models.user import User
from app.models.event import Event
from app.models.favorite import Favorite
from config import Config

class TestConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'  # 使用記憶體資料庫進行測試，避免干擾本地資料
    WTF_CSRF_ENABLED = False

class CampusEventIntegrationTestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app(TestConfig)
        self.client = self.app.test_client()
        self.app_context = self.app.app_context()
        self.app_context.push()
        # 資料庫已在 create_app 內自動建立並種子化分類資料

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_user_registration_and_login(self):
        """測試使用者註冊與登入功能"""
        # 1. 註冊學生帳號
        response = self.client.post('/auth/register', data={
            'username': 'student_test',
            'email': 'student@test.com',
            'password': 'password123',
            'role': 'student'
        }, follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn('註冊成功！請登入您的帳號。', response.get_data(as_text=True))

        # 2. 登入學生帳號
        response = self.client.post('/auth/login', data={
            'username': 'student_test',
            'password': 'password123'
        }, follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn('歡迎回來，student_test！', response.get_data(as_text=True))

    def test_event_publishing_and_management(self):
        """測試活動發布與管理功能 (主辦單位專屬)"""
        # 1. 註冊並登入主辦單位帳號
        User.create(username='org_test', email='org@test.com', password='password123', role='organizer')
        self.client.post('/auth/login', data={
            'username': 'org_test',
            'password': 'password123'
        })

        # 2. 發布新活動
        start_time = (datetime.utcnow() + timedelta(days=1)).strftime('%Y-%m-%dT%H:%M')
        end_time = (datetime.utcnow() + timedelta(days=2)).strftime('%Y-%m-%dT%H:%M')
        
        response = self.client.post('/event/publish', data={
            'title': '測試社團成果展',
            'category': 'club',
            'start_time': start_time,
            'end_time': end_time,
            'location': '學生活動中心二樓',
            'description': '這是一場精彩的測試社團成果發表會！',
            'registration_link': 'https://google.com',
            'contact_info': '張同學 0900-123456'
        }, follow_redirects=True)
        
        self.assertEqual(response.status_code, 200)
        self.assertIn('活動發布成功！', response.get_data(as_text=True))
        
        # 驗證資料庫已建立活動
        event = Event.query.filter_by(title='測試社團成果展').first()
        self.assertIsNotNone(event)
        self.assertEqual(str(event.category), 'club')

        # 3. 進入管理後台檢視
        response = self.client.get('/event/manage')
        self.assertEqual(response.status_code, 200)
        self.assertIn('測試社團成果展', response.get_data(as_text=True))

        # 4. 編輯活動
        new_location = '體育館三樓'
        response = self.client.post(f'/event/edit/{event.id}', data={
            'title': '測試社團成果展 (已更新)',
            'category': 'club',
            'start_time': start_time,
            'end_time': end_time,
            'location': new_location,
            'description': '這是一場精彩的測試社團成果發表會！',
            'registration_link': 'https://google.com',
            'contact_info': '張同學 0900-123456'
        }, follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn('活動修改成功！', response.get_data(as_text=True))
        
        updated_event = Event.get_by_id(event.id)
        self.assertEqual(updated_event.location, new_location)
        self.assertEqual(updated_event.title, '測試社團成果展 (已更新)')

        # 5. 刪除活動
        response = self.client.post(f'/event/delete/{event.id}', follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn('活動已成功刪除下架。', response.get_data(as_text=True))
        self.assertIsNone(Event.get_by_id(event.id))

    def test_event_favorites_flow(self):
        """測試活動收藏完整資料流 (AJAX 收藏與取消收藏)"""
        # 1. 建立主辦單位並發布活動
        org = User.create(username='org_owner', email='org_owner@test.com', password='password', role='organizer')
        start = (datetime.utcnow() + timedelta(days=1))
        end = (datetime.utcnow() + timedelta(days=2))
        
        cat = Category.query.filter_by(name='學術講座').first()
        self.assertIsNotNone(cat)
        
        event = Event.create(
            title='講座: AI發展趨勢', category_id=cat.id, start_time=start, end_time=end,
            location='資工館101', description='AI講座', registration_link='', contact_info='', organizer_id=org.id
        )

        # 2. 建立學生並登入
        student = User.create(username='student_user', email='student_user@test.com', password='password', role='student')
        self.client.post('/auth/login', data={'username': 'student_user', 'password': 'password'})

        # 3. 測試 AJAX 收藏功能
        response = self.client.post(f'/favorite/toggle/{event.id}')
        self.assertEqual(response.status_code, 200)
        res_data = response.get_json()
        self.assertEqual(res_data['status'], 'success')
        self.assertEqual(res_data['action'], 'favorited')
        
        # 驗證資料庫收藏關係已建立
        self.assertTrue(Favorite.is_favorited(student.id, event.id))

        # 4. 檢視「我的收藏」頁面
        response = self.client.get('/favorite/my-favorites')
        self.assertEqual(response.status_code, 200)
        self.assertIn('講座: AI發展趨勢', response.get_data(as_text=True))

        # 5. 測試 AJAX 取消收藏
        response = self.client.post(f'/favorite/toggle/{event.id}')
        self.assertEqual(response.status_code, 200)
        res_data = response.get_json()
        self.assertEqual(res_data['status'], 'success')
        self.assertEqual(res_data['action'], 'unfavorited')

        # 驗證資料庫收藏關係已移除
        self.assertFalse(Favorite.is_favorited(student.id, event.id))

    def test_event_browsing(self):
        """測試活動資訊瀏覽功能 (F-01)"""
        # 1. 建立測試活動
        org = User.create(username='org_browse', email='org_browse@test.com', password='password', role='organizer')
        cat = Category.query.filter_by(name='學術講座').first()
        start = datetime.utcnow() + timedelta(days=1)
        end = datetime.utcnow() + timedelta(days=2)
        event = Event.create(
            title='公開講座: 探索物聯網', category_id=cat.id, start_time=start, end_time=end,
            location='綜合大樓101', description='物聯網的未來與挑戰', registration_link='', contact_info='聯絡信箱: test@test.com', organizer_id=org.id
        )

        # 2. 匿名瀏覽首頁列表
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        response_text = response.get_data(as_text=True)
        self.assertIn('公開講座: 探索物聯網', response_text)
        self.assertIn('綜合大樓101', response_text)

        # 3. 匿名瀏覽活動詳情頁面
        response = self.client.get(f'/event/detail/{event.id}')
        self.assertEqual(response.status_code, 200)
        detail_text = response.get_data(as_text=True)
        self.assertIn('公開講座: 探索物聯網', detail_text)
        self.assertIn('物聯網的未來與挑戰', detail_text)
        self.assertIn('綜合大樓101', detail_text)
        self.assertIn('聯絡信箱: test@test.com', detail_text)

    def test_event_category_and_search(self):
        """測試活動分類與搜尋功能 (F-02)"""
        # 1. 建立兩個不同分類的活動
        org = User.create(username='org_search', email='org_search@test.com', password='password', role='organizer')
        cat_lecture = Category.query.filter_by(name='學術講座').first()
        cat_club = Category.query.filter_by(name='社團活動').first()
        start = datetime.utcnow() + timedelta(days=1)
        end = datetime.utcnow() + timedelta(days=2)

        event_lecture = Event.create(
            title='人工智慧導論', category_id=cat_lecture.id, start_time=start, end_time=end,
            location='資工系館', description='學習AI基礎知識', registration_link='', contact_info='', organizer_id=org.id
        )
        event_club = Event.create(
            title='熱舞社迎新晚會', category_id=cat_club.id, start_time=start, end_time=end,
            location='戶外劇場', description='歡迎所有新生加入熱舞社', registration_link='', contact_info='', organizer_id=org.id
        )

        # 2. 測試分類篩選 (學術講座)
        response = self.client.get('/?category=lecture')
        self.assertEqual(response.status_code, 200)
        text = response.get_data(as_text=True)
        self.assertIn('人工智慧導論', text)
        self.assertNotIn('熱舞社迎新晚會', text)

        # 3. 測試分類篩選 (社團活動)
        response = self.client.get('/?category=club')
        self.assertEqual(response.status_code, 200)
        text = response.get_data(as_text=True)
        self.assertIn('熱舞社迎新晚會', text)
        self.assertNotIn('人工智慧導論', text)

        # 4. 測試關鍵字搜尋 (搜尋 '人工智慧')
        response = self.client.get('/?q=人工智慧')
        self.assertEqual(response.status_code, 200)
        text = response.get_data(as_text=True)
        self.assertIn('人工智慧導論', text)
        self.assertNotIn('熱舞社迎新晚會', text)

        # 5. 測試關鍵字搜尋 (搜尋 '迎新')
        response = self.client.get('/?q=迎新')
        self.assertEqual(response.status_code, 200)
        text = response.get_data(as_text=True)
        self.assertIn('熱舞社迎新晚會', text)
        self.assertNotIn('人工智慧導論', text)

    def test_latest_event_notifications(self):
        """測試最新活動通知功能 (F-05)"""
        # 1. 建立並訂閱簡訊的學生 A，以及未訂閱的學生 B
        student_a = User.create(username='sub_student_a', email='sub_a@test.com', password='password', role='student')
        student_a.phone = '0900-111-222'
        student_a.receive_sms = True
        
        student_b = User.create(username='sub_student_b', email='sub_b@test.com', password='password', role='student')
        student_b.phone = '0900-333-444'
        student_b.receive_sms = False
        
        db.session.commit()

        # 2. 註冊並登入主辦單位帳號
        User.create(username='org_notif', email='org_notif@test.com', password='password', role='organizer')
        self.client.post('/auth/login', data={
            'username': 'org_notif',
            'password': 'password'
        })

        # 3. 發布新活動，確認發送簡訊給 1 位使用者
        start_time = (datetime.utcnow() + timedelta(days=1)).strftime('%Y-%m-%dT%H:%M')
        end_time = (datetime.utcnow() + timedelta(days=2)).strftime('%Y-%m-%dT%H:%M')
        
        response = self.client.post('/event/publish', data={
            'title': '測試發布與簡訊通知活動',
            'category': 'lecture',
            'start_time': start_time,
            'end_time': end_time,
            'location': '行政大樓七樓',
            'description': '這是一場會觸發簡訊發送測試的講座！',
            'registration_link': '',
            'contact_info': ''
        }, follow_redirects=True)

        self.assertEqual(response.status_code, 200)
        # 驗證 Flash 訊息中，通知了 1 位訂閱使用者
        self.assertIn('活動發布成功！已發送簡訊通知 1 位訂閱使用者。', response.get_data(as_text=True))

if __name__ == '__main__':
    unittest.main()
