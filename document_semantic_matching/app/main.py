import logging
from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI
from app.config.logging_config import setup_logging
from app.database.vector_db import db
from app.routers import app_router

# Initialize global logging before other imports
setup_logging()
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app_ins: FastAPI):
    print(f'start: {app_ins.__str__()}')
    await db.init()
    try:
        yield
    finally:
        print('finish')


app = FastAPI(title="doc App", lifespan=lifespan)
app.include_router(app_router.router, prefix="/api")


@app.get("/")
def root():
    logger.info('{"message1": "Hello doc server"}')
    return {"message": "Hello doc server"}


if __name__ == " __main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
