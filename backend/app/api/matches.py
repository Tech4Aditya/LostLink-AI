from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select, or_
from sqlalchemy.orm import Session, joinedload
from ..db import get_db
from ..models import Match, Claim, User, Report
from ..schemas import MatchOut, ClaimCreate, ClaimOut
from ..security import current_user

router = APIRouter(prefix="/matches", tags=["matches"])

@router.get("", response_model=list[MatchOut])
def list_matches(user: User = Depends(current_user), db: Session = Depends(get_db)):
    stmt = (
        select(Match)
        .join(Report, or_(Match.lost_report_id == Report.id, Match.found_report_id == Report.id))
        .where(Report.user_id == user.id)
        .order_by(Match.final_score.desc())
        .limit(100)
    )
    return db.scalars(stmt).unique().all()

@router.get("/{match_id}", response_model=MatchOut)
def get_match(match_id, user: User = Depends(current_user), db: Session = Depends(get_db)):
    match = db.get(Match, match_id)
    if not match:
        raise HTTPException(404, "Match not found")
    owned = db.scalar(select(Report).where(Report.id.in_([match.lost_report_id, match.found_report_id]), Report.user_id == user.id))
    if not owned:
        raise HTTPException(404, "Match not found")
    return match

@router.post("/{match_id}/claims", response_model=ClaimOut)
def create_claim(match_id, payload: ClaimCreate, user: User = Depends(current_user), db: Session = Depends(get_db)):
    match = db.get(Match, match_id)
    if not match:
        raise HTTPException(404, "Match not found")
    owned = db.scalar(select(Report).where(Report.id.in_([match.lost_report_id, match.found_report_id]), Report.user_id == user.id))
    if not owned:
        raise HTTPException(404, "Match not found")
    claim = Claim(match_id=match.id, claimant_user_id=user.id, private_detail=payload.private_detail)
    db.add(claim)
    db.commit()
    db.refresh(claim)
    return claim
