import enum
from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from app.database import Base

class UserRole(str, enum.Enum):
    student = "student"
    instructor = "instructor"
    admin = "admin"
    super_admin = "super_admin"
    
class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    email = Column(String(255), unique=True, nullable=False, index=True)
    hashed_password = Column(String(255), nullable=False)
    avatar_url = Column(String(500), nullable=True)
    role = Column(String(20), default=UserRole.student.value, nullable=False)

    courses = relationship("Course", back_populates="instructor")
    enrollments = relationship("Enrollment", back_populates="user", cascade="all, delete-orphan")