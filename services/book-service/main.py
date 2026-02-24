from fastapi import FastAPI
from app.routers import health_router, books_router
from app.core.database import init_db
from contextlib import asynccontextmanager
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("book-service")

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("🚀 Book Service Starting")
    await init_db()
    yield
    logger.info("🛑 Book Service Shutting Down")

app = FastAPI(title="Book Service", lifespan=lifespan)

app.include_router(health_router)
app.include_router(books_router)
