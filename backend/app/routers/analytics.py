from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.orm import Session
from typing import Optional
from datetime import date
from ..database import get_db, User, SalesData
from ..auth import get_current_user
from ..analytics import (compute_kpis, sales_trend, region_sales, category_performance,
                          top_products, worst_categories, generate_insights,
                          detect_anomalies, forecast_sales)

router = APIRouter(prefix="/analytics", tags=["analytics"])

def _check_dataset(dataset_id: int, db: Session, user: User):
    ds = db.query(SalesData).filter(SalesData.id == dataset_id).first()
    if not ds:
        raise HTTPException(status_code=404, detail="Dataset not found")
    if ds.status != "ready":
        raise HTTPException(status_code=400, detail=f"Dataset is {ds.status}")
    if user.role != "admin" and ds.user_id != user.id:
        raise HTTPException(status_code=403, detail="Access denied")
    return ds

def _filters(region, category, date_from, date_to):
    return dict(region=region, category=category, date_from=date_from, date_to=date_to)

@router.get("/{dataset_id}/kpis")
def get_kpis(dataset_id: int,
             region: Optional[str] = None, category: Optional[str] = None,
             date_from: Optional[date] = None, date_to: Optional[date] = None,
             db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    _check_dataset(dataset_id, db, current_user)
    return compute_kpis(db, dataset_id, **_filters(region, category, date_from, date_to))

@router.get("/{dataset_id}/trend")
def get_trend(dataset_id: int,
              region: Optional[str] = None, category: Optional[str] = None,
              date_from: Optional[date] = None, date_to: Optional[date] = None,
              db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    _check_dataset(dataset_id, db, current_user)
    return sales_trend(db, dataset_id, **_filters(region, category, date_from, date_to))

@router.get("/{dataset_id}/regions")
def get_regions(dataset_id: int,
                date_from: Optional[date] = None, date_to: Optional[date] = None,
                db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    _check_dataset(dataset_id, db, current_user)
    return region_sales(db, dataset_id, date_from=date_from, date_to=date_to)

@router.get("/{dataset_id}/categories")
def get_categories(dataset_id: int,
                   region: Optional[str] = None,
                   date_from: Optional[date] = None, date_to: Optional[date] = None,
                   db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    _check_dataset(dataset_id, db, current_user)
    return category_performance(db, dataset_id, **_filters(region, None, date_from, date_to))

@router.get("/{dataset_id}/top-products")
def get_top_products(dataset_id: int,
                     region: Optional[str] = None, category: Optional[str] = None,
                     date_from: Optional[date] = None, date_to: Optional[date] = None,
                     db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    _check_dataset(dataset_id, db, current_user)
    return top_products(db, dataset_id, **_filters(region, category, date_from, date_to))

@router.get("/{dataset_id}/worst-categories")
def get_worst(dataset_id: int, db: Session = Depends(get_db),
              current_user: User = Depends(get_current_user)):
    _check_dataset(dataset_id, db, current_user)
    return worst_categories(db, dataset_id)

@router.get("/{dataset_id}/insights")
def get_insights(dataset_id: int,
                 region: Optional[str] = None, category: Optional[str] = None,
                 date_from: Optional[date] = None, date_to: Optional[date] = None,
                 db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    _check_dataset(dataset_id, db, current_user)
    return generate_insights(db, dataset_id, **_filters(region, category, date_from, date_to))

@router.get("/{dataset_id}/anomalies")
def get_anomalies(dataset_id: int, db: Session = Depends(get_db),
                  current_user: User = Depends(get_current_user)):
    _check_dataset(dataset_id, db, current_user)
    return detect_anomalies(db, dataset_id)

@router.get("/{dataset_id}/forecast")
def get_forecast(dataset_id: int, db: Session = Depends(get_db),
                 current_user: User = Depends(get_current_user)):
    _check_dataset(dataset_id, db, current_user)
    return forecast_sales(db, dataset_id)

@router.get("/{dataset_id}/filters")
def get_filter_options(dataset_id: int, db: Session = Depends(get_db),
                       current_user: User = Depends(get_current_user)):
    from ..database import ProcessedData
    _check_dataset(dataset_id, db, current_user)
    rows = db.query(ProcessedData.region, ProcessedData.category)\
             .filter(ProcessedData.dataset_id == dataset_id).distinct().all()
    regions = sorted(set(r.region for r in rows if r.region))
    categories = sorted(set(r.category for r in rows if r.category))
    return {"regions": regions, "categories": categories}
