from sqlalchemy import Column, Integer, ForeignKey, String, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base

class Enrollment(Base):
    __tablename__ = "enrollments"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    course_id = Column(Integer, ForeignKey("courses.id"), nullable=False)
    status = Column(String(50), default="active")
    
    enrolled_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Biar 1 user ga bisa daftar course yg sama 2x
    __table_args__ = (
        # Unique constraint: user_id + course_id harus unik
    )
    
    user = relationship("User", back_populates="enrollments")
    course = relationship("Course", back_populates="enrollments")