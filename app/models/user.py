from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from ..database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), index=True)      # <-- Kasih 100
    email = Column(String(255), unique=True, index=True) # <-- Kasih 255
    password = Column(String(255))              # <-- Kasih 255, hash bcrypt panjang
    role = Column(String(20), default="student", nullable=False) # <-- Kasih 20
    avatar_url = Column(String, nullable=True)
    courses = relationship("Course", back_populates="instructor") # Course yg diajar user ini
    enrollments = relationship("Enrollment", back_populates="student") # Course yg dia ikutin