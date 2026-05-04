from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.models import User, Course, Chapter, Enrollment
from passlib.context import CryptContext
from datetime import datetime

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)

def seed():
    db: Session = SessionLocal()
    try:
        # Cek kalau udah ada data, skip
        if db.query(User).first():
            print("⚠️ DB already seeded. Skip.")
            return

        print("🌱 Seeding users...")

        # 1. Buat 4 user dengan role berbeda
        users = [
            User(
                name="Super Admin",
                email="superadmin@global.com",
                hashed_password=get_password_hash("superadmin123"),
                role="super_admin" # ganti ke "super_admin" kalau di model lu pake underscore
            ),
            User(
                name="Admin",
                email="admin@global.com",
                hashed_password=get_password_hash("admin123"),
                role="admin"
            ),
            User(
                name="Instructor",
                email="instructor@global.com",
                hashed_password=get_password_hash("instructor123"),
                role="instructor"
            ),
            User(
                name="Student",
                email="student@global.com",
                hashed_password=get_password_hash("student123"),
                role="student"
            ),
        ]

        db.add_all(users)
        db.commit()

        # Refresh buat dapetin ID
        for user in users:
            db.refresh(user)

        instructor = users[2] # instructor@global.com
        student = users[3] # student@global.com
        admin = users[1] # admin@global.com

        print("✅ Users created")

        # 2. Buat 5 Course - 3 by instructor, 2 by admin
        print("🌱 Seeding courses...")
        courses_data = [
            {
                "title": "Belajar FastAPI dari 0 Jadi Pro",
                "description": "Course terlengkap buat jago FastAPI + deploy ke Railway",
                "price": 199000,
                "instructor_id": instructor.id,
                "published": True
            },
            {
                "title": "SQLAlchemy Deep Dive",
                "description": "Pahami ORM Python paling populer dari dasar sampai advanced",
                "price": 149000,
                "instructor_id": instructor.id,
                "published": True
            },
            {
                "title": "Docker untuk Developer",
                "description": "Containerize aplikasi Python kamu dengan Docker",
                "price": 99000,
                "instructor_id": instructor.id,
                "published": True
            },
            {
                "title": "React + FastAPI Fullstack",
                "description": "Bangun aplikasi fullstack modern dengan React dan FastAPI",
                "price": 249000,
                "instructor_id": admin.id,
                "published": True
            },
            {
                "title": "Deploy ke AWS + CI/CD",
                "description": "Deploy aplikasi ke AWS dengan GitHub Actions",
                "price": 199000,
                "instructor_id": admin.id,
                "published": False # draft course
            },
        ]

        courses = [Course(**course) for course in courses_data]
        db.add_all(courses)
        db.commit()

        for course in courses:
            db.refresh(course)

        print("✅ Courses created")

        # 3. Buat Chapters untuk setiap course yang dibuat instructor
        print("🌱 Seeding chapters...")
        chapters = []
        for i, course in enumerate(courses[:3]): # 3 course pertama by instructor
            for j in range(1, 4): # 3 chapter per course
                chapters.append(Chapter(
                    title=f"Chapter {j}: {course.title.split()[1]} Part {j}",
                    content=f"Ini adalah konten untuk chapter {j} dari course {course.title}. Lorem ipsum dolor sit amet.",
                    course_id=course.id,
                    order=j,
                    #duration_minutes=15 + (j * 5)
                ))

        db.add_all(chapters)
        db.commit()
        print(f"✅ {len(chapters)} Chapters created")

        # 4. Buat 5 Enrollment - student enroll ke semua course yang published
        print("🌱 Seeding enrollments...")
        published_courses = [c for c in courses if c.published]

        enrollments = []
        for i, course in enumerate(published_courses[:5]): # max 5 enrollment
            enrollments.append(Enrollment(
                user_id=student.id,
                course_id=course.id,
                status="active",
                enrolled_at=datetime.utcnow()
            ))

        db.add_all(enrollments)
        db.commit()
        print(f"✅ {len(enrollments)} Enrollments created")

        # 5. Summary
        print("\n🎉 SEEDING COMPLETED!")
        print("=" * 50)
        print("LOGIN CREDENTIALS:")
        print("superadmin@global.com | superadmin | superadmin")
        print("admin@global.com | admin123 | admin")
        print("instructor@global.com | instructor123 | instructor")
        print("student@global.com | student123 | student")
        print("=" * 50)
        print(f"Created: {len(users)} users, {len(courses)} courses, {len(chapters)} chapters, {len(enrollments)} enrollments")

    except Exception as e:
        print(f"❌ Error: {e}")
        db.rollback()
        raise
    finally:
        db.close()

if __name__ == "__main__":
    seed()