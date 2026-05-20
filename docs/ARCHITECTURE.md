# 系統架構設計 (ARCHITECTURE)

## 1. 技術架構說明

為了解決校園活動資訊分散的問題，並快速建立出高效率、易於使用的 MVP（最小可行性產品），我們選擇了以下技術組合：

- **後端框架**：**Python + Flask**
  - **原因**：Flask 輕量、靈活，非常適合小型專案與快速開發。它的學習曲線平緩，且擁有豐富的擴充套件，能讓我們專注於核心功能的實作。
- **模板引擎**：**Jinja2**
  - **原因**：與 Flask 完美整合，直接由後端渲染 HTML 畫面（伺服器端渲染 SSR）。由於我們的系統初期不需要複雜的前端狀態管理，非前後端分離架構能大幅降低開發成本並加快上線速度。
- **資料庫**：**SQLite (搭配 SQLAlchemy)**
  - **原因**：SQLite 是一套輕量級關聯式資料庫，資料儲存於單一檔案，無需額外的伺服器架設。配合 SQLAlchemy (ORM) 可用 Python 語法安全地操作資料庫，預防 SQL Injection，並為未來的擴充保留彈性。

### Flask MVC 模式應用
我們將採用類似 MVC (Model-View-Controller) 的架構來分離職責：
- **Model (資料模型)**：負責定義資料表（例如：User, Event），透過 SQLAlchemy 與 SQLite 互動。
- **View (視圖)**：Jinja2 模板，負責將資料（例如活動列表）渲染成漂亮的 HTML 頁面給使用者。
- **Controller (控制器/路由)**：Flask 的 Route，負責接收使用者的請求，向 Model 取得或更新資料，然後決定回傳哪個 View。

---

## 2. 專案資料夾結構

本專案的程式碼將依照功能與職責進行結構化整理，詳細規劃如下：

```text
campus_events_platform/
│
├── app/                      ← 應用程式主目錄 (Flask 核心)
│   ├── __init__.py           ← 負責初始化 Flask 實例與資料庫連線
│   ├── models.py             ← 定義資料庫的 Model (Table 結構)
│   ├── routes/               ← Controller 路由目錄
│   │   ├── __init__.py
│   │   ├── main.py           ← 首頁與共用頁面路由
│   │   ├── events.py         ← 活動相關路由 (瀏覽、搜尋、管理)
│   │   └── auth.py           ← 會員認證相關路由 (註冊、登入)
│   ├── templates/            ← Jinja2 HTML 模板 (View)
│   │   ├── base.html         ← 網站共用主版型 (Header, Footer)
│   │   ├── index.html        ← 首頁
│   │   ├── events/
│   │   │   ├── list.html     ← 活動列表與搜尋結果頁
│   │   │   ├── detail.html   ← 單一活動詳細資訊頁
│   │   │   └── form.html     ← 新增/編輯活動表單頁
│   │   └── auth/
│   │       ├── login.html    ← 登入頁面
│   │       └── register.html ← 註冊頁面
│   └── static/               ← 前端靜態資源
│       ├── css/
│       │   └── style.css     ← 自訂樣式表
│       ├── js/
│       │   └── main.js       ← 前端互動腳本
│       └── images/           ← 圖片資源目錄
│
├── instance/                 ← 不加入版本控制的動態生成的實體檔案
│   └── database.db           ← SQLite 資料庫檔案
│
├── docs/                     ← 開發與系統文件 (PRD, 架構圖等)
│
├── config.py                 ← 環境與應用程式設定檔 (如 SECRET_KEY)
├── run.py                    ← 啟動伺服器的程式入口
├── requirements.txt          ← Python 依賴套件清單
└── README.md                 ← 專案說明文件
```

---

## 3. 元件關係圖

以下展示了系統在處理一次使用者請求時，各元件之間的資料流動與關係：

```mermaid
flowchart TD
    Browser[使用者瀏覽器]
    
    subgraph 伺服器端 [Flask Application]
        Router[Flask Route (Controller)]
        Model[SQLAlchemy (Model)]
        Template[Jinja2 HTML (View)]
    end
    
    Database[(SQLite 資料庫)]
    
    %% 請求與回應流程
    Browser -- "1. HTTP Request (例如搜尋活動)" --> Router
    Router -- "2. 查詢資料 (ORM)" --> Model
    Model -- "3. SQL 查詢" --> Database
    Database -- "4. 回傳資料" --> Model
    Model -- "5. 轉為 Python 物件" --> Router
    Router -- "6. 傳遞資料" --> Template
    Template -- "7. 渲染畫面" --> Router
    Router -- "8. HTTP Response (HTML)" --> Browser
```

---

## 4. 關鍵設計決策

1. **路由藍圖化 (Flask Blueprints)**
   - **說明**：我們會將路由依照功能切分成 `main.py`、`events.py` 與 `auth.py`。
   - **原因**：避免所有的路由邏輯全擠在一個檔案裡，提高程式碼的易讀性與團隊協作效率。
   
2. **共用基礎模板 (Template Inheritance)**
   - **說明**：所有頁面將繼承自 `base.html`。
   - **原因**：確保導覽列與頁尾在所有頁面維持一致，並且在修改共用元件時只需更改一個檔案。

3. **統一設定管理 (`config.py`)**
   - **說明**：專案設定（如資料庫連線路徑、加密金鑰）會集中在 `config.py`。
   - **原因**：讓環境設定與業務邏輯分離，未來若要區分開發環境與正式環境時會更容易維護。
