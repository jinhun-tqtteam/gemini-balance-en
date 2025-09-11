# Batch Add Proxy Servers - Fix Documentation

## Vấn đề đã được sửa

Chức năng "Batch Add Proxy Servers" không hoạt động với format proxy mới `IP:PORT:USER:PASS` do vẫn sử dụng regex pattern cũ.

## Các thay đổi đã thực hiện

### 1. **Cập nhật Regex Pattern** (`app/static/js/config_editor.js`)

**Trước:**
```javascript
const PROXY_REGEX = /(?:https?|socks5):\/\/(?:[^:@\/]+(?::[^@\/]+)?@)?(?:[^:\/\s]+)(?::\d+)?/g;
```

**Sau:**
```javascript
const PROXY_REGEX = /(?:\d{1,3}\.){3}\d{1,3}:\d{1,5}:[^:\s]+:[^:\s]+/g;
```

### 2. **Cập nhật UI Text** (`app/templates/config_editor.html`)

**Trước:**
```html
>Proxy server list supporting http and socks5 formats, e.g.:
http://user:pass@host:port or
socks5://host:port. Click buttons to batch add or delete.</small
```

**Sau:**
```html
>Proxy server list supporting IP:PORT:USER:PASS format, e.g.:
192.168.1.100:8080:username:password or
10.0.0.1:3128:admin:secret. Click buttons to batch add or delete.</small
```

### 3. **Cập nhật Placeholder Text**

**Trước:**
```html
placeholder="Paste proxy addresses here (e.g., http://user:pass@host:port or socks5://host:port)..."
```

**Sau:**
```html
placeholder="Paste proxy addresses here (e.g., 192.168.1.100:8080:username:password or 10.0.0.1:3128:admin:secret)..."
```

## Regex Pattern Chi Tiết

### Pattern: `/(?:\d{1,3}\.){3}\d{1,3}:\d{1,5}:[^:\s]+:[^:\s]+/g`

**Giải thích:**
- `(?:\d{1,3}\.){3}` - Ba nhóm 1-3 chữ số theo sau bởi dấu chấm
- `\d{1,3}` - Nhóm cuối 1-3 chữ số (IP address)
- `:` - Dấu hai chấm phân cách
- `\d{1,5}` - Port number (1-5 chữ số)
- `:` - Dấu hai chấm phân cách
- `[^:\s]+` - Username (không chứa dấu hai chấm hoặc space)
- `:` - Dấu hai chấm phân cách
- `[^:\s]+` - Password (không chứa dấu hai chấm hoặc space)

### Ví dụ Valid Matches:
✅ `192.168.1.100:8080:username:password`
✅ `127.0.0.1:3128:user123:pass456`
✅ `10.0.0.1:1080:admin:secret`
✅ `203.123.45.67:8888:test:test123`

### Ví dụ Invalid (sẽ bị bỏ qua):
❌ `192.168.1.100:8080:username` (thiếu password)
❌ `192.168.1.100:8080` (thiếu user và password)
❌ `http://proxy.com:8080` (format cũ)
❌ `socks5://proxy.com:1080` (format cũ)
❌ `invalid:format:test:test` (IP không hợp lệ)

## Cách sử dụng

1. **Mở Config Editor**
2. **Tìm section "Proxy Server List"**
3. **Click nút "Add Proxy"**
4. **Paste danh sách proxy theo format mới:**
   ```
   192.168.1.100:8080:username:password
   127.0.0.1:3128:user123:pass456
   10.0.0.1:1080:admin:secret
   ```
5. **Click "Confirm"**

## Testing

Để test regex pattern, mở file `tmp_rovodev_test_regex.html` trong browser và kiểm tra kết quả.

## Logic Flow

1. **User paste text** vào textarea
2. **JavaScript sử dụng `PROXY_REGEX.match()`** để extract valid proxies
3. **Combine với existing proxies** và remove duplicates
4. **Update UI** với danh sách proxy mới
5. **Show notification** với số lượng proxy đã thêm

## Files Đã Cập Nhật

- ✅ `app/static/js/config_editor.js` - Regex pattern
- ✅ `app/templates/config_editor.html` - UI text và placeholder
- ✅ `app/service/proxy/proxy_check_service.py` - Backend validation
- ✅ `app/service/client/api_client.py` - Proxy usage
- ✅ `app/utils/proxy_helper.py` - Helper functions
- ✅ `app/config/config.py` - Configuration documentation

## Kết quả

🎉 **Chức năng Batch Add Proxy Servers hiện đã hoạt động đúng với format mới `IP:PORT:USER:PASS`**