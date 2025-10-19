from contextlib import asynccontextmanager
from fastapi import FastAPI
import uvicorn
from app.data.CoreDB import db
from app.web import api
import logging

logger = logging.getLogger("main")

logging.basicConfig(
    level=logging.INFO,          # or DEBUG
    format="%(asctime)s - %(levelname)s - %(message)s",
    force=True                  # <- important, overrides previous logging config
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    await db.init()
    try:
        yield
    finally:
        await db.close()

app = FastAPI(title="My App", lifespan=lifespan)
app.include_router(api.router, prefix="/api")


@app.get("/")
def root():
    logger.info('{"message1": "Hello FastAPI"}')
    return {"message": "Hello FastAPI"}


if __name__ == " __main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
