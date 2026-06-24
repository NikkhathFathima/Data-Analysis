import io
import sys
import os
import pandas as pd
from fastapi import APIRouter, Depends, UploadFile, File, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from ..database import get_db, SalesData, User, ProcessedData, DATABASE_URL
from ..auth import get_current_user
from ..processor import validate_schema, clean_and_process, save_to_db

router = APIRouter(prefix="/upload", tags=["upload"])

def process_file_bg(content: bytes, filename: str, dataset_id: int):
    """Runs in background thread (not subprocess) — safe to use absolute imports."""
    from sqlalchemy import create_engine
    from sqlalchemy.orm import sessionmaker
    import pandas as pd
    import io

    engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
    BgSession = sessionmaker(bind=engine)
    db = BgSession()
    try:
        if filename.lower().endswith(".csv"):
            df = pd.read_csv(io.BytesIO(content))
        else:
            df = pd.read_excel(io.BytesIO(content))
        df = clean_and_process(df)
        save_to_db(df, dataset_id, db)
        ds = db.query(SalesData).filter(SalesData.id == dataset_id).first()
        if ds:
            ds.row_count = len(df)
            ds.status = "ready"
            db.commit()
    except Exception as e:
        db.rollback()
        ds = db.query(SalesData).filter(SalesData.id == dataset_id).first()
        if ds:
            ds.status = "error"
            db.commit()
    finally:
        db.close()

@router.post("/")
async def upload_file(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if not file.filename.endswith((".csv", ".xlsx", ".xls")):
        raise HTTPException(status_code=400, detail="Only CSV/Excel files allowed")
    content = await file.read()
    # Quick schema check
    try:
        df_peek = pd.read_csv(io.BytesIO(content)) if file.filename.endswith(".csv") \
            else pd.read_excel(io.BytesIO(content))
        missing = validate_schema(df_peek)
        if missing:
            raise HTTPException(status_code=422,
                detail=f"Missing columns: {', '.join(missing)}")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Cannot parse file: {str(e)}")

    dataset = SalesData(filename=file.filename, user_id=current_user.id, status="processing")
    db.add(dataset)
    db.commit()
    db.refresh(dataset)

    from ..database import DATABASE_URL
    background_tasks.add_task(process_file_bg, content, file.filename, dataset.id)
    return {"dataset_id": dataset.id, "status": "processing", "filename": file.filename}

@router.get("/datasets")
def list_datasets(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    if current_user.role == "admin":
        datasets = db.query(SalesData).order_by(SalesData.uploaded_at.desc()).all()
    else:
        datasets = db.query(SalesData).filter(SalesData.user_id == current_user.id)\
                     .order_by(SalesData.uploaded_at.desc()).all()
    return [{"id": d.id, "filename": d.filename, "status": d.status,
             "row_count": d.row_count, "uploaded_at": str(d.uploaded_at)} for d in datasets]

@router.get("/datasets/{dataset_id}/status")
def dataset_status(dataset_id: int, db: Session = Depends(get_db),
                   current_user: User = Depends(get_current_user)):
    ds = db.query(SalesData).filter(SalesData.id == dataset_id).first()
    if not ds:
        raise HTTPException(status_code=404, detail="Dataset not found")
    return {"status": ds.status, "row_count": ds.row_count}
