# 📊 Sales Intelligence Platform

A full-stack data analytics web app that lets you upload sales data, process it automatically, and explore interactive dashboards with KPIs, charts, insights, forecasts, and anomaly detection.

---

## 🖥️ Tech Stack

| Layer | Technology |
|---|---|
| Frontend | React 18 + Vite + Recharts |
| Backend | Python + FastAPI |
| Database | SQLite (via SQLAlchemy) |
| Data Processing | Pandas + NumPy |
| Machine Learning | Scikit-learn (forecast + anomaly) |
| Auth | JWT (JSON Web Tokens) |
| Reports | ReportLab (PDF export) |

---

## ✨ Features

- ✅ Upload CSV or Excel sales files
- ✅ Auto data cleaning and processing
- ✅ KPI cards — Total Sales, Profit, Margin, Orders, Discount
- ✅ Sales trend charts (monthly area chart)
- ✅ Region-wise sales breakdown
- ✅ Category performance (pie + bar charts)
- ✅ Top 5 products ranking
- ✅ Auto-generated business insights
- ✅ Anomaly detection (statistical threshold)
- ✅ 3-month sales forecast (Linear Regression)
- ✅ Filters — Region, Category, Date Range
- ✅ Export data as CSV
- ✅ Export PDF report
- ✅ Login / Register with JWT auth
- ✅ Role-based access — Admin and User

---

## 📁 Project Structure

```
sales-platform/
│
├── backend/                  ← Python FastAPI server
│   ├── app/
│   │   ├── main.py           ← App entry point
│   │   ├── database.py       ← DB models (User, SalesData, etc.)
│   │   ├── auth.py           ← JWT login/register logic
│   │   ├── processor.py      ← Data cleaning & processing
│   │   ├── analytics.py      ← KPIs, trends, insights, forecast
│   │   └── routers/
│   │       ├── auth.py       ← /auth endpoints
│   │       ├── upload.py     ← /upload endpoints
│   │       ├── analytics.py  ← /analytics endpoints
│   │       └── export.py     ← /export endpoints
│   └── requirements.txt
│
├── frontend/                 ← React + Vite app
│   └── src/
│       ├── pages/
│       │   ├── Login.jsx
│       │   ├── Register.jsx
│       │   ├── Dashboard.jsx ← Main analytics dashboard
│       │   ├── Upload.jsx    ← File upload page
│       │   └── Reports.jsx   ← Export reports page
│       ├── components/
│       │   ├── Layout.jsx    ← Sidebar navigation
│       │   └── KpiCard.jsx   ← Reusable KPI card
│       └── api/
│           └── auth.jsx      ← Axios + Auth context
│
├── Superstore_Sales_Data.xlsx ← Sample dataset (ready to upload)
├── setup.bat                  ← One-click setup (Windows)
├── start.bat                  ← One-click start (Windows)
└── README.md
```

---

## 🚀 Getting Started

### Prerequisites

- Python 3.10 or higher → https://www.python.org/downloads/
- Node.js 18 or higher → https://nodejs.org/

---

### Step 1 — Clone the Repository

```bash
git clone https://github.com/NikkhathFathima/Data-Analysis.git
cd Data-Analysis
```

---

### Step 2 — Setup & Run the Backend

```bash
cd backend

# Create virtual environment
python -m venv venv

# Activate it (Windows)
venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Start the backend server
uvicorn app.main:app --host 127.0.0.1 --port 8000
```

Backend will be running at → **http://localhost:8000**
API documentation → **http://localhost:8000/docs**

---

### Step 3 — Setup & Run the Frontend

Open a **new terminal window**, then:

```bash
cd frontend

# Install dependencies
npm install

# Start the frontend
npm run dev
```

Frontend will be running at → **http://localhost:5173**

---

### Step 4 — Open the App

1. Go to **http://localhost:5173**
2. Click **Create Account** and register
3. Go to **Upload Data** in the sidebar
4. Upload the included `Superstore_Sales_Data.xlsx` file
5. Wait a few seconds for processing
6. Click **Analyze** to open the dashboard

---

## 📊 Sample Dataset

The file `Superstore_Sales_Data.xlsx` is included in the repo.

| Column | Description |
|---|---|
| Order ID | Unique order identifier |
| Order Date | Date the order was placed |
| Ship Date | Date the order was shipped |
| Customer Name | Name of the customer |
| Segment | Consumer / Corporate / Home Office |
| Region | West / East / Central / South |
| Category | Technology / Furniture / Office Supplies |
| Sub-Category | Phones, Chairs, Binders, etc. |
| Product Name | Name of the product |
| Sales | Total sale amount ($) |
| Quantity | Number of units sold |
| Discount | Discount applied (0.0 to 0.5) |
| Profit | Net profit ($) |

- **2,000 rows** of realistic US retail sales data
- **Date range:** 2021 – 2022
- **4 Regions**, **3 Categories**, **12 Sub-Categories**

---

## 🔌 API Endpoints

### Auth
| Method | Endpoint | Description |
|---|---|---|
| POST | `/auth/register` | Create new account |
| POST | `/auth/login` | Login and get token |
| GET | `/auth/me` | Get current user info |

### Upload
| Method | Endpoint | Description |
|---|---|---|
| POST | `/upload/` | Upload CSV or Excel file |
| GET | `/upload/datasets` | List all uploaded datasets |
| GET | `/upload/datasets/{id}/status` | Check processing status |

### Analytics
All analytics endpoints support optional filters: `?region=West&category=Technology&date_from=2021-01-01&date_to=2021-12-31`

| Method | Endpoint | Description |
|---|---|---|
| GET | `/analytics/{id}/kpis` | Total Sales, Profit, Margin |
| GET | `/analytics/{id}/trend` | Monthly sales trend |
| GET | `/analytics/{id}/regions` | Sales by region |
| GET | `/analytics/{id}/categories` | Category performance |
| GET | `/analytics/{id}/top-products` | Top 5 products |
| GET | `/analytics/{id}/insights` | Auto-generated insights |
| GET | `/analytics/{id}/anomalies` | Sales anomalies |
| GET | `/analytics/{id}/forecast` | 3-month forecast |
| GET | `/analytics/{id}/filters` | Available filter options |

### Export
| Method | Endpoint | Description |
|---|---|---|
| GET | `/export/{id}/csv` | Download data as CSV |
| GET | `/export/{id}/pdf` | Download PDF report |
| POST | `/export/reports/save` | Save a report |
| GET | `/export/reports` | List saved reports |

---

## 🔐 Authentication

- Register → get a JWT token
- Token is stored in `localStorage`
- All API requests include `Authorization: Bearer <token>`
- First registered user automatically gets **Admin** role
- All other users get **User** role

---

## 📸 Dashboard Pages

| Page | What you see |
|---|---|
| **Dashboard → Overview** | KPI cards + Region bar chart + Category pie chart |
| **Dashboard → Trends** | Monthly area chart + Radar chart + Margin bar chart |
| **Dashboard → Products** | Top 5 products horizontal bar + ranking table |
| **Dashboard → Insights** | Auto-generated text insights + summary cards |
| **Dashboard → Advanced** | 3-month forecast line chart + anomaly detection table |
| **Upload Data** | Drag & drop file upload + dataset list |
| **Reports** | Download CSV / PDF for any dataset |

---

## ⚙️ Environment

No `.env` file needed for local development. Default settings:

- Backend: `http://127.0.0.1:8000`
- Frontend: `http://localhost:5173`
- Database: `backend/sales_platform.db` (auto-created on first run)

---

## 🌐 Deployment

### Backend → Render
1. Connect your GitHub repo to [render.com](https://render.com)
2. Set **Build Command:** `pip install -r requirements.txt`
3. Set **Start Command:** `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
4. Set **Root Directory:** `backend`

### Frontend → Netlify
1. Connect your GitHub repo to [netlify.com](https://netlify.com)
2. Set **Build Command:** `npm run build`
3. Set **Publish Directory:** `dist`
4. Set **Root Directory:** `frontend`
5. Add environment variable: `VITE_API_URL=https://your-backend.onrender.com`

---

## 🛠️ Troubleshooting

**Backend won't start**
- Make sure virtual environment is activated: `venv\Scripts\activate`
- Make sure you are inside the `backend` folder

**Upload fails with Invalid Token**
- Log out and log back in to get a fresh token
- Make sure backend is running on port 8000

**Frontend shows blank page**
- Make sure `npm install` was run inside the `frontend` folder
- Make sure both backend and frontend servers are running

**Processing stuck**
- Refresh the Upload page after 10 seconds
- Make sure your file has the required columns listed above

---

## 👩‍💻 Author

**Nikkhath Fathima**
GitHub → https://github.com/NikkhathFathima
