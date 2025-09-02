# Gemini Balance - Proxy và Cân Bằng Tải cho Gemini API

<p align="center">
  <a href="https://trendshift.io/repositories/13692" target="_blank">
    <img src="https://trendshift.io/api/badge/repositories/13692" alt="snailyp%2Fgemini-balance | Trendshift" style="width: 250px; height: 55px;" width="250" height="55"/>
  </a>
</p>

<p align="center">
  <a href="https://www.python.org/"><img src="https://img.shields.io/badge/Python-3.9%2B-blue.svg" alt="Python"></a>
  <a href="https://fastapi.tiangolo.com/"><img src="https://img.shields.io/badge/FastAPI-0.100%2B-green.svg" alt="FastAPI"></a>
  <a href="https://www.uvicorn.org/"><img src="https://img.shields.io/badge/Uvicorn-running-purple.svg" alt="Uvicorn"></a>
  <a href="https://t.me/+soaHax5lyI0wZDVl"><img src="https://img.shields.io/badge/Telegram-Group-blue.svg?logo=telegram" alt="Telegram Group"></a>
</p>

> ⚠️ **Quan trọng**: Dự án này được cấp phép theo giấy phép [CC BY-NC 4.0](LICENSE). **Mọi hình thức dịch vụ bán lại thương mại đều bị cấm**.

---

## 📖 Giới Thiệu Dự Án

**Gemini Balance** là một ứng dụng được xây dựng bằng Python FastAPI, được thiết kế để cung cấp các chức năng proxy và cân bằng tải cho Google Gemini API. Nó cho phép bạn quản lý nhiều Gemini API Keys và thực hiện luân phiên khóa, xác thực, lọc mô hình và giám sát trạng thái thông qua cấu hình đơn giản.

<details>
<summary>📂 Xem Cấu Trúc Dự Án</summary>

```plaintext
app/
├── config/       # Quản lý cấu hình
├── core/         # Logic ứng dụng cốt lõi (FastAPI, middleware)
├── database/     # Models và kết nối cơ sở dữ liệu
├── domain/       # Các đối tượng domain nghiệp vụ
├── exception/    # Exceptions tùy chỉnh
├── handler/      # Xử lý request và response
├── log/          # Cấu hình logging
├── middleware/   # FastAPI middleware
├── router/       # API routes (Gemini, OpenAI, admin)
├── scheduler/    # Tác vụ định kỳ
├── service/      # Dịch vụ logic nghiệp vụ
├── static/       # File tĩnh (CSS, JS)
├── templates/    # HTML templates
└── utils/        # Các hàm tiện ích
```
</details>

---

## ✨ Tính Năng Nổi Bật

*   **Cân Bằng Tải Đa Khóa**: Hỗ trợ cấu hình nhiều Gemini API Keys để tự động luân phiên tuần tự
*   **Cấu Hình Trực Quan**: Các cấu hình được sửa đổi thông qua web interface có hiệu lực ngay lập tức
*   **Tương Thích API Dual Protocol**: Hỗ trợ cả định dạng Gemini và OpenAI API
    *   OpenAI Base URL: `http://localhost:8000(/hf)/v1`
    *   Gemini Base URL: `http://localhost:8000(/gemini)/v1beta`
*   **Chat Hình-Văn & Chỉnh Sửa**: Hỗ trợ chat với hình ảnh và tạo/chỉnh sửa hình ảnh
*   **Tìm Kiếm Web**: Tích hợp khả năng tìm kiếm web trực tiếp trong chat
*   **Giám Sát Trạng Thái Khóa**: Giao diện web để giám sát trạng thái API keys thời gian thực
*   **Logging Chi Tiết**: Hệ thống log chi tiết cho việc debug và giám sát
*   **Thử Lại Tự Động**: Tự động thử lại request thất bại và vô hiệu hóa keys có vấn đề
*   **Tương Thích API Toàn Diện**: Embeddings API, Image Generation API
*   **Hỗ Trợ Proxy**: HTTP/SOCKS5 proxy support
*   **Docker Support**: Images cho cả kiến trúc AMD và ARM

---

## 🚀 Bắt Đầu Nhanh

### Lựa Chọn 1: Docker Compose (Khuyến Nghị)

1.  **Chuẩn bị môi trường**:
    ```bash
    # Tải docker-compose.yml từ repository
    # Sao chép .env.example thành .env
    cp .env.example .env
    # Chỉnh sửa cấu hình trong .env
    ```

2.  **Khởi động dịch vụ**:
    ```bash
    docker-compose up -d
    ```

### Lựa Chọn 2: Docker Command

```bash
# Pull image
docker pull ghcr.io/snailyp/gemini-balance:latest

# Chạy container
docker run -d -p 8000:8000 --name gemini-balance \
  -v ./data:/app/data \
  --env-file .env \
  ghcr.io/snailyp/gemini-balance:latest
```

### Lựa Chọn 3: Phát Triển Cục Bộ

```bash
git clone https://github.com/snailyp/gemini-balance.git
cd gemini-balance
pip install -r requirements.txt
cp .env.example .env
# Chỉnh sửa .env
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

---

## ⚙️ Endpoints API

### Gemini API Format (`/gemini/v1beta`)
*   `GET /models`: Liệt kê các mô hình Gemini
*   `POST /models/{model_name}:generateContent`: Tạo nội dung
*   `POST /models/{model_name}:streamGenerateContent`: Tạo nội dung dạng stream

### OpenAI API Format
#### Hugging Face Compatible (`/hf/v1`)
*   `GET /hf/v1/models`: Liệt kê mô hình
*   `POST /hf/v1/chat/completions`: Chat completion
*   `POST /hf/v1/embeddings`: Text embeddings
*   `POST /hf/v1/images/generations`: Tạo hình ảnh

#### Standard OpenAI (`/openai/v1`)
*   `GET /openai/v1/models`: Liệt kê mô hình
*   `POST /openai/v1/chat/completions`: Chat completion
*   `POST /openai/v1/embeddings`: Text embeddings
*   `POST /openai/v1/images/generations`: Tạo hình ảnh

---

## 🔧 Cấu Hình Chính

### Cấu Hình Cơ Bản

| Mục Cấu Hình | Mô Tả | Giá Trị Mặc Định |
| :--- | :--- | :--- |
| `DATABASE_TYPE` | `mysql` hoặc `sqlite` | `mysql` |
| `API_KEYS` | **Bắt buộc** - Danh sách Gemini API keys | `[]` |
| `ALLOWED_TOKENS` | **Bắt buộc** - Danh sách access tokens | `[]` |
| `AUTH_TOKEN` | Token siêu quản trị | `sk-123456` |
| `BASE_URL` | URL cơ sở Gemini API | `https://generativelanguage.googleapis.com/v1beta` |
| `MAX_FAILURES` | Số lần thất bại tối đa mỗi key | `3` |
| `MAX_RETRIES` | Số lần thử lại tối đa | `3` |
| `TIME_OUT` | Timeout request (giây) | `300` |

### Cấu Hình Database

#### MySQL (Khuyến nghị)
```env
DATABASE_TYPE=mysql
MYSQL_HOST=localhost
MYSQL_PORT=3306
MYSQL_USER=your_db_user
MYSQL_PASSWORD=your_db_password
MYSQL_DATABASE=defaultdb
```

#### SQLite (Development)
```env
DATABASE_TYPE=sqlite
SQLITE_DATABASE=./data/gemini_balance.db
```

### Cấu Hình Tính Năng

```env
# Mô hình hỗ trợ tìm kiếm web
SEARCH_MODELS=["gemini-2.0-flash-exp"]

# Mô hình hỗ trợ tạo hình ảnh
IMAGE_MODELS=["gemini-2.0-flash-exp"]

# Bật thực thi mã
TOOLS_CODE_EXECUTION_ENABLED=true

# Proxy support
PROXIES=["http://proxy1:8080", "socks5://proxy2:1080"]

# Stream optimization
STREAM_OPTIMIZER_ENABLED=true
FAKE_STREAM_ENABLED=true
```

---

## 📚 Hướng Dẫn Sử Dụng

### 1. Truy Cập Web Interface

- **Trang chủ**: `http://localhost:8000`
- **Trạng thái Keys**: `http://localhost:8000/keys_status`
- **Cấu hình**: `http://localhost:8000/config_editor`
- **Log lỗi**: `http://localhost:8000/error_logs`

### 2. Sử Dụng API

#### Chat với OpenAI Format
```bash
curl -X POST "http://localhost:8000/hf/v1/chat/completions" \
-H "Authorization: Bearer sk-123456" \
-H "Content-Type: application/json" \
-d '{
  "model": "gemini-1.5-flash",
  "messages": [{"role": "user", "content": "Xin chào!"}],
  "stream": true
}'
```

#### Tìm kiếm Web
```bash
curl -X POST "http://localhost:8000/hf/v1/chat/completions" \
-H "Authorization: Bearer sk-123456" \
-H "Content-Type: application/json" \
-d '{
  "model": "gemini-2.0-flash-exp-search",
  "messages": [{"role": "user", "content": "Tin tức AI mới nhất"}]
}'
```

#### Tạo Hình Ảnh
```bash
curl -X POST "http://localhost:8000/hf/v1/images/generations" \
-H "Authorization: Bearer sk-123456" \
-H "Content-Type: application/json" \
-d '{
  "prompt": "Một con mèo trong vườn",
  "n": 1,
  "size": "1024x1024"
}'
```

---

## 🚨 Khắc Phục Sự Cố

### Lỗi Thường Gặp

1. **"No valid API keys available"**
   - Kiểm tra API keys tại Google AI Studio
   - Xem log chi tiết tại `/error_logs`

2. **"Database connection failed"**
   ```bash
   # Kiểm tra MySQL connection
   mysql -h localhost -u your_user -p
   ```

3. **Container không khởi động**
   ```bash
   # Kiểm tra logs
   docker-compose logs -f gemini-balance
   
   # Kiểm tra port conflict
   netstat -tulpn | grep 8000
   ```

### Debug Mode
```env
LOG_LEVEL=DEBUG
```

---

## 🔒 Bảo Mật

### Khuyến Nghị Bảo Mật

1. **Sử dụng HTTPS** trong môi trường sản xuất
2. **Thay đổi AUTH_TOKEN** mặc định
3. **Giới hạn truy cập** đến database
4. **Cập nhật thường xuyên** để vá lỗi bảo mật
5. **Backup dữ liệu** định kỳ

### Cấu Hình Firewall
```bash
# Chỉ cho phép truy cập port 8000
ufw allow 8000/tcp
ufw enable
```

---

## 🤝 Đóng Góp

Chúng tôi hoan nghênh Pull Requests hoặc Issues.

[![Contributors](https://contrib.rocks/image?repo=snailyp/gemini-balance)](https://github.com/snailyp/gemini-balance/graphs/contributors)

---

## 🙏 Lời Cảm Ơn

*   [PicGo](https://www.picgo.net/)
*   [SM.MS](https://smms.app/)
*   [CloudFlare-ImgBed](https://github.com/MarSeventh/CloudFlare-ImgBed)

Cảm ơn [DigitalOcean](https://m.do.co/c/b249dd7f3b4c) đã cung cấp hạ tầng cloud ổn định!

---

## 📄 Giấy Phép

Dự án này được cấp phép theo [CC BY-NC 4.0](LICENSE) (Attribution-NonCommercial).

**Không được phép sử dụng cho mục đích thương mại.**