# FarmSathi — Digital Agricultural Platform

FarmSathi is a production-oriented, farmer-centric agricultural assistance platform providing crop recommendations, plant disease detection, verified agro-weather forecasts, and natural-language farm advisory.

## Monorepo Architecture

```
farm_sathii/
├── backend/            # FastAPI ASGI backend, SQLAlchemy 2.0 asyncpg, ML inference services
│   ├── app/            # Application core, API routes, models, schemas, services
│   ├── tests/          # Pytest suite
│   ├── requirements.txt# Backend Python dependencies
│   └── venv/           # Python 3.13 virtual environment
├── frontend/           # React 18, TypeScript, Vite, Google Stitch Design System
│   ├── src/            # Components, features, styles, state management
│   └── package.json    # Frontend Node dependencies
├── ml/                 # Machine learning models and datasets
│   ├── datasets/       # Approved training and evaluation datasets
│   └── models/         # Serialized production model artifacts
├── storage/            # Local media storage abstraction
│   └── uploads/        # Uploaded leaf diagnostic images and media
├── .env.example        # Environment configuration template
└── README.md
```

## Quick Start (Development)

### 1. Backend Setup
```bash
# Activate virtual environment
.\backend\venv\Scripts\Activate.ps1

# Run tests
pytest .\backend\tests

# Start development server
uvicorn app.main:app --app-dir backend --reload --port 8000
```
Backend API will be accessible at: `http://localhost:8000/api/v1`
Swagger Docs: `http://localhost:8000/docs`

### 2. Frontend Setup
```bash
# Install dependencies
npm --prefix frontend install

# Start Vite dev server
npm --prefix frontend run dev

# Build for production
npm --prefix frontend run build
```
Frontend will be accessible at: `http://localhost:5173`
