from sqlalchemy.orm import Session
from .database import SessionLocal
from . import models
from .auth import get_password_hash

def seed_data():
    db = SessionLocal()
    try:
        # 1. Bikin Instructor kalo belum ada
        instructor = db.query(models.User).filter(models.User.email == "instructor@global.academy").first()
        if not instructor:
            instructor = models.User(
                name="Budi Santoso",
                email="instructor@global.academy",
                password=get_password_hash("password123"),
                role="instructor"
            )
            db.add(instructor)
            db.commit()
            db.refresh(instructor)
            print("Instructor created")

        # 2. Bikin Course kalo belum ada
        course = db.query(models.Course).filter(models.Course.slug == "belajar-fastapi-pro").first()
        if not course:
            course = models.Course(
                title="Belajar FastAPI dari 0 Jadi Pro",
                slug="belajar-fastapi-pro",
                description="Course terlengkap buat jago FastAPI + deploy ke Railway",
                price=199000,
                thumbnail_url="https://i.imgur.com/8x8x8x8.png",
                instructor_id=instructor.id
            )
            db.add(course)
            db.commit()
            db.refresh(course)
            print("Course created")

            # 3. Bikin Module 1
            module1 = models.Module(title="Pengenalan FastAPI", order=1, course_id=course.id)
            db.add(module1)
            db.commit()
            db.refresh(module1)

            # 4. Bikin Lesson di Module 1
            lessons = [
                models.Lesson(title="Apa itu FastAPI?", content_type="video", content_url="https://youtube.com/watch?v=xxx", duration_minutes=10, order=1, module_id=module1.id),
                models.Lesson(title="Install Python & VSCode", content_type="video", content_url="https://youtube.com/watch?v=yyy", duration_minutes=15, order=2, module_id=module1.id),
            ]
            db.add_all(lessons)
            db.commit()
            print("Module + Lessons created")

        print("Seeding Global Academy done")
    finally:
        db.close()

if __name__ == "__main__":
    seed_data()