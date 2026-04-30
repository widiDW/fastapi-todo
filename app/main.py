from fastapi import FastAPI
from app.database import Base, engine
from app.routers import user, todo

Base.metadata.create_all(bind=engine)

app = FastAPI(title="API Python Jhon")
swagger_ui_parameters={"persistAuthorization": True}

# Include router
app.include_router(user.router)
app.include_router(todo.router)

@app.get("/")
def root():
    return {"status": "API Jhon udah pake MVC 🔥"}