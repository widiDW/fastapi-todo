from fastapi import FastAPI
from app.database import engine, Base
from app.routers.user import router as user_router
from app.routers.course import router as course_router
from app.auth import router as auth_router  # FIX DISINI
from app.db.seed import run_seed

Base.metadata.create_all(bind=engine)

app = FastAPI()

@app.on_event("startup")
def on_startup():
    run_seed()

app.include_router(user_router, prefix="/api/v1", tags=["Users"])
app.include_router(course_router, prefix="/api/v1", tags=["Courses"])
app.include_router(auth_router, prefix="/api/v1", tags=["Auth"])

@app.get("/")
def root():
    return {"message": "Global Academy API"}