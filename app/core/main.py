from fastapi import FastAPI
#from app.models import Base, engine
from app.core.database import init_database
from app.routers import user
from app.routers import auth_router

init_database()
app = FastAPI()


@app.get("/")
async def root():
    return {"message": "Hello World"}


@app.get("/hello/{name}")
async def say_hello(name: str):
    return {"message": f"Hello {name}"}

#app.include_router(user.router)
app.include_router(auth_router.router)
