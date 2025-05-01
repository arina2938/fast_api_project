from fastapi import FastAPI
#from app.models import Base, engine
from app.schemas.database import init_database


init_database()
app = FastAPI()


@app.get("/")
async def root():
    return {"message": "Hello World"}


@app.get("/hello/{name}")
async def say_hello(name: str):
    return {"message": f"Hello {name}"}
