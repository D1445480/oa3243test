# 路由與頁面設計文件 (Route Design & API Specifications)

本文件定義「校園活動資訊整合平台」的 URL 路由規劃、各路由的輸入輸出與處理邏輯，以及前端 Jinja2 模板配置。

---

## 1. 路由總覽表格

| 功能模組 | HTTP 方法 | URL 路徑 | 對應 Jinja2 模板 | 限制權限 | 說明 |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Auth** (驗證) | `GET` | `/auth/register` | `templates/register.html` | 無 | 顯示註冊頁面 |
| | `POST` | `/auth/register` | — (重導向) | 無 | 處理註冊請求 |
| | `GET` | `/auth/login` | `templates/login.html` | 無 | 顯示登入頁面 |
| | `POST` | `/auth/login` | — (重導向) | 無 | 處理登入請求 |
| | `POST` | `/auth/logout` | — (重導向) | 需登入 | 處理登出請求 |
| **Main** (瀏覽) | `GET` | `/` | `templates/index.html` | 無 | 首頁 (活動列表與搜尋篩選) |
| | `GET` | `/event/detail/<int:event_id>` | `templates/event_detail.html` | 無 | 活動詳情頁面 |
| **Favorite** (收藏) | `POST` | `/favorite/toggle/<int:event_id>` | — (JSON) | 學生 | AJAX 收藏與取消收藏切換 |
| | `GET` | `/favorite/my-favorites` | `templates/favorite_list.html` | 學生 | 顯示個人收藏活動清單頁面 |
| **Event** (管理) | `GET` | `/event/publish` | `templates/event_publish.html` | 主辦單位 | 顯示發布活動表單頁面 |
| | `POST` | `/event/publish` | — (重導向) | 主辦單位 | 處理發布活動請求 |
| | `GET` | `/event/manage` | `templates/event_manage.html` | 主辦單位 | 主辦單位活動管理後台列表 |
| | `GET` | `/event/edit/<int:event_id>` | `templates/event_publish.html` | 主辦單位 (限擁有者) | 顯示編輯活動表單頁面 |
| | `POST` | `/event/edit/<int:event_id>` | — (重導向) | 主辦單位 (限擁有者) | 處理更新活動請求 |
| | `POST` | `/event/delete/<int:event_id>` | — (重導向) | 主辦單位 (限擁有者) | 處理刪除活動請求 |

---

## 2. 每個路由的詳細說明

### 2.1 使用者驗證模組 (Auth)

#### [GET/POST] `/auth/register`
*   **用途**：使用者註冊。
*   **輸入參數**：
    *   `username` (TEXT, 表單必填)：使用者名稱。
    *   `email` (TEXT, 表單必填)：電子郵件。
    *   `password` (TEXT, 表單必填)：密碼。
    *   `role` (TEXT, 表單必填)：角色限制 `'student'` 或 `'organizer'`。
*   **處理邏輯**：
    1. 驗證資料格式，確保無空值且信箱符合格式。
    2. 檢查 `username` 與 `email` 是否已被註冊（呼叫 `User.get_by_username` 和 `User.get_by_email`）。
    3. 呼叫 `User.create(...)` 加密密碼並寫入資料庫。
*   **輸出**：
    *   `GET`：渲染 `templates/register.html`。
    *   `POST 成功`：重導向至 `/auth/login` (HTTP 302)，並 Flash 成功訊息。
*   **錯誤處理**：若欄位不合規或帳號已存在，Flash 錯誤訊息，重新渲染 `register.html` (回傳 HTTP 400)。

#### [GET/POST] `/auth/login`
*   **用途**：使用者登入。
*   **輸入參數**：
    *   `username` (TEXT, 表單必填)：使用者名稱。
    *   `password` (TEXT, 表單必填)：密碼。
*   **處理邏輯**：
    1. 呼叫 `User.get_by_username(username)`。
    2. 使用 `check_password(password)` 驗證密碼雜湊是否吻合。
    3. 成功後呼叫 `login_user(user)` 建立會話。
*   **輸出**：
    *   `GET`：渲染 `templates/login.html`。
    *   `POST 成功`：若使用者為學生角色，重導向至首頁 `/`；若為主辦單位角色，重導向至後台 `/event/manage`。
*   **錯誤處理**：帳密不正確時，Flash 錯誤訊息「帳號或密碼錯誤」，重新渲染 `login.html` (回傳 HTTP 401)。

---

### 2.2 活動瀏覽模組 (Main)

#### [GET] `/`
*   **用途**：首頁，供訪客或學生瀏覽、關鍵字搜尋及分類篩選活動。
*   **輸入參數**：
    *   `category` (Query String, 選填)：篩選特定活動分類。
    *   `q` (Query String, 選填)：關鍵字搜尋。
*   **處理邏輯**：
    1. 呼叫 `Event.get_all(category, search_query=q)` 取得活動列表。
*   **輸出**：渲染 `templates/index.html`，傳入活動清單 `events` 與當前篩選條件。

#### [GET] `/event/detail/<int:event_id>`
*   **用途**：查看特定活動詳細內容。
*   **輸入參數**：`event_id` (URL 路由參數)。
*   **處理邏輯**：
    1. 呼叫 `Event.get_by_id(event_id)`，若不存在回傳 404。
    2. 若使用者已登入且為學生，呼叫 `Favorite.is_favorited(current_user.id, event_id)` 取得收藏狀態。
*   **輸出**：渲染 `templates/event_detail.html`，傳送 `event` 物件與 `is_favorited` 布林值。

---

### 2.3 活動收藏模組 (Favorite)

#### [POST] `/favorite/toggle/<int:event_id>`
*   **用途**：學生點擊收藏或取消收藏（AJAX 異步操作）。
*   **輸入參數**：`event_id` (URL 路由參數)。
*   **處理邏輯**：
    1. 檢查目前登入使用者角色是否為 `student`，若不是則拒絕存取。
    2. 呼叫 `Favorite.toggle(current_user.id, event_id)`，會自動新增或刪除收藏關聯。
*   **輸出**：JSON 格式回傳，例如：
    *   新增收藏成功：`{"status": "success", "action": "favorited", "message": "已加入收藏"}`
    *   取消收藏成功：`{"status": "success", "action": "unfavorited", "message": "已取消收藏"}`
*   **錯誤處理**：未登入或權限不足回傳 `{"status": "error", "message": "Unauthorized"}` (HTTP 401/403)。活動不存在回傳 HTTP 404。

#### [GET] `/favorite/my-favorites`
*   **用途**：顯示當前登入學生的收藏活動清單。
*   **輸入參數**：無（由 Session 取得 `current_user.id`）。
*   **處理邏輯**：
    1. 驗證角色為學生。
    2. 呼叫 `Favorite.get_by_user(current_user.id)` 取得該生收藏的所有活動。
*   **輸出**：渲染 `templates/favorite_list.html`。

---

### 2.4 活動發布與管理模組 (Event)

#### [GET/POST] `/event/publish`
*   **用途**：主辦單位發布新活動。
*   **輸入參數**：
    *   `title`, `category`, `start_time`, `end_time`, `location` (表單必填)
    *   `description`, `registration_link`, `contact_info` (表單選填)
*   **處理邏輯**：
    1. 驗證目前登入使用者角色為 `organizer`。
    2. 驗證結束時間是否大於開始時間。
    3. 呼叫 `Event.create(...)` 將活動寫入資料庫，並設定外鍵 `organizer_id`。
*   **輸出**：
    *   `GET`：渲染 `templates/event_publish.html`。
    *   `POST 成功`：重導向至 `/event/manage`，並 Flash 成功提示。

#### [GET] `/event/manage`
*   **用途**：主辦單位查看自己發布的活動後台列表。
*   **處理邏輯**：
    1. 驗證角色為 `organizer`。
    2. 呼叫 `Event.get_by_organizer(current_user.id)` 獲取活動列表。
*   **輸出**：渲染 `templates/event_manage.html`。

#### [GET/POST] `/event/edit/<int:event_id>`
*   **用途**：主辦單位編輯自己發布的活動。
*   **輸入參數**：`event_id` (URL 路由參數)；表單修改後的各個活動欄位。
*   **處理邏輯**：
    1. 查詢活動是否存在，且 `organizer_id` 是否等於 `current_user.id` (防止越權修改)。
    2. [POST] 接收修改欄位並呼叫 `event.update(...)`。
*   **輸出**：
    *   `GET`：渲染 `templates/event_publish.html` (複用發布表單，並帶入舊有活動資料)。
    *   `POST 成功`：重導向至 `/event/manage`。

#### [POST] `/event/delete/<int:event_id>`
*   **用途**：刪除 (下架) 指定活動。
*   **輸入參數**：`event_id` (URL 路由參數)。
*   **處理邏輯**：
    1. 查詢活動並驗證是否為該活動的發布擁有者。
    2. 呼叫 `event.delete()` 將其從資料庫中移除。
*   **輸出**：重導向至 `/event/manage`，並 Flash 「活動已刪除」。

---

## 3. Jinja2 模板清單

專案的前端頁面皆基於同一個基礎版型 `base.html` 進行繼承與擴充：

1.  **`templates/base.html`** (基礎版型)
    *   *功能*：包含全域網頁標頭、CSS 載入、Responsive RWD 導覽列（依登入狀態與角色動態顯示不同連結）、Flash 提示訊息容器、網頁主內容區塊 (`{% block content %}`) 以及全域 JavaScript 與頁尾。
2.  **`templates/index.html`** (繼承 `base.html`)
    *   *功能*：顯示所有活動的看板。上方有搜尋欄與分類標籤按鈕，下方以卡片 (Cards) 呈現活動，包含標題、分類標籤、時間與地點，並為學生角色提供收藏快捷按鈕。
3.  **`templates/event_detail.html`** (繼承 `base.html`)
    *   *功能*：顯示活動完整詳細資訊（描述、報名連結等），學生可在此頁點擊「收藏/取消收藏」，主辦單位若是該活動擁有者則顯示「編輯」與「刪除」按鈕。
4.  **`templates/login.html`** (繼承 `base.html`)
    *   *功能*：登入表單。
5.  **`templates/register.html`** (繼承 `base.html`)
    *   *功能*：註冊表單，包含選取角色的下拉選單或單選鈕（一般學生 / 活動主辦）。
6.  **`templates/favorite_list.html`** (繼承 `base.html`)
    *   *功能*：已登入學生的收藏夾頁面。以卡片清單列出該生收藏的所有活動。
7.  **`templates/event_publish.html`** (繼承 `base.html`)
    *   *功能*：主辦單位發布活動與編輯活動的填寫表單頁。
8.  **`templates/event_manage.html`** (繼承 `base.html`)
    *   *功能*：主辦單位專屬後台。以表格或列表列出該主辦已發布的活動，並在每一列提供「編輯」與「刪除」的按鈕與操作。

---

## 4. 路由骨架程式碼說明

我們已經在專案的 `app/routes/` 資料夾下建立了對應的程式碼骨架：
*   [app/routes/\_\_init\_\_.py](file:///Users/wilson/oa3243test/app/routes/__init__.py): Blueprint 集中管理與註冊註冊器。
*   [app/routes/auth.py](file:///Users/wilson/oa3243test/app/routes/auth.py): 包含 `register`、`login` 與 `logout` 路由簽名。
*   [app/routes/main.py](file:///Users/wilson/oa3243test/app/routes/main.py): 包含 `index` 首頁與 `event_detail` 詳情頁路由簽名。
*   [app/routes/event.py](file:///Users/wilson/oa3243test/app/routes/event.py): 包含 `publish`、`manage`、`edit` 與 `delete` 路由簽名。
*   [app/routes/favorite.py](file:///Users/wilson/oa3243test/app/routes/favorite.py): 包含 AJAX 收藏切換 `toggle_favorite` 與 `my_favorites` 路由簽名。
