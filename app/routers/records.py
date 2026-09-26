from fastapi import APIRouter, Depends, Form, Query, Request, status
from fastapi.responses import RedirectResponse, StreamingResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
import csv
import io
from datetime import datetime

from app.crud import create_work_record, delete_work_record, get_user_work_records, build_dashboard_summary
from app.deps import get_current_user, get_db
from app.models import User
from app.schemas import WorkRecordCreate

router = APIRouter()
templates = Jinja2Templates(directory="templates")


@router.get("/dashboard")
async def dashboard(
    request: Request,
    customer_name: str | None = None,
    start_date: str | None = None,
    end_date: str | None = None,
    status: str | None = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    start_dt = datetime.strptime(start_date, "%Y-%m-%d") if start_date else None
    end_dt = datetime.strptime(end_date, "%Y-%m-%d") if end_date else None
    summary = build_dashboard_summary(
        db,
        current_user.id,
        customer_name=customer_name,
        start_date=start_dt,
        end_date=end_dt,
        status=status,
    )

    return templates.TemplateResponse(
        "dashboard.html",
        {
            "request": request,
            "current_user": current_user,
            "records": summary["records"],
            "customer_name": customer_name or "",
            "start_date": start_date or "",
            "end_date": end_date or "",
            "status": status or "",
            "total_records": summary["total_records"],
            "total_minutes": summary["total_minutes"],
            "completed_records": summary["completed_records"],
            "customer_hours": summary["by_customer"],
        },
    )


@router.get("/records/new")
async def new_record_page(request: Request, current_user: User = Depends(get_current_user)):
    return templates.TemplateResponse("records_form.html", {"request": request, "current_user": current_user})


@router.post("/records/new")
async def create_record(
    request: Request,
    record_date: str = Form(...),
    customer_name: str = Form(...),
    work_content: str = Form(...),
    work_type: str = Form(...),
    status: str = Form(...),
    duration_minutes: int = Form(...),
    note: str = Form(""),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    try:
        parsed_date = datetime.strptime(record_date, "%Y-%m-%dT%H:%M")
    except ValueError:
        return templates.TemplateResponse(
            "records_form.html",
            {"request": request, "current_user": current_user, "error": "日時の形式が正しくありません。"},
            status_code=status.HTTP_400_BAD_REQUEST,
        )

    payload = WorkRecordCreate(
        record_date=parsed_date,
        customer_name=customer_name,
        work_content=work_content,
        work_type=work_type,
        status=status,
        duration_minutes=duration_minutes,
        note=note,
    )
    create_work_record(db, current_user.id, payload)
    return RedirectResponse(url="/dashboard", status_code=303)


@router.post("/records/{record_id}/delete")
async def delete_record(
    record_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    delete_work_record(db, record_id, current_user.id)
    return RedirectResponse(url="/dashboard", status_code=303)


@router.get("/reports")
async def reports_page(
    request: Request,
    start_date: str | None = None,
    end_date: str | None = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    start_dt = datetime.strptime(start_date, "%Y-%m-%d") if start_date else None
    end_dt = datetime.strptime(end_date, "%Y-%m-%d") if end_date else None
    records = get_user_work_records(db, current_user.id, start_date=start_dt, end_date=end_dt)

    by_customer = {}
    total_minutes = 0
    for record in records:
        total_minutes += record.duration_minutes
        by_customer[record.customer_name] = by_customer.get(record.customer_name, 0) + record.duration_minutes

    return templates.TemplateResponse(
        "reports.html",
        {
            "request": request,
            "current_user": current_user,
            "records": records,
            "total_minutes": total_minutes,
            "by_customer": dict(sorted(by_customer.items(), key=lambda item: item[1], reverse=True)),
            "start_date": start_date or "",
            "end_date": end_date or "",
        },
    )


@router.get("/reports/export.csv")
async def export_csv(
    start_date: str | None = Query(default=None),
    end_date: str | None = Query(default=None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    start_dt = datetime.strptime(start_date, "%Y-%m-%d") if start_date else None
    end_dt = datetime.strptime(end_date, "%Y-%m-%d") if end_date else None
    records = get_user_work_records(db, current_user.id, start_date=start_dt, end_date=end_dt)

    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["日付", "顧客名", "作業内容", "種別", "ステータス", "勤務時間(分)", "備考"])

    for record in records:
        writer.writerow([
            record.record_date.strftime("%Y-%m-%d %H:%M"),
            record.customer_name,
            record.work_content,
            record.work_type,
            record.status,
            record.duration_minutes,
            record.note,
        ])

    csv_bytes = output.getvalue().encode("utf-8")
    return StreamingResponse(
        io.BytesIO(csv_bytes),
        media_type="text/csv; charset=utf-8",
        headers={"Content-Disposition": "attachment; filename=work_report.csv"},
    )
