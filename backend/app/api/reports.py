from datetime import datetime
from pathlib import Path
from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile
from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload
from ..db import get_db
from ..models import Report, Image, User
from ..schemas import ReportOut
from ..security import current_user
from ..storage import save_upload
from ..ai.encoder import get_encoder
from ..services.matching import persist_matches

router = APIRouter(prefix="/reports", tags=["reports"])

def serialize(report: Report):
    image_url = None
    if report.images:
        image_url = "/uploads/" + Path(report.images[0].storage_path).name
    return ReportOut(
        id=report.id, type=report.type, category=report.category,
        description=report.description, color=report.color,
        location_name=report.location_name, latitude=report.latitude,
        longitude=report.longitude, event_time=report.event_time,
        status=report.status, image_url=image_url, created_at=report.created_at
    )

@router.post("", response_model=ReportOut)
async def create_report(
    type: str = Form(...),
    category: str = Form(...),
    description: str = Form(...),
    location_name: str = Form(...),
    color: str | None = Form(None),
    latitude: float | None = Form(None),
    longitude: float | None = Form(None),
    event_time: datetime | None = Form(None),
    image: UploadFile | None = File(None),
    user: User = Depends(current_user),
    db: Session = Depends(get_db),
):
    type = type.lower().strip()
    if type not in {"lost", "found"}:
        raise HTTPException(422, "type must be lost or found")
    report = Report(
        user_id=user.id, type=type, category=category.strip(),
        description=description.strip(), color=color.strip() if color else None,
        location_name=location_name.strip(), latitude=latitude, longitude=longitude,
        event_time=event_time,
    )
    db.add(report)
    db.flush()

    # AI is an enrichment layer, not a prerequisite for creating a report.
    try:
        encoder = get_encoder()
        text = f"{category}. {color or ''}. {description}. Location: {location_name}."
        report.text_embedding = encoder.text(text)
    except Exception:
        report.text_embedding = None

    if image:
        try:
            storage_path, mime = await save_upload(image)
        except ValueError as exc:
            db.rollback()
            raise HTTPException(422, str(exc))
        db_image = Image(report_id=report.id, storage_path=storage_path, mime_type=mime)
        db.add(db_image)
        db.flush()
        try:
            db_image.embedding = get_encoder().image(storage_path)
        except Exception:
            db_image.embedding = None

    db.commit()
    db.refresh(report)

    try:
        persist_matches(db, report)
    except Exception:
        # Matching failure must never roll back a valid user report.
        db.rollback()

    report = db.scalar(select(Report).options(joinedload(Report.images)).where(Report.id == report.id))
    return serialize(report)

@router.get("", response_model=list[ReportOut])
def list_reports(
    type: str | None = None,
    user: User = Depends(current_user),
    db: Session = Depends(get_db),
):
    stmt = select(Report).options(joinedload(Report.images)).where(Report.user_id == user.id).order_by(Report.created_at.desc()).limit(100)
    if type:
        stmt = stmt.where(Report.type == type)
    reports = db.scalars(stmt).unique().all()
    return [serialize(r) for r in reports]

@router.get("/{report_id}", response_model=ReportOut)
def get_report(report_id, user: User = Depends(current_user), db: Session = Depends(get_db)):
    report = db.scalar(select(Report).options(joinedload(Report.images)).where(Report.id == report_id))
    if not report or report.user_id != user.id:
        raise HTTPException(404, "Report not found")
    return serialize(report)
