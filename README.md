# URL Shortener + Analytics

- JWT auth (SimpleJWT), OpenAPI (Swagger/Redoc)
- CRUD Link, Redirect `/r/<slug>/`, Thống kê 7/30 ngày, Top, QR
- **Auto-seed**:  
  - **admin / password123** (superuser)  
  - **hai / password123**
- Root `/` → **redirect sang `/ui/`** (UI demo sẵn)

---

## 🚀 Chạy bằng Docker — **1 lệnh duy nhất**
```bash
docker compose up --build
```

Sau khi chạy:
- UI demo: http://localhost:8000/ui/
- Swagger: http://localhost:8000/api/schema/swagger-ui/
- Redoc: http://localhost:8000/api/schema/redoc/
- Redirect mẫu:  
  - `http://localhost:8000/r/ggl/` → Google  
  - `http://localhost:8000/r/yt/`  → YouTube  
  - `http://localhost:8000/r/uit/` → UIT  
  - `http://localhost:8000/r/drf/` → DRF

> Lần đầu container sẽ tự `migrate` và **seed** dữ liệu mẫu vào `db.sqlite3`.

---

## 🔐 Xác thực (JWT)

### 1) Đăng nhập
**POST** `/api/auth/login/`  
Body:
```json
{ "username": "hai", "password": "password123" }
```
Response:
```json
{ "access": "<JWT_ACCESS>", "refresh": "<JWT_REFRESH>" }
```

### 2) Dùng token
Thêm header cho API khác:
```
Authorization: Bearer <JWT_ACCESS>
```

### 3) Refresh access token
**POST** `/api/auth/refresh/`  
Body:
```json
{ "refresh": "<JWT_REFRESH>" }
```
Response:
```json
{ "access": "<NEW_JWT_ACCESS>" }
```

> Swagger: bấm **Authorize** (icon 🔒) → dán `Bearer <JWT_ACCESS>`.

---

## 🔗 Links (CRUD, tìm kiếm & phân trang)

### A) List + Search + Pagination
**GET** `/api/links/`  
Query:
- `q=<text>` — tìm theo `title` (icontains)
- `owner=<user_id>` — chỉ **admin** thấy hiệu lực (lọc theo owner khác)
- `created_at=YYYY-MM-DD` — lọc theo ngày tạo
- `page=<n>` — phân trang (page size mặc định 10)

Response (chuẩn DRF Pagination):
```json
{
  "count": 12,
  "next": "http://localhost:8000/api/links/?page=2",
  "previous": null,
  "results": [
    {
      "id": 1,
      "title": "Google",
      "target_url": "https://www.google.com",
      "slug": "ggl",
      "is_active": true,
      "created_at": "2025-09-13T10:00:00Z",
      "owner_username": "hai",
      "clicks_count": 8
    }
  ]
}
```

**curl mẫu:**
```bash
# List của chính mình
curl -H "Authorization: Bearer <ACCESS>" http://localhost:8000/api/links/ | jq

# Tìm theo title
curl -H "Authorization: Bearer <ACCESS>" "http://localhost:8000/api/links/?q=uit" | jq

# (Admin) xem link của user id=2
curl -H "Authorization: Bearer <ADMIN_ACCESS>" "http://localhost:8000/api/links/?owner=2" | jq
```

### B) Tạo link
**POST** `/api/links/`  
Body:
```json
{
  "title": "UIT News",
  "target_url": "https://www.uit.edu.vn",
  "slug": "uit-news"  // (tuỳ chọn) — nếu bỏ trống, server tự sinh slug 6 ký tự
}
```
Response:
```json
{
  "id": 12,
  "title": "UIT News",
  "target_url": "https://www.uit.edu.vn",
  "slug": "uit-news",
  "is_active": true,
  "created_at": "2025-09-13T12:34:56Z",
  "owner_username": "hai",
  "clicks_count": 0
}
```

> Nếu `slug` bị trùng:
```json
{ "slug": ["Slug này đã được sử dụng. Hãy chọn slug khác."] }
```

**curl mẫu:**
```bash
curl -X POST http://localhost:8000/api/links/   -H "Authorization: Bearer <ACCESS>"   -H "Content-Type: application/json"   -d '{"title":"UIT News","target_url":"https://www.uit.edu.vn"}' | jq
```

### C) Chi tiết
**GET** `/api/links/{id}/`

### D) Sửa (PATCH)
**PATCH** `/api/links/{id}/`  
- Cho phép sửa: `title`, `target_url`, `slug`  
- `is_active` đang **read-only** (không sửa qua API trong bản demo này)

**curl mẫu:**
```bash
curl -X PATCH http://localhost:8000/api/links/12/   -H "Authorization: Bearer <ACCESS>"   -H "Content-Type: application/json"   -d '{"title":"UIT News (updated)"}' | jq
```

### E) Xoá
**DELETE** `/api/links/{id}/` → `204 No Content`

---

## 📈 Analytics

### 1) Thống kê theo ngày (7 hoặc 30 ngày)
**GET** `/api/links/{id}/stats/?range=7d|30d`  
Response:
```json
{
  "range": "7d",
  "total_clicks": 23,
  "daily_clicks": [
    {"date":"2025-09-07","count":3},
    {"date":"2025-09-08","count":5}
  ]
}
```

**curl mẫu:**
```bash
curl -H "Authorization: Bearer <ACCESS>"   "http://localhost:8000/api/links/12/stats/?range=7d" | jq
```

### 2) Top link toàn hệ thống
**GET** `/api/stats/top/?limit=10`  
Response:
```json
[
  { "id": 4, "title": "Django REST Framework", "slug": "drf", "owner": "admin", "click_count": 11 }
]
```

---

## 🧾 QR Code
**GET** `/api/links/{id}/qr/` → PNG (QR của short link)  
**curl mẫu:**
```bash
curl -H "Authorization: Bearer <ACCESS>"   -o qr.png http://localhost:8000/api/links/12/qr/
```

---

## 🔀 Redirect (công khai)
**GET** `/r/{slug}/` → Ghi **Click** + 302 redirect đến `target_url`.

> **Lưu ý có “/** cuối**:** pattern định nghĩa `/r/<slug>/` (có dấu `/` kết thúc).

**Ghi log click gồm:**
- thời điểm (`ts`), `referrer`, `user_agent`
- `ip_hash` (SHA-256 của IP + `SECRET_KEY`) → **không lưu IP thô**.

---

## 🧰 UI demo
- Trang: `http://localhost:8000/ui/`
- Chức năng: Đăng nhập JWT → tạo link → xem danh sách → **Stats (biểu đồ)** → **QR** → Edit/Xoá.
- UI gọi same-origin API → **không cần CORS**.

---

## ⚙️ Biến môi trường
File `.env` (đã có sẵn):
```
SECRET_KEY=dev-secret-please-change
DEBUG=1
ALLOWED_HOSTS=*
TIME_ZONE=Asia/Ho_Chi_Minh
ACCESS_TOKEN_MINUTES=120
```

> ⚠️ Đổi `SECRET_KEY` ⇒ **token cũ** sẽ **invalid** (phải login lại).

---

## 👨‍💻 Chạy local (không Docker)
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env  # nếu cần
python manage.py migrate
python manage.py runserver
```
- UI: `http://127.0.0.1:8000/ui/`
- Swagger: `http://127.0.0.1:8000/api/schema/swagger-ui/`

---

## ❗ Troubleshooting

- **401 / Token invalid or expired**  
  - Đăng nhập lại lấy **access** mới.  
  - Kiểm tra header có đúng `Authorization: Bearer <token>` chưa.  
  - Bạn vừa đổi `SECRET_KEY`? → token cũ invalid.  
  - Trên Swagger: **Logout** trong Authorize rồi dán token mới.

- **Unauthorized trên `/api/auth/login/`**  
  - Sai username/password hoặc user chưa tồn tại. Dùng user seed:
    - `hai/password123` hoặc `admin/password123`.

- **404 tại `/`**  
  - Repo này đã cấu hình **redirect `/` → `/ui/`**.  
  - Nếu tự làm: thêm vào `urlshortener/urls.py`
    ```python
    from django.views.generic import RedirectView
    urlpatterns = [
      path('', RedirectView.as_view(url='/ui/', permanent=False)),
      ...
    ]
    ```

- **Pylance “Cannot access attribute id for class Click”** (VS Code)  
  - Cảnh báo do Django tạo `id` tự động. Runtime vẫn OK.  
  - Có thể thêm `id = models.BigAutoField(primary_key=True)` vào model để Pylance hết báo.

- **Muốn seed lại dữ liệu**  
  - Xoá `db.sqlite3` → `docker compose up --build` (hoặc `python manage.py migrate` khi chạy local).

---

## 📚 Ghi chú triển khai
- `slug` unique, tối đa 10 ký tự. Không gửi `slug` → server tự sinh 6 ký tự (chữ + số).  
- `is_active` hiện **read-only** qua API (demo).  
- Click tracking: đếm khi gọi `/r/<slug>/`. IP được băm SHA-256 với `SECRET_KEY` (**không lưu IP thô**).

---

## 📎 OpenAPI
- JSON schema: `/api/schema/`  
- Swagger: `/api/schema/swagger-ui/`  
- Redoc: `/api/schema/redoc/`  
Trong Swagger, bấm **Authorize** rồi dán `Bearer <access>` để gọi thử API có bảo vệ.
