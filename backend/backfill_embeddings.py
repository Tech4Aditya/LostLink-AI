from app.db import SessionLocal
from app.models import Report
from app.ai.encoder import get_encoder

db = SessionLocal()
encoder = get_encoder()

try:
    reports = db.query(Report).all()
    print("REPORTS:", len(reports))

    count = 0

    for report in reports:
        text = (
            f"{report.category}. "
            f"{report.color or ''}. "
            f"{report.description}. "
            f"Location: {report.location_name}."
        )

        embedding = encoder.text(text)

        if embedding is not None:
            report.text_embedding = embedding
            count += 1

    db.commit()
    print("BACKFILLED:", count)

finally:
    db.close()
