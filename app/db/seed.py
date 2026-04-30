from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.models.user import User
from app.models.course import Course
from app.core.security import get_password_hash

def run_seed():
    db = SessionLocal()
    try:
        if db.query(User).first():
            print("DB already seeded")
            return

        admin = User(
            name="Admin",
            email="admin@global.com",
            password=get_password_hash("admin123"),
            role="instructor"
        )
        db.add(admin)
        db.commit()
        db.refresh(admin)

        course = Course(
            title="Belajar FastAPI dari 0 Jadi Pro",
            description="Course terlengkap buat jago FastAPI + deploy ke Railway",
            price=199000,
            instructor_id=admin.id
        )
        db.add(course)
        db.commit()
        print("Seeding done")
    finally:
        db.close()