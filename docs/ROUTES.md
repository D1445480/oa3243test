# 路由與頁面設計 (API Design)

本文件依據 PRD 與架構設計，定義系統所需的 URL 路徑、HTTP 方法與對應的處理邏輯，作為前後端開發的實作依據。

## 1. 路由總覽表格

| 功能 | HTTP 方法 | URL 路徑 | 對應模板 | 說明 |
| --- | --- | --- | --- | --- |
| **首頁** | GET | `/` | `index.html` | 顯示近期熱門活動與分類導覽列 |
| **活動列表總覽** | GET | `/events` | `events/list.html` | 顯示所有活動，支援依分類過濾 |
| **活動搜尋** | GET | `/events/search` | `events/list.html` | 透過關鍵字查詢活動，與列表頁共用模板 |
| **活動詳細資訊** | GET | `/events/<id>` | `events/detail.html` | 顯示單筆活動的完整時間、地點與說明 |
| **新增活動頁面** | GET | `/events/new` | `events/form.html` | 顯示新增活動的表單 (僅主辦單位) |
| **送出新增活動** | POST | `/events/new` | — | 接收表單並將資料寫入 DB，完成後重導 |
| **編輯活動頁面** | GET | `/events/<id>/edit` | `events/form.html` | 顯示活動編輯表單 (預填舊資料) |
| **送出更新活動** | POST | `/events/<id>/edit` | — | 接收修改後的資料，更新 DB |
| **刪除活動** | POST | `/events/<id>/delete`| — | 自資料庫移除活動並重導向 |
| **會員註冊頁** | GET | `/auth/register` | `auth/register.html`| 顯示註冊表單 |
| **送出註冊** | POST | `/auth/register` | — | 處理帳號建立與密碼加密 |
| **會員登入頁** | GET | `/auth/login` | `auth/login.html` | 顯示登入表單 |
| **送出登入** | POST | `/auth/login` | — | 驗證帳號密碼，建立 Session |
| **會員登出** | GET | `/auth/logout` | — | 清除 Session 並重導向回首頁 |

---

## 2. 每個路由的詳細說明

### `main.py`
- **`index()` (GET `/`)**
  - 輸入：無
  - 處理邏輯：查詢最新即將到來的活動 (例如取前 6 筆)，並取得所有分類供導覽。
  - 輸出：渲染 `index.html`。

### `events.py`
- **`list_events()` (GET `/events`)**
  - 輸入：URL 參數 `category` (選填，分類 ID)。
  - 處理邏輯：若有 `category`，則過濾出該分類的活動；否則回傳所有活動 (依日期排序)。
  - 輸出：渲染 `events/list.html`。
- **`search_events()` (GET `/events/search`)**
  - 輸入：URL 參數 `q` (關鍵字)。
  - 處理邏輯：使用 SQL `LIKE` 模糊搜尋標題或內容符合的活動。
  - 輸出：渲染 `events/list.html`，傳入搜尋結果。
- **`event_detail(id)` (GET `/events/<id>`)**
  - 輸入：URL 路徑參數 `id` (活動 ID)。
  - 處理邏輯：透過 `Event.query.get_or_404(id)` 取得活動。
  - 輸出：渲染 `events/detail.html`。
- **`create_event()` (GET/POST `/events/new`)**
  - 處理邏輯：GET 時回傳表單；POST 時驗證欄位，並將新 Event 存入資料庫。需驗證使用者登入狀態。
- **`edit_event(id)` (GET/POST `/events/<id>/edit`)**
  - 處理邏輯：GET 時回傳帶有資料的表單；POST 時更新欄位。需驗證登入狀態且為活動發布者。
- **`delete_event(id)` (POST `/events/<id>/delete`)**
  - 處理邏輯：刪除指定 ID 的活動，需驗證權限。

### `auth.py`
- **`register()` (GET/POST `/auth/register`)**
  - 處理邏輯：GET 顯示表單。POST 驗證 Email 是否重複，建立新 `User` 並 Hash 密碼。
- **`login()` (GET/POST `/auth/login`)**
  - 處理邏輯：GET 顯示表單。POST 比對信箱與密碼，成功則記錄至 `session`。
- **`logout()` (GET `/auth/logout`)**
  - 處理邏輯：清空 `session` 內的資料並重導回首頁。

---

## 3. Jinja2 模板清單

所有的模板將繼承自 `base.html`，以維持統一的導覽列與整體外觀。

- **`base.html`**：共用主版型 (Header, Footer, 導覽列)。
- **`index.html`**：首頁，展示平台理念與近期活動預覽。
- **`events/list.html`**：活動列表與搜尋結果呈現。
- **`events/detail.html`**：活動專屬頁面，呈現詳細圖文與報名/收藏按鈕。
- **`events/form.html`**：共用的新增與編輯活動表單頁。
- **`auth/login.html`**：使用者登入頁面。
- **`auth/register.html`**：使用者註冊頁面。
