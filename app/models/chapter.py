from sqlalchemy import Column, Integer, String, ForeignKey, Text, DateTime
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.database import Base

class Chapter(Base):
    __tablename__ = "chapters"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False)
    order = Column(Integer, default=0)
    
    # TAMBAHIN INI JOHNN - buat nyimpen isi chapter
    content = Column(Text, nullable=True)  
    
    course_id = Column(Integer, ForeignKey("courses.id", ondelete="CASCADE"), nullable=False)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # RELATIONSHIP KE COURSE
    course = relationship("Course", back_populates="chapters")

    # RELATIONSHIP KE LESSON - INI KUNCI NYA JOHNN
    lessons = relationship(
        "Lesson",
        back_populates="chapter",
        cascade="all, delete-orphan"  # <- Kalo chapter kehapus, lesson ikut kehapus
    )