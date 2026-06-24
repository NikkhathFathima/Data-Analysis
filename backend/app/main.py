from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .database import init_db
from .routers import auth, upload, analytics, export

app = FastAPI(title="Sales Intelligence Platform", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
def startup():
    init_db()

app.include_router(auth.router)
app.include_router(upload.router)
app.include_router(analytics.router)
app.include_router(export.router)

@app.get("/")
def root():
    return {"message": "Sales Intelligence Platform API", "docs": "/docs"}
