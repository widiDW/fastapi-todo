from fastapi import FastAPI
from app.database import Base, engine
from app.routers import course, user, auth
from app.db.seed import run_seed

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Global Academy API",
    swagger_ui_parameters={"persistAuthorization": True}
)

@app.on_event("startup")
async def startup_event():
    print("Running startup event...")
    run_seed()
    print("Startup event done!")

# Include router
app.include_router(user.router, prefix="/api/v1", tags=["Users"])
app.include_router(auth.router, prefix="/api/v1", tags=["Auth"])
app.include_router(course.router, prefix="/api/v1", tags=["Courses"])

@app.get("/")
def root():
    return {"status": "Global Academy API udah online 🔥"}