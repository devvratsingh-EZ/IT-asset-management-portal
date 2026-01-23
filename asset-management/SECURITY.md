# Security Implementation Guide

## Cookie Security Configuration

### Overview
Your application implements a two-token JWT authentication system with production-grade cookie security.

### Cookie Security Features

#### Current Implementation (Development Mode: DEBUG=True)
```
Secure Flag: ❌ secure=False (HTTP allowed for local testing)
HttpOnly: ✅ httponly=True
SameSite: ✅ samesite="strict"
Max-Age: ✅ 24 hours
Path: ✅ /api/auth only
```

#### Production Implementation (DEBUG=False)
```
Secure Flag: ✅ secure=True (HTTPS required)
HttpOnly: ✅ httponly=True
SameSite: ✅ samesite="strict"
Max-Age: ✅ 24 hours
Path: ✅ /api/auth only
```

### What Each Flag Does

#### `secure=True/False`
- **Development (secure=False)**: Cookie sent over HTTP and HTTPS
  - Useful for local testing without SSL certificate
  - Network sniffing possible on unencrypted HTTP
  
- **Production (secure=True)**: Cookie ONLY sent over HTTPS
  - Browser refuses to send cookie over HTTP
  - Prevents man-in-the-middle (MITM) attacks
  - Requires valid SSL/TLS certificate

#### `httponly=True`
- JavaScript **cannot** access this cookie
- Prevents XSS (Cross-Site Scripting) attacks
- Refresh token is secure from compromised JavaScript

#### `samesite="strict"`
- Cookie **not** sent on cross-site requests
- Strongest CSRF (Cross-Site Request Forgery) protection
- User's cookies can't be exploited by attacker websites

#### `max_age=86400` (24 hours)
- Cookie automatically expires after 24 hours
- Forces re-authentication if token is stolen
- Reduces impact of token compromise

#### `path="/api/auth"`
- Cookie only sent to /api/auth endpoints
- Reduces exposure of token
- Other routes don't need the cookie

### Security Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│ USER LOGIN                                                      │
└─────────────────────────────────────────────────────────────────┘
                             ↓
┌─────────────────────────────────────────────────────────────────┐
│ SERVER GENERATES TOKENS                                         │
│ ├─ Access Token (15 min JWT)                                    │
│ │  └─ Sent in response body (frontend stores in memory)        │
│ └─ Refresh Token (24 hrs random string)                         │
│    └─ Sent in HttpOnly cookie (browser handles automatically)  │
└─────────────────────────────────────────────────────────────────┘
                             ↓
┌─────────────────────────────────────────────────────────────────┐
│ BROWSER RECEIVES RESPONSE                                       │
│ ├─ Access Token: Stored in JavaScript variable (memory only)   │
│ └─ Cookie: Stored by browser, JavaScript can't access it       │
│    (Browser automatically includes in future requests)          │
└─────────────────────────────────────────────────────────────────┘
                             ↓
┌─────────────────────────────────────────────────────────────────┐
│ USER MAKES API REQUEST                                          │
│ ├─ Access Token: JavaScript adds to Authorization header       │
│ ├─ Refresh Token: Browser automatically adds to cookies        │
│ └─ HTTPS Encryption: Entire request encrypted in transit       │
│    [ENCRYPTED: Authorization: Bearer <token> + Cookie: <token>]│
└─────────────────────────────────────────────────────────────────┘
```

### Threat Model & Mitigations

| Threat | Risk | Mitigation |
|--------|------|-----------|
| **XSS Attack** | Attacker injects JS, steals tokens | ✅ HttpOnly cookie (JS can't read) + in-memory access token |
| **CSRF Attack** | Attacker tricks browser to send request | ✅ SameSite=Strict cookie (no cross-site requests) |
| **MITM Attack** | Network sniffing, token theft | ✅ Secure flag + HTTPS (traffic encrypted) |
| **Token Expiration** | Old stolen token remains valid | ✅ 15-min access token + 24-hr refresh token |
| **Token Rotation** | Stolen token gets reused | ✅ New refresh token on each refresh |

### Deployment Checklist

#### Before Production Deployment

- [ ] **Enable HTTPS**
  ```bash
  # Install SSL certificate (Let's Encrypt recommended)
  # Configure reverse proxy (nginx/Apache) with SSL
  # Redirect all HTTP traffic to HTTPS
  ```

- [ ] **Set DEBUG=False in .env**
  ```bash
  # This automatically enables:
  # - secure=True (HTTPS-only cookies)
  # - Proper logging of production mode
  DEBUG=False
  ```

- [ ] **Change JWT_SECRET_KEY**
  ```bash
  # Generate strong random key
  openssl rand -hex 32
  # Copy result to .env
  JWT_SECRET_KEY=abc123def456...
  ```

- [ ] **Verify Cookie Settings in Logs**
  ```
  Expected in production:
  PRODUCTION: Refresh cookie set with secure=True (HTTPS required)
  
  This means:
  - Cookies only sent over HTTPS
  - Browser refuses HTTP transmission
  ```

- [ ] **Test Cookie Transmission**
  ```bash
  # Open browser DevTools → Application → Cookies
  # Verify refresh_token cookie exists
  # In production, it should show secure: ✓ (green checkmark)
  ```

### Local Development Setup

For development, the current configuration allows HTTP:

```bash
# Your .env (development)
DEBUG=True
```

Logs will show:
```
DEVELOPMENT: Refresh cookie set with secure=False (HTTP allowed)
```

This is safe for local development because:
- No production data involved
- Localhost traffic not intercepted
- Quick development iterations

### Production Example (.env)

```bash
# Production environment
DEBUG=False
JWT_SECRET_KEY=<random-32-byte-hex-string>
DB_HOST=production-db-server.example.com
DB_USER=prod_app_user
DB_PASSWORD=<strong-password>
```

When deployed with this configuration:
- Cookies automatically require HTTPS
- Server logs show "PRODUCTION" security mode
- All authentication events logged with file/line numbers
- Token refresh happens transparently on expiration

### Monitoring & Logging

Check your server logs for authentication events:

```
2026-01-23 04:27:47 - routes.auth - WARNING - [auth.py:40] - PRODUCTION: Refresh cookie set with secure=True
2026-01-23 04:27:47 - services.auth - INFO - [auth_service.py:35] - Access token created for user 'itadmin'
2026-01-23 04:27:47 - services.auth - INFO - [auth_service.py:46] - Access token verified for user 'itadmin'
```

### FAQ

**Q: Why HttpOnly instead of storing in localStorage?**
A: HttpOnly cookies can't be accessed by JavaScript, protecting against XSS attacks. localStorage is vulnerable to JavaScript injection.

**Q: Why separate access and refresh tokens?**
A: Access tokens are short-lived (15 min), limiting damage if stolen. Refresh tokens are long-lived but more tightly controlled.

**Q: Is the refresh token encrypted?**
A: The token value itself is not encrypted. Instead:
- It's transmitted over HTTPS (encryption layer)
- It's stored in an HttpOnly cookie (JavaScript can't steal it)
- It's stored in the database (not in response body)
- It's long enough (32 bytes) to be cryptographically secure

**Q: What if someone steals the refresh token?**
A: They can get a new access token, but:
- Tokens only work from the same origin (SameSite=Strict)
- Tokens expire after 24 hours
- New tokens are rotated on each refresh
- Access token is only valid for 15 minutes

**Q: Do I need to change anything for HTTPS?**
A: Set `DEBUG=False` in your production .env. Everything else is automatic:
```bash
# Your code handles this automatically:
is_production = not settings.DEBUG
secure = is_production  # True in production, False in development
```
