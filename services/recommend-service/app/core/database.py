from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase
from app.core.config import settings

engine = create_async_engine(
    settings.POSTGRES_URL,
    echo=settings.DEBUG,
    pool_pre_ping=True,
    pool_size=10,
    max_overflow=20,
)

AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autoflush=False,
    autocommit=False,
)


class Base(DeclarativeBase):
    pass


async def get_db() -> AsyncSession:
    """Dependency: yields an async DB session."""
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


import asyncio
import logging

logger = logging.getLogger(__name__)

async def init_db():
    """Create all tables on startup with retry logic."""
    max_retries = 5
    retry_delay = 5
    
    for attempt in range(1, max_retries + 1):
        try:
            async with engine.begin() as conn:
                from app.models import book  # noqa: F401 - registers models
                await conn.run_sync(Base.metadata.create_all)
            logger.info("✅ Database initialized successfully.")
            return
        except Exception as e:
            if attempt == max_retries:
                logger.error(f"❌ Failed to initialize database after {max_retries} attempts: {e}")
                raise
            logger.warning(f"⚠️ Database initialization attempt {attempt} failed. Retrying in {retry_delay}s... Error: {e}")
            await asyncio.sleep(retry_delay)
