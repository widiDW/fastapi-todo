from fastapi import FastAPI
from app.database import engine, Base
from app.auth import router as auth_router
from app.db.seed import run_seed
from app.routers import user, course, chapter, enrollment

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Global Academy API")

@app.on_event("startup")
def on_startup():
    run_seed()

app.include_router(auth_router, tags=["Auth"])
app.include_router(user.router, tags=["Users"])
app.include_router(course.router, tags=["Courses"])
app.include_router(chapter.router, tags=["Chapters"])
app.include_router(enrollment.router, tags=["Enrollments"])

@app.get("/")
def root():
    return {"message": "Global Academy API - IJO"}