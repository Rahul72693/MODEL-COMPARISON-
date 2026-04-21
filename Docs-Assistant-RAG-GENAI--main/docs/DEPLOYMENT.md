# Deployment Guide

## Local Deployment (Development)

### 1. Prerequisites
- Python 3.9+
- Node.js 18+
- Tesseract OCR (installed on system)

### 2. Environment Setup
- Clone the repository.
- Create and activate a virtual environment.
- Install backend dependencies: `pip install -r requirements.txt`.
- Install frontend dependencies: `cd frontend-react && npm install`.

### 3. Configuration
- Create a `.env` file in the root directory based on `.env.example`.
- Add your `GEMINI_API_KEY` and `GROQ_API_KEY`.

### 4. Running the Servers
- **Backend**: `uvicorn backend.main:app --reload --port 8000`
- **Frontend**: `cd frontend-react && npm run dev`

---

## Docker Deployment (Production-ready)

### 1. Build and Run with Compose
Ensure Docker and Docker Compose are installed. Run from the root directory:

```bash
docker-compose up --build
```

### 2. Accessing the Application
- **Frontend**: `http://localhost:3000` (or as configured in Docker)
- **Backend API**: `http://localhost:8000`

### 3. Data Persistence
The `metrics.db` SQLite database is persisted via Docker volumes as defined in `docker-compose.yml`.
