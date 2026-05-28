from app.models import db

class Category(db.Model):
    """
    活動分類模型
    """
    __tablename__ = 'categories'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(50), unique=True, nullable=False)

    @classmethod
    def create(cls, name):
        try:
            category = cls(name=name)
            db.session.add(category)
            db.session.commit()
            return category
        except Exception as e:
            db.session.rollback()
            raise e

    def __repr__(self):
        return f"<Category {self.name}>"

    def __str__(self):
        """
        將中文分類名稱映射為英文識別碼，以方便 Jinja2 模板直接渲染為 CSS 類別
        """
        mapping = {
            '學術講座': 'lecture',
            '社團活動': 'club',
            '運動競賽': 'competition',
            '工讀公告': 'job',
            '系所通知': 'announcement',
            '其他活動': 'announcement'
        }
        return mapping.get(self.name, 'announcement')
