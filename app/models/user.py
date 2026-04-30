from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from app.database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), index=True) # PAKE NAME
    email = Column(String(255), unique=True, index=True)
    password = Column(String(255)) # PAKE PASSWORD
    role = Column(String(20), default="student", nullable=False)
    avatar_url = Column(String, nullable=True)

    courses = relationship("Course", back_populates="instructor")
    enrollments = relationship("Enrollment", back_populates="student")