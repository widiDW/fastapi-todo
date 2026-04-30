from fastapi import FastAPI
from app.database import Base, engine
from app.routers import course, user
from app import auth # TAMBAHIN INI. Karena auth.py di luar folder routers

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Global Academy API", 
    swagger_ui_parameters={"persistAuthorization": True} # MASUKIN KE DALEM SINI
)

# Include router
app.include_router(user.router)
app.include_router(auth.router) # UDAH KEBACA SEKARANG
app.include_router(course.router)

@app.get("/")
def root():
    return {"status": "Global Academy API udah online 🔥"}