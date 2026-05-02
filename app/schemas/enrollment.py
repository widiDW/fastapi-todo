from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class EnrollmentBase(BaseModel):
    user_id: int
    course_id: int
    status: Optional[str] = "active"

class EnrollmentCreate(EnrollmentBase):
    pass

class EnrollmentOut(EnrollmentBase):
    id: int
    enrolled_at: datetime

    class Config:
        from_attributes = True