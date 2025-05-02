from fastapi import FastAPI
from app.core.database import init_database
from app.routers import auth_router
from app.routers import concert
from app.routers import composer_route
from app.routers import instruments_router
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
app.include_router(concert.router)
app.include_router(composer_route.router)
app.include_router(instruments_router.router)
