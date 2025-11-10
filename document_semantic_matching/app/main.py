import logging
from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI

from app.config.Settings import get_settings
from app.config.logging_config import setup_logging
from app.database.data.batch_insert import batch_insert_async
from app.database.vector_db import db
from app.routers import app_router

# Initialize global logging before other imports
setup_logging()
logger = logging.getLogger(__name__)
app_name = get_settings().APP_NAME
port = get_settings().PORT


@asynccontextmanager
async def lifespan(app_ins: FastAPI):
    print(f'start: {app_ins.__str__()}')
    await db.init()
    await batch_insert_async()
    try:
        yield
    finally:
        await db.close()
        print('finish')


app = FastAPI(title=app_name, lifespan=lifespan)
app.include_router(app_router.router, prefix="/api")


@app.get("/")
async def health():
    logger.info('{"health": "Server in fine health"}')
    return {"health": "Server in fine health"}


if __name__ == " __main__":
    uvicorn.run("main:app", host="127.0.0.1", port=port, reload=True)
