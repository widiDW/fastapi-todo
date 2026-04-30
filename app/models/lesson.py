from sqlalchemy import Column, Integer, String, Text, ForeignKey
from sqlalchemy.orm import relationship
from ..database import Base

class Lesson(Base):
    __tablename__ = "lessons"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False)
    content_type = Column(String(50), default="video") # video, text, quiz
    content_url = Column(Text, nullable=True) # URL video YouTube / S3
    duration_minutes = Column(Integer, default=0)
    order = Column(Integer, default=0) # Urutan materi dalam 1 bab
    
    module_id = Column(Integer, ForeignKey("modules.id", ondelete="CASCADE"), nullable=False)
    
    # Relationships
    module = relationship("Module", back_populates="lessons")