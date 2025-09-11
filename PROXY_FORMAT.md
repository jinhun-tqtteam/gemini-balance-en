# Proxy Configuration Guide

## New Proxy Format

The project now uses a new proxy format: **IP:PORT:USER:PASS**

### Format Specification

```
IP:PORT:USER:PASS
```

Where:
- **IP**: Proxy server IP address
- **PORT**: Proxy server port (1-65535)
- **USER**: Username for proxy authentication
- **PASS**: Password for proxy authentication

### Examples

```bash
# Valid proxy formats
192.168.1.100:8080:username:password
127.0.0.1:3128:admin:secret123
203.123.45.67:1080:user123:pass456
```

### Configuration

Add proxies to your configuration:

```python
PROXIES = [
    "192.168.1.100:8080:username:password",
    "10.0.0.1:3128:admin:secret",
    "203.123.45.67:1080:user:pass"
]
```

### Environment Variables

```bash
PROXIES='["192.168.1.100:8080:username:password","10.0.0.1:3128:admin:secret"]'
```

### How It Works

1. **Parsing**: The system automatically parses `IP:PORT:USER:PASS` format
2. **Conversion**: Converts to httpx compatible format: `http://username:password@ip:port`
3. **Usage**: Uses converted format for all HTTP requests through the proxy

### Validation

The system validates:
- ✅ Exactly 4 parts separated by colons
- ✅ Valid port number (1-65535)
- ✅ Non-empty IP and port
- ✅ Username and password present

### Migration from Old Format

**Old format** (no longer supported):
```
http://proxy.example.com:8080
https://proxy.example.com:3128
socks5://proxy.example.com:1080
```

**New format**:
```
192.168.1.100:8080:username:password
10.0.0.1:3128:admin:secret
203.123.45.67:1080:user:pass
```

### Files Updated

- `app/service/proxy/proxy_check_service.py` - Proxy validation and checking
- `app/service/client/api_client.py` - HTTP client proxy usage
- `app/utils/proxy_helper.py` - Proxy format conversion utilities
- `app/config/config.py` - Configuration documentation

### Testing

The proxy format has been tested with various scenarios:
- Valid IP:PORT:USER:PASS combinations ✅
- Invalid formats (missing parts, invalid ports) ✅
- Conversion to httpx compatible format ✅