# Sales Intelligence Platform

A production-ready full-stack sales analytics system built for analyzing retail sales data.

## Tech Stack

- **Frontend**: React 18 + Vite + Recharts + React Router
- **Backend**: FastAPI + SQLAlchemy
- **Database**: SQLite (easily swappable to PostgreSQL)
- **Data Processing**: Pandas + NumPy
- **ML**: Scikit-learn (Linear Regression forecast + anomaly detection)
- **Reports**: ReportLab (PDF generation)

## Features

| Feature | Status |
|---|---|
| CSV/Excel upload with schema validation | ✅ |
| Background data processing | ✅ |
| KPI Engine (Sales, Profit, Margin, Orders) | ✅ |
| Sales trends (monthly area chart) | ✅ |
| Region-wise sales (bar + radar chart) | ✅ |
| Category performance (pie + bar charts) | ✅ |
| Top 5 products ranking | ✅ |
| Filters: Region, Category, Date Range | ✅ |
| Auto-generated insights (rule-based) | ✅ |
| Anomaly detection (2.5σ threshold) | ✅ |
| Sales forecast (Linear Regression, 3 months) | ✅ |
| JWT Authentication (Login/Register) | ✅ |
| Role-based access (Admin/User) | ✅ |
| Export CSV | ✅ |
| Export PDF report | ✅ |

## Setup

### Prerequisites
- Python 3.10+
- Node.js 18+

### Quick Start (Windows)

```bash
# Run setup script (creates venv, installs deps, generates sample data)
cd sales-platform
setup.bat

# Start everything
start.bat
```

### Manual Setup

**Backend:**
```bash
cd backend
python -m venv venv
venv\Scripts\activate        # Windows
source venv/bin/activate     # Mac/Linux
pip install -r requirements.txt
python generate_sample.py    # Creates sample_superstore.csv
uvicorn app.main:app --reload --port 8000
```

**Frontend:**
```bash
cd frontend
npm install
npm run dev
```

### Access
- **Frontend**: http://localhost:5173
- **API**: http://localhost:8000
- **Swagger Docs**: http://localhost:8000/docs

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/auth/register` | Register new user |
| POST | `/auth/login` | Login + get JWT |
| GET | `/auth/me` | Current user info |
| POST | `/upload/` | Upload CSV/Excel |
| GET | `/upload/datasets` | List user datasets |
| GET | `/analytics/{id}/kpis` | KPI metrics |
| GET | `/analytics/{id}/trend` | Monthly trend |
| GET | `/analytics/{id}/regions` | Region breakdown |
| GET | `/analytics/{id}/categories` | Category performance |
| GET | `/analytics/{id}/top-products` | Top 5 products |
| GET | `/analytics/{id}/insights` | Auto insights |
| GET | `/analytics/{id}/anomalies` | Sales anomalies |
| GET | `/analytics/{id}/forecast` | 3-month forecast |
| GET | `/analytics/{id}/filters` | Filter options |
| GET | `/export/{id}/csv` | Download CSV |
| GET | `/export/{id}/pdf` | Download PDF report |

All analytics endpoints support query params: `region`, `category`, `date_from`, `date_to`

## Database Schema

```
users           → id, email, name, hashed_password, role
sales_data      → id, filename, status, row_count, user_id
processed_data  → id, dataset_id, order_id, order_date, region, category,
                   product_name, sales, profit, profit_pct, month_year, ...
reports         → id, name, content, user_id
```

## Sample Dataset

Run `python generate_sample.py` to create `sample_superstore.csv` with 2,000 realistic sales records across:
- 4 Regions: West, East, Central, South
- 3 Categories: Technology, Furniture, Office Supplies
- 2020–2024 date range

## Deployment

### Render (Backend)
1. Connect GitHub repo
2. Build: `pip install -r requirements.txt`
3. Start: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`

### Netlify (Frontend)
1. Build: `npm run build`
2. Publish: `dist/`
3. Set env: `VITE_API_URL=https://your-backend.onrender.com`
