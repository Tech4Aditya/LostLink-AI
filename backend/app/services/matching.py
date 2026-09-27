from __future__ import annotations
from datetime import datetime, timezone
from math import radians, sin, cos, asin, sqrt, exp
from uuid import UUID
from sqlalchemy import select, or_
from sqlalchemy.orm import Session, joinedload
from . import __init__  # keeps package import explicit
from ..models import Report, Image, Match
from ..config import get_settings
from ..ai.encoder import get_encoder, normalize_text

def cosine(a, b):
    if a is None or b is None:
        return 0.0

    if len(a) == 0 or len(b) == 0:
        return 0.0

    num = sum(x * y for x, y in zip(a, b))
    den = (sum(x * x for x in a) ** 0.5) * (sum(y * y for y in b) ** 0.5)

    return max(0.0, min(1.0, num / den)) if den else 0.0


def token_similarity(a, b):
    aa = set(normalize_text(a).split())
    bb = set(normalize_text(b).split())
    if not aa or not bb:
        return 0.0
    return len(aa & bb) / len(aa | bb)

def metadata_score(lost: Report, found: Report):
    attr = 0.0
    if lost.category and found.category:
        attr += 0.65 if normalize_text(lost.category) == normalize_text(found.category) else 0.0
    if lost.color and found.color:
        attr += 0.35 if normalize_text(lost.color) == normalize_text(found.color) else 0.0

    loc = 0.0
    if lost.latitude is not None and found.latitude is not None:
        r = 6371.0
        dlat = radians(found.latitude - lost.latitude)
        dlon = radians(found.longitude - lost.longitude)
        a = sin(dlat/2)**2 + cos(radians(lost.latitude))*cos(radians(found.latitude))*sin(dlon/2)**2
        distance_km = 2*r*asin(sqrt(a))
        loc = exp(-distance_km / 1.5)
    elif lost.location_name and found.location_name:
        loc = 1.0 if normalize_text(lost.location_name) == normalize_text(found.location_name) else token_similarity(lost.location_name, found.location_name)

    tim = 0.0
    if lost.event_time and found.event_time:
        delta_hours = abs((found.event_time - lost.event_time).total_seconds()) / 3600
        tim = exp(-delta_hours / 12)

    return attr, max(0.0, min(1.0, loc)), max(0.0, min(1.0, tim))

def final_score(visual, text, attr, loc, tim):
    # Initial baseline weights. Tune from held-out real data later.
    return 0.45*visual + 0.25*text + 0.12*attr + 0.10*loc + 0.08*tim

def rank_pair(lost, found):
    encoder = get_encoder()
    visual = 0.0
    if lost.images and found.images:
        # Image embeddings are stored in DB; use values if loaded.
        vectors = [i.embedding for i in lost.images if i.embedding is not None]
        fvectors = [i.embedding for i in found.images if i.embedding is not None]
        if vectors and fvectors:
            visual = max(cosine(a, b) for a in vectors for b in fvectors)
    text = cosine(lost.text_embedding, found.text_embedding)
    if text == 0.0:
        text = token_similarity(lost.description, found.description)
    attr, loc, tim = metadata_score(lost, found)
    score = final_score(visual, text, attr, loc, tim)
    reasons = []
    if visual >= 0.80: reasons.append("Strong visual similarity")
    if text >= 0.60: reasons.append("Descriptions are semantically similar")
    if attr >= 0.75: reasons.append("Category/color attributes align")
    if loc >= 0.65: reasons.append("Locations are geographically/contextually compatible")
    if tim >= 0.65: reasons.append("Report times are reasonably close")
    if not reasons: reasons.append("Weak/partial evidence; manual verification recommended")
    return {
        "visual_score": round(visual, 4),
        "text_score": round(text, 4),
        "attribute_score": round(attr, 4),
        "location_score": round(loc, 4),
        "time_score": round(tim, 4),
        "final_score": round(score, 4),
        "explanation": {
            "reasons": reasons,
            "weights": {"visual": .45, "text": .25, "attributes": .12, "location": .10, "time": .08},
            "note": "Scores are candidate-match evidence, not proof of ownership."
        }
    }

def create_candidates(db: Session, report: Report, limit=50):
    opposite = "found" if report.type == "lost" else "lost"
    stmt = (
        select(Report)
        .options(joinedload(Report.images))
        .where(Report.type == opposite, Report.status == "active")
        .where(Report.id != report.id)
        .order_by(Report.created_at.desc())
        .limit(300)
    )
    candidates = db.scalars(stmt).unique().all()
    ranked = [(candidate, rank_pair(report, candidate)) for candidate in candidates]
    ranked.sort(key=lambda x: x[1]["final_score"], reverse=True)
    return ranked[:limit]

def persist_matches(db: Session, report: Report, limit=50):
    settings = get_settings()
    ranked = create_candidates(db, report, limit)
    for candidate, s in ranked:
        lost_id = report.id if report.type == "lost" else candidate.id
        found_id = candidate.id if report.type == "lost" else report.id
        existing = db.scalar(select(Match).where(Match.lost_report_id == lost_id, Match.found_report_id == found_id))
        if existing:
            existing.visual_score = s["visual_score"]
            existing.text_score = s["text_score"]
            existing.attribute_score = s["attribute_score"]
            existing.location_score = s["location_score"]
            existing.time_score = s["time_score"]
            existing.final_score = s["final_score"]
            existing.explanation = s["explanation"]
        elif s["final_score"] >= settings.match_min_score:
            db.add(Match(
                lost_report_id=lost_id,
                found_report_id=found_id,
                visual_score=s["visual_score"],
                text_score=s["text_score"],
                attribute_score=s["attribute_score"],
                location_score=s["location_score"],
                time_score=s["time_score"],
                final_score=s["final_score"],
                status="candidate",
                explanation=s["explanation"],
            ))
    db.commit()
