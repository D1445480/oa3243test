# 使用者流程與系統流程圖 (FLOWCHART)

## 1. 使用者流程圖 (User Flow)

此流程圖描述一般學生與主辦單位從進入網站開始的操作路徑與體驗。

```mermaid
flowchart LR
    A([進入網站]) --> B[瀏覽首頁與近期活動]
    
    %% 搜尋與瀏覽分支
    B --> C{尋找特定活動？}
    C -->|是| D[使用關鍵字或分類篩選]
    D --> E[顯示符合條件的活動列表]
    C -->|否| E
    
    E --> F[點擊進入活動詳細頁]
    
    %% 登入後行為分支
    F --> G{使用者已登入？}
    G -->|否| H[瀏覽資訊結束，關閉或回首頁]
    
    G -->|是| I{使用者身分}
    I -->|一般學生| J[點擊「加入收藏」追蹤活動]
    I -->|主辦單位| K{是自己發布的嗎？}
    
    K -->|是| L[進入編輯或刪除頁面]
    K -->|否| H
    
    %% 發布活動流程
    B --> M[點擊「發布活動」]
    M --> N{已登入為主辦方？}
    N -->|否| O[重導向至登入頁]
    N -->|是| P[填寫活動資訊表單]
    P --> Q[送出並發布成功]
    Q --> B
```

---

## 2. 系統序列圖 (Sequence Diagram)

此序列圖描述「主辦單位新增活動」時，前端、後端與資料庫之間的資料傳遞流程。

```mermaid
sequenceDiagram
    actor User as 主辦單位 (User)
    participant Browser as 瀏覽器 (View)
    participant Route as Flask 路由 (Controller)
    participant Model as SQLAlchemy (Model)
    participant DB as SQLite (Database)

    User->>Browser: 填寫「新增活動」表單並送出
    Browser->>Route: POST /events/new (攜帶表單資料)
    
    activate Route
    Route->>Route: 驗證表單資料 (必填欄位等)
    Route->>Model: 建立 Event 物件 (Event(title=...))
    Route->>Model: db.session.add(event)
    Route->>Model: db.session.commit()
    
    activate Model
    Model->>DB: 執行 SQL: INSERT INTO events ...
    activate DB
    DB-->>Model: 回傳成功狀態與生成之 ID
    deactivate DB
    Model-->>Route: 資料庫操作完成
    deactivate Model
    
    Route-->>Browser: HTTP 302 Redirect (重導向至首頁或列表頁)
    deactivate Route
    
    Browser->>User: 顯示「新增成功」並呈現最新活動列表
```

---

## 3. 功能清單與路由對照表

本表列出系統預期實作之核心功能與對應的路由規劃。

| 功能名稱 | URL 路徑 | HTTP 方法 | 說明 |
| --- | --- | --- | --- |
| **首頁 / 近期活動** | `/` | GET | 顯示最新的活動精選與導覽列。 |
| **活動列表總覽** | `/events` | GET | 列出系統內所有的活動，預設依日期排序。 |
| **活動分類與搜尋** | `/events/search` | GET | 透過 Query Parameter (如 `?q=關鍵字` 或 `?category=講座`) 取得篩選結果。 |
| **活動詳細資訊** | `/events/<id>` | GET | 顯示指定活動的完整圖文、時間與地點。 |
| **新增活動頁面** | `/events/new` | GET | 顯示供主辦單位填寫的表單 (需驗證登入權限)。 |
| **送出新增活動** | `/events/new` | POST | 接收表單，將新活動寫入資料庫並重導向。 |
| **編輯活動頁面** | `/events/<id>/edit` | GET | 顯示活動編輯表單，預設帶入舊有資料。 |
| **更新活動資料** | `/events/<id>/edit` | POST | 將修改過的資料更新至資料庫。 |
| **刪除活動** | `/events/<id>/delete`| POST | 自資料庫移除指定活動 (為防誤觸，通常不直接使用 GET)。 |
| **會員註冊** | `/auth/register` | GET/POST | 顯示註冊表單與處理帳號建立邏輯。 |
| **會員登入** | `/auth/login` | GET/POST | 處理使用者登入並建立 Session。 |
| **會員登出** | `/auth/logout` | GET | 清除 Session 並回到首頁。 |
