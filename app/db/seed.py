from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.models.user import User
from app.models.course import Course
from app.core.security import get_password_hash
from datetime import datetime

def seed_users(db: Session):
    if db.query(User).count() == 0:
        print("Seeding users...")
        users = [
            User(
                name="Admin Global", # PAKE name
                email="admin@global.academy",
                password=get_password_hash("admin123"), # PAKE password
                role="admin" # PAKE role
            ),
            User(
                name="Siswa Testing",
                email="siswa@global.academy",
                password=get_password_hash("siswa123"),
                role="student" # DEFAULT LU student
            )
        ]
        db.add_all(users)
        db.commit()
        print("Seeding users done!")
    else:
        print("Users exist. Skip seeding.")

def seed_courses(db: Session):
    if db.query(Course).count() == 0:
        print("Seeding courses...")
        admin = db.query(User).filter(User.role == "admin").first()
        admin_id = admin.id if admin else 1

        courses = [
            Course(
                title="Belajar FastAPI dari 0 Jadi Pro",
                description="Course terlengkap buat jago FastAPI + deploy ke Railway",
                price=199000,
                instructor_id=admin_id,
                created_at=datetime.now(),
                updated_at=datetime.now()
            ),
        ]
        db.add_all(courses)
        db.commit()
        print("Seeding courses done!")
    else:
        print("Courses exist. Skip seeding.")

def run_seed():
    db: Session = SessionLocal()
    try:
        seed_users(db)
        seed_courses(db)
    finally:
        db.close()