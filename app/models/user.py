from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from ..database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    nama = Column(String(100), index=True)      # <-- Kasih 100
    email = Column(String(255), unique=True, index=True) # <-- Kasih 255
    umur = Column(Integer)
    password = Column(String(255))              # <-- Kasih 255, hash bcrypt panjang
    role = Column(String(20), default="user", nullable=False) # <-- Kasih 20
    todos = relationship("Todo", back_populates="user", cascade="all, delete-orphan")