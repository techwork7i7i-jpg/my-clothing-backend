# Clothing Store — Django REST API Backend

Production-ready API with **JWT authentication**, **secure file uploads**, **CORS**, and **SQLite/PostgreSQL** support.

## Project structure

```
backend/
├── config/           # Project settings, URLs, WSGI/ASGI
├── accounts/         # Register, login, JWT, profile
│   ├── models.py
│   ├── serializers.py
│   ├── views.py
│   ├── urls.py
│   └── permissions.py
├── files/            # Upload, list, delete user files
│   ├── models.py
│   ├── serializers.py
│   ├── views.py
│   ├── urls.py
│   ├── permissions.py
│   └── utils.py      # Secure paths & validation
├── media/            # Uploaded files (gitignored under uploads/)
├── manage.py
├── requirements.txt
└── .env.example
```

## Quick start (commands)

Run from the `backend/` directory.

### 1. Create virtual environment

```powershell
# Windows (PowerShell)
cd backend
python -m venv venv
.\venv\Scripts\Activate.ps1
```

```bash
# Linux / macOS
cd backend
python3 -m venv venv
source venv/bin/activate
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Environment file

```bash
# Windows
copy .env.example .env

# Linux / macOS
cp .env.example .env
```

Edit `.env` and set a strong `SECRET_KEY` before production.

### 4. Migrations

```bash
python manage.py makemigrations accounts files
python manage.py migrate
```

### 5. Create admin user (optional)

```bash
python manage.py createsuperuser
```

### 6. Run development server

```bash
python manage.py runserver
```

API base URL: `http://127.0.0.1:8000/api/`

### 7. Production (Gunicorn)

```bash
# Set DEBUG=False and ALLOWED_HOSTS in .env first
gunicorn config.wsgi:application --bind 0.0.0.0:8000 --workers 3
```

Collect static files for admin:

```bash
python manage.py collectstatic --noinput
```

---

## API endpoints

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| POST | `/api/auth/register/` | No | Register user |
| POST | `/api/auth/login/` | No | Login (JWT) |
| POST | `/api/auth/refresh/` | No | Refresh access token |
| POST | `/api/auth/logout/` | Yes | Blacklist refresh token |
| GET | `/api/auth/me/` | Yes | Current user profile |
| POST | `/api/files/upload/` | Yes | Upload file |
| GET | `/api/files/` | Yes | List user's files |
| GET | `/api/files/<id>/` | Yes | File metadata |
| DELETE | `/api/files/<id>/` | Yes | Delete file |

**Auth header for protected routes:**

```
Authorization: Bearer <access_token>
```

---

## Example API responses

### Register — `POST /api/auth/register/`

**Request:**

```json
{
  "email": "user@example.com",
  "password": "SecurePass123!",
  "password_confirm": "SecurePass123!",
  "first_name": "Jane",
  "last_name": "Doe"
}
```

**Response `201`:**

```json
{
  "success": true,
  "message": "Registration successful.",
  "user": {
    "id": 1,
    "email": "user@example.com",
    "username": "user",
    "first_name": "Jane",
    "last_name": "Doe",
    "date_joined": "2026-05-21T12:00:00Z"
  },
  "tokens": {
    "access": "eyJ0eXAiOiJKV1QiLCJhbGc...",
    "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc..."
  }
}
```

### Login — `POST /api/auth/login/`

**Request:**

```json
{
  "email": "user@example.com",
  "password": "SecurePass123!"
}
```

**Response `200`:**

```json
{
  "success": true,
  "message": "Login successful.",
  "user": {
    "id": 1,
    "email": "user@example.com",
    "username": "user",
    "first_name": "Jane",
    "last_name": "Doe",
    "date_joined": "2026-05-21T12:00:00Z"
  },
  "tokens": {
    "access": "eyJ0eXAiOiJKV1QiLCJhbGc...",
    "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc..."
  }
}
```

### Refresh token — `POST /api/auth/refresh/`

**Request:**

```json
{
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc..."
}
```

**Response `200`:**

```json
{
  "access": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
}
```

### Upload file — `POST /api/files/upload/`

**Request:** `multipart/form-data`

```
file: <binary>
```

**Response `201`:**

```json
{
  "success": true,
  "message": "File uploaded successfully.",
  "file": {
    "id": 1,
    "original_name": "photo.jpg",
    "file_url": "http://127.0.0.1:8000/media/uploads/1/abc123....jpg",
    "file_size": 245760,
    "size_mb": 0.23,
    "content_type": "image/jpeg",
    "created_at": "2026-05-21T12:05:00Z"
  }
}
```

### List user files — `GET /api/files/`

**Response `200`:**

```json
{
  "success": true,
  "count": 2,
  "files": [
    {
      "id": 1,
      "original_name": "photo.jpg",
      "file_url": "http://127.0.0.1:8000/media/uploads/1/abc123.jpg",
      "file_size": 245760,
      "size_mb": 0.23,
      "content_type": "image/jpeg",
      "created_at": "2026-05-21T12:05:00Z"
    }
  ]
}
```

### Delete file — `DELETE /api/files/1/`

**Response `200`:**

```json
{
  "success": true,
  "message": "File \"photo.jpg\" deleted successfully."
}
```

### Error example — `400`

```json
{
  "success": false,
  "errors": {
    "email": ["A user with this email already exists."]
  }
}
```

---

## Frontend integration (fetch)

```javascript
const API = 'http://127.0.0.1:8000/api';

// Login
const res = await fetch(`${API}/auth/login/`, {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ email: 'user@example.com', password: 'SecurePass123!' }),
});
const { tokens } = await res.json();

// Upload
const form = new FormData();
form.append('file', fileInput.files[0]);
await fetch(`${API}/files/upload/`, {
  method: 'POST',
  headers: { Authorization: `Bearer ${tokens.access}` },
  body: form,
});
```

Add your frontend origin to `CORS_ALLOWED_ORIGINS` in `.env`.

---

## PostgreSQL

Install dependencies (already in `requirements.txt`), then set:

```env
DATABASE_URL=postgres://USER:PASSWORD@HOST:5432/DATABASE_NAME
```

Run migrations again on the new database.

---

## Security notes

- Files are stored under `media/uploads/<user_id>/<random-uuid>.<ext>`
- Extension and size are validated before save
- Users can only access/delete their own files
- Set `DEBUG=False` and a strong `SECRET_KEY` in production
- Serve media via nginx or object storage; do not expose `DEBUG` media serving in production
