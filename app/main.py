from fastapi import FastAPI
from app.database import engine, Base
from app.routers.user import router as user_router
from app.routers.course import router as course_router
from app.auth import router as auth_router
from app.db.seed import run_seed
from app.routers import user, course, chapter, enrollment

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Global Academy API")

@app.on_event("startup")
def on_startup():
    run_seed()

app.include_router(user_router, prefix="/api/v1", tags=["Users"])
app.include_router(course_router, prefix="/api/v1", tags=["Courses"])
app.include_router(auth_router, prefix="/api/v1", tags=["Auth"])

app.include_router(user.router, tags=["users"])
app.include_router(course.router, prefix="/api/v1", tags=["courses"])
app.include_router(chapter.router, prefix="/api/v1", tags=["chapters"])
app.include_router(enrollment.router, prefix="/api/v1", tags=["enrollments"])

@app.get("/")
def root():
    return {"message": "Global Academy API - IJO"}