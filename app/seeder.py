from sqlalchemy.orm import Session
from .database import SessionLocal, engine, Base
from .models.user import User  # <-- UDAH GUA GANTI
from .auth import get_password_hash
import os
from dotenv import load_dotenv
from faker import Faker

load_dotenv()
fake = Faker('id_ID')

def seed_admin():
    Base.metadata.create_all(bind=engine)
    db: Session = SessionLocal()
    
    # 1. SEED ADMIN
    admin_email = os.getenv("SEEDER_ADMIN_EMAIL", "admin@jhon.com")
    admin_pass = os.getenv("SEEDER_ADMIN_PASS", "admin123")
    
    admin_exist = db.query(User).filter(User.email == admin_email).first()
    if not admin_exist:
        admin_user = User(
            nama="Super Admin Jhon",
            email=admin_email, 
            umur=99,
            password=get_password_hash(admin_pass),
            role="admin"
        )
        db.add(admin_user)
        print(f"✅ Admin {admin_email} dibuat")
    else:
        print(f"⚠️  Admin {admin_email} udah ada, skip")

    # 2. SEED 10 USER RANDOM
    user_count = db.query(User).filter(User.role == "user").count()
    if user_count < 10:
        print("🔄 Bikin 10 user dummy...")
        for i in range(10 - user_count):
            user = User(
                nama=fake.name(),
                email=fake.unique.email(),
                umur=fake.random_int(17, 60),
                password=get_password_hash("password"),
                role="user"
            )
            db.add(user)
        print("✅ 10 user dummy berhasil dibuat. Pass: password")
    else:
        print(f"⚠️  User dummy udah ada {user_count} biji, skip")

    db.commit()
    db.close()
    print("\n🔥 SEEDER SELESAI JHON 🔥")

if __name__ == "__main__":
    seed_admin()