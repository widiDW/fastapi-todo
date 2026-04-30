from sqlalchemy import Column, Integer, String, Text, ForeignKey
from sqlalchemy.orm import relationship
from ..database import Base
from sqlalchemy.sql.sqltypes import DateTime
from sqlalchemy.sql import func

class Course(Base):
    __tablename__ = "courses"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False, index=True)
    slug = Column(String(255), unique=True, nullable=False, index=True) # buat URL: /course/belajar-fastapi
    description = Column(Text)
    price = Column(Integer, default=0) # 0 = gratis. Simpel pake Integer dulu
    thumbnail_url = Column(String(500), nullable=True)
    
    instructor_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

# Relasi balik ke User/Instructor
    
    # Relasi balik ke User/Instructor
    instructor = relationship("User", back_populates="courses")
    
    # Relasi ke Module - 1 course punya banyak module
    modules = relationship("Module", back_populates="course", cascade="all, delete-orphan")
    
    # Relasi ke Enrollment - buat tau siapa aja yg daftar
    enrollments = relationship("Enrollment", back_populates="course", cascade="all, delete-orphan")