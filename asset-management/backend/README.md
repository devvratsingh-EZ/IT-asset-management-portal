# IT Asset Management - Backend

FastAPI backend server with MySQL database for the IT Asset Management system.

## Quick Start

### 1. Prerequisites
- Python 3.8+
- MySQL Server running locally
- MySQL user: `root`, password: `root`

### 2. Setup
```bash
cd backend

# Create virtual environment (optional but recommended)
python -m venv venv
source venv/bin/activate  # Linux/Mac
# or: venv\Scripts\activate  # Windows

# Install dependencies
pip install -r requirements.txt
```

### 3. Build Frontend
```bash
cd ..
npm install
npm run build
cd backend
```

### 4. Run Server
```bash
python main.py
# or: uvicorn main:app --reload --port 8000
```

### 5. Access
- **App**: http://localhost:8000
- **Login**: http://localhost:8000/login
- **Asset Addition**: http://localhost:8000/asset_addition
- **API Docs**: http://localhost:8000/docs

## Database

MySQL database `ITAssetData` is created automatically on startup.

### Tables
- **AuthData**: User authentication (username, password, full_name, email)

### Default Users
| Username | Password | Full Name |
|----------|----------|-----------|
| itadmin | pass123 | IT Administrator |
| techlead | admin456 | Tech Lead |

## API Endpoints

### Authentication
- `POST /api/auth/login` - Authenticate user
- `GET /api/auth/verify` - Verify token (placeholder)

### Health
- `GET /api/health` - Server health check

## Environment Variables (.env)
```
DB_HOST=localhost
DB_USER=root
DB_PASSWORD=root
DB_NAME=ITAssetData
SERVER_HOST=127.0.0.1
SERVER_PORT=8000
DEBUG=True
FRONTEND_DIST_PATH=../dist
```

## File Structure
```
backend/
├── main.py          # FastAPI app & routes
├── DB_utils.py      # MySQL database utilities
├── requirements.txt # Python dependencies
├── .env             # Environment variables
└── README.md
```
