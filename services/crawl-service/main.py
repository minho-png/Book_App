from fastapi import FastAPI
from app.routers import health_router, crawl_router
from app.core.database import init_db
from app.services.scheduler import start_scheduler, stop_scheduler
from contextlib import asynccontextmanager
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("crawl-service")

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("🚀 Crawl Service Starting")
    await init_db()
    await start_scheduler()
    yield
    stop_scheduler()
    logger.info("🛑 Crawl Service Shutting Down")

app = FastAPI(title="Crawl Service", lifespan=lifespan)

app.include_router(health_router)
app.include_router(crawl_router)
