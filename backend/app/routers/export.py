import io
import json
import csv
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from ..database import get_db, User, ProcessedData, Report, SalesData
from ..auth import get_current_user

router = APIRouter(prefix="/export", tags=["export"])

@router.get("/{dataset_id}/csv")
def export_csv(dataset_id: int, db: Session = Depends(get_db),
               current_user: User = Depends(get_current_user)):
    ds = db.query(SalesData).filter(SalesData.id == dataset_id).first()
    if not ds:
        raise HTTPException(status_code=404, detail="Dataset not found")
    rows = db.query(ProcessedData).filter(ProcessedData.dataset_id == dataset_id).all()
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["Order ID", "Order Date", "Customer", "Region", "Category",
                     "Sub-Category", "Product", "Sales", "Quantity", "Discount",
                     "Profit", "Profit %", "Month-Year"])
    for r in rows:
        writer.writerow([r.order_id, r.order_date, r.customer_name, r.region,
                         r.category, r.sub_category, r.product_name, r.sales,
                         r.quantity, r.discount, r.profit, r.profit_pct, r.month_year])
    output.seek(0)
    return StreamingResponse(io.BytesIO(output.getvalue().encode()),
                             media_type="text/csv",
                             headers={"Content-Disposition": f"attachment; filename=sales_data_{dataset_id}.csv"})

@router.get("/{dataset_id}/pdf")
def export_pdf(dataset_id: int, db: Session = Depends(get_db),
               current_user: User = Depends(get_current_user)):
    from reportlab.lib.pagesizes import letter
    from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
    from reportlab.lib.styles import getSampleStyleSheet
    from reportlab.lib import colors
    from ..analytics import compute_kpis, category_performance, top_products, generate_insights

    ds = db.query(SalesData).filter(SalesData.id == dataset_id).first()
    if not ds or ds.status != "ready":
        raise HTTPException(status_code=404, detail="Dataset not ready")

    buf = io.BytesIO()
    doc = SimpleDocTemplate(buf, pagesize=letter)
    styles = getSampleStyleSheet()
    elements = []

    elements.append(Paragraph(f"Sales Intelligence Report — {ds.filename}", styles["Title"]))
    elements.append(Spacer(1, 12))

    kpis = compute_kpis(db, dataset_id)
    kpi_data = [["Metric", "Value"],
                ["Total Sales", f"${kpis.get('total_sales', 0):,.2f}"],
                ["Total Profit", f"${kpis.get('total_profit', 0):,.2f}"],
                ["Profit Margin", f"{kpis.get('profit_margin', 0):.2f}%"],
                ["Total Orders", str(kpis.get('total_orders', 0))],
                ["Avg Discount", f"{kpis.get('avg_discount', 0):.2f}%"]]
    t = Table(kpi_data, colWidths=[200, 200])
    t.setStyle(TableStyle([("BACKGROUND", (0, 0), (-1, 0), colors.darkblue),
                            ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                            ("GRID", (0, 0), (-1, -1), 0.5, colors.grey)]))
    elements.append(t)
    elements.append(Spacer(1, 20))

    elements.append(Paragraph("Top 5 Products by Sales", styles["Heading2"]))
    products = top_products(db, dataset_id)
    prod_data = [["Product", "Sales"]] + [[p["product"][:50], f"${p['sales']:,.2f}"] for p in products]
    t2 = Table(prod_data, colWidths=[350, 100])
    t2.setStyle(TableStyle([("BACKGROUND", (0, 0), (-1, 0), colors.steelblue),
                             ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                             ("GRID", (0, 0), (-1, -1), 0.5, colors.lightgrey)]))
    elements.append(t2)
    elements.append(Spacer(1, 20))

    elements.append(Paragraph("Auto-Generated Insights", styles["Heading2"]))
    for insight in generate_insights(db, dataset_id):
        elements.append(Paragraph(f"• {insight}", styles["Normal"]))
        elements.append(Spacer(1, 6))

    doc.build(elements)
    buf.seek(0)
    return StreamingResponse(buf, media_type="application/pdf",
                             headers={"Content-Disposition": f"attachment; filename=report_{dataset_id}.pdf"})

@router.post("/reports/save")
def save_report(payload: dict, db: Session = Depends(get_db),
                current_user: User = Depends(get_current_user)):
    report = Report(name=payload.get("name", "Untitled"),
                    content=json.dumps(payload.get("content", {})),
                    user_id=current_user.id)
    db.add(report)
    db.commit()
    db.refresh(report)
    return {"id": report.id, "name": report.name}

@router.get("/reports")
def list_reports(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    reports = db.query(Report).filter(Report.user_id == current_user.id)\
                .order_by(Report.created_at.desc()).all()
    return [{"id": r.id, "name": r.name, "created_at": str(r.created_at)} for r in reports]
