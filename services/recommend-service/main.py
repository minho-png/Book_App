from fastapi import FastAPI
from app.routers import health_router, recommend_router
from app.core.database import init_db
from contextlib import asynccontextmanager
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("recommend-service")

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("🚀 Recommend Service Starting")
    await init_db()
    yield
    logger.info("🛑 Recommend Service Shutting Down")

app = FastAPI(title="Recommend Service", lifespan=lifespan)

app.include_router(health_router)
app.include_router(recommend_router)
