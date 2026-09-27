from datetime import datetime, timezone, timedelta
from sqlalchemy import select
from .db import SessionLocal, engine, Base
from .models import User, Report
from .security import hash_password
from .services.matching import persist_matches

def main():
    Base.metadata.create_all(engine)
    db = SessionLocal()
    try:
        user = db.scalar(select(User).where(User.email == "demo@lostlink.ai"))
        if not user:
            user = User(email="demo@lostlink.ai", name="Demo User", password_hash=hash_password("DemoPass123!"))
            db.add(user)
            db.flush()

        if db.scalar(select(Report).limit(1)) is None:
            t = datetime.now(timezone.utc)
            r1 = Report(
                user_id=user.id, type="lost", category="backpack",
                description="Black backpack with orange zipper and small white rectangular logo.",
                color="black", location_name="Library", latitude=28.628, longitude=77.365,
                event_time=t - timedelta(minutes=45)
            )
            r2 = Report(
                user_id=user.id, type="found", category="backpack",
                description="Dark school bag with orange zip and small white logo.",
                color="black", location_name="Cafeteria", latitude=28.631, longitude=77.368,
                event_time=t
            )
            db.add_all([r1, r2])
            db.commit()
            persist_matches(db, r1)
            persist_matches(db, r2)
        print("Seed complete. Demo login: demo@lostlink.ai / DemoPass123!")
    finally:
        db.close()

if __name__ == "__main__":
    main()
