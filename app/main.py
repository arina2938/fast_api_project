"""Основной модуль FastAPI приложения.

Создает и настраивает экземпляр FastAPI, подключает маршруты.
"""

from typing import Dict
from fastapi import FastAPI
from app.database import init_database
from app.routers import (
    auth_router,
    concert_router,
    composer_route,
    instruments_router,
)

app = FastAPI(
    title="Concert API",
    description="API для управления концертами и участниками",
)

init_database()


@app.get("/", tags=["Root"])
async def root() -> Dict[str, str]:
    """Корневой маршрут для проверки работы API.

    Returns:
        Dict[str, str]: Приветственное сообщение
    """
    return {"message": "Hello World"}



app.include_router(auth_router.router)
app.include_router(concert_router.router)
app.include_router(composer_route.router)
app.include_router(instruments_router.router)
