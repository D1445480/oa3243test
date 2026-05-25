# 使用者與系統流程圖文件 (Flowcharts & Sequence Diagrams)

本文件描述「校園活動資訊整合平台」的使用者操作流程（User Flow）、系統資料流向（Sequence Diagram）以及對應的路由與 API 規劃。

---

## 1. 使用者流程圖 (User Flow)

此圖描述一般訪客、學生與主辦單位在平台上的操作路徑。

```mermaid
flowchart LR
    Start([使用者開啟網頁]) --> Home[首頁 - 活動列表與搜尋]
    Home --> Choice{是否登入？}
    
    %% 未登入訪客流程
    Choice -->|否| GuestChoice{要做什麼？}
    GuestChoice -->|瀏覽與篩選活動| Home
    GuestChoice -->|查看活動詳情| Detail[活動詳情頁]
    GuestChoice -->|點擊收藏活動| LoginPrompt[引導至登入/註冊]
    GuestChoice -->|欲發布活動| LoginPrompt
    LoginPrompt --> Register[註冊帳號]
    Register --> Login[登入系統]
    Login --> Choice
    
    %% 已登入使用者流程
    Choice -->|是| RoleChoice{角色身份？}
    
    %% 學生分支
    RoleChoice -->|一般學生| StudentAction{選擇操作}
    StudentAction -->|瀏覽活動| Home
    StudentAction -->|查看活動詳情| StudentDetail[活動詳情頁]
    StudentDetail -->|點擊收藏/取消收藏| ToggleFav[API 狀態切換]
    ToggleFav --> StudentDetail
    StudentAction -->|進入個人收藏專區| FavList[我的收藏頁面]
    FavList -->|點擊活動| StudentDetail
    FavList -->|取消收藏| FavList
    
    %% 主辦單位分支
    RoleChoice -->|活動主辦單位| OrganizerAction{選擇操作}
    OrganizerAction -->|進入管理後台| ManageHome[我發布的活動列表]
    ManageHome --> ManageAction{後台操作}
    ManageAction -->|發布新活動| PublishForm[活動發布表單]
    PublishForm -->|填寫並送出| SaveNew[資料庫寫入]
    SaveNew --> ManageHome
    ManageAction -->|編輯活動| EditForm[活動編輯表單]
    EditForm -->|儲存更新| UpdateDB[資料庫更新]
    UpdateDB --> ManageHome
    ManageAction -->|刪除活動| DeleteCheck{確認刪除？}
    DeleteCheck -->|是| DeleteDB[資料庫刪除]
    DeleteDB --> ManageHome
```

---

## 2. 系統序列圖 (Sequence Diagram)

以下是本專案主要分工功能的系統資料流向。

### 2.1 活動收藏功能序列圖 (AJAX 異步處理)
描述學生點擊「收藏/取消收藏」到資料庫更新並回傳的流程。

```mermaid
sequenceDiagram
    autonumber
    actor Student as 一般學生
    participant Browser as 瀏覽器 (JS AJAX)
    participant Route as Flask Route (favorite.py)
    participant Model as Favorite Model (favorite.py)
    participant DB as SQLite 資料庫
    
    Student->>Browser: 點擊「加入收藏/取消收藏」
    Browser->>Route: POST /favorite/toggle/<event_id>
    Note over Route: 驗證 Session 登入狀態及是否為學生
    Route->>Model: 查詢是否已存在收藏紀錄
    alt 已收藏：執行取消收藏
        Route->>Model: 刪除收藏關聯
        Model->>DB: DELETE FROM favorites WHERE user_id AND event_id
        DB-->>Model: 刪除成功
        Route-->>Browser: HTTP 200 JSON {status: "unfavorited", message: "已取消收藏"}
    else 未收藏：執行加入收藏
        Route->>Model: 建立收藏關聯
        Model->>DB: INSERT INTO favorites (user_id, event_id)
        DB-->>Model: 寫入成功
        Route-->>Browser: HTTP 200 JSON {status: "favorited", message: "已加入收藏"}
    end
    Browser-->>Student: 動態切換按鈕 UI 樣式與狀態提示
```

### 2.2 活動發布與管理序列圖 (Form 表單提交)
描述活動主辦單位填寫表單發布活動至後台列表呈現的流程。

```mermaid
sequenceDiagram
    autonumber
    actor Organizer as 活動主辦單位
    participant Browser as 瀏覽器 (HTML Form)
    participant Route as Flask Route (event.py)
    participant Model as Event Model (event.py)
    participant DB as SQLite 資料庫
    
    Organizer->>Browser: 填寫活動資訊，點擊「送出發布」
    Browser->>Route: POST /event/publish (表單資料)
    Note over Route: 驗證登入狀態及角色為主辦單位
    Note over Route: 檢查欄位合法性 (名稱、時間、地點為必填)
    Route->>Model: 建立 Event 實例 (organizer_id = current_user.id)
    Model->>DB: INSERT INTO events (...)
    DB-->>Model: 寫入成功
    Route-->>Browser: Redirect to /event/manage (HTTP 302 重導向)
    Browser->>Route: GET /event/manage
    Route->>Model: 查詢該主辦發布的所有活動
    Model->>DB: SELECT * FROM events WHERE organizer_id = current_user.id
    DB-->>Model: 回傳活動陣列
    Route-->>Browser: 渲染 event_manage.html (帶入活動列表)
    Browser-->>Organizer: 顯示我發布的活動清單，並跳出「發布成功」提示
```

---

## 3. 功能清單與路由對照表

本平台的路由設計如下，這也是後續開發路由 Skeleton 的基礎：

| 功能模組 | 功能名稱 | URL 路徑 | HTTP 方法 | 限制權限 | 說明 |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Auth** (認證) | 使用者註冊 | `/auth/register` | GET, POST | 無 | 處理一般學生與主辦單位的註冊流程。 |
| | 使用者登入 | `/auth/login` | GET, POST | 無 | 驗證帳密並建立 Session。 |
| | 使用者登出 | `/auth/logout` | POST | 需登入 | 清除 Session 並重導向至首頁。 |
| **Main** (瀏覽) | 首頁活動列表 | `/` | GET | 無 | 顯示活動，支援分類篩選與關鍵字搜尋。 |
| | 活動詳細頁 | `/event/detail/<int:event_id>` | GET | 無 | 展示活動的時間、地點、詳情與報名連結。 |
| **Favorite** (收藏) | 收藏切換 (AJAX) | `/favorite/toggle/<int:event_id>` | POST | 學生 | 切換收藏狀態（自動判斷新增或刪除）。 |
| | 我的收藏清單 | `/favorite/my-favorites` | GET | 學生 | 顯示當前學生帳號已收藏的活動列表。 |
| **Event** (管理) | 發布活動頁面 | `/event/publish` | GET, POST | 主辦單位 | 填寫並發布新活動。 |
| | 主辦管理後台 | `/event/manage` | GET | 主辦單位 | 顯示該主辦帳號發布的所有活動。 |
| | 編輯活動頁面 | `/event/edit/<int:event_id>` | GET, POST | 主辦單位 (限擁有者) | 修改已發布活動的欄位資訊。 |
| | 刪除活動 | `/event/delete/<int:event_id>` | POST | 主辦單位 (限擁有者) | 下架並刪除該活動。 |
