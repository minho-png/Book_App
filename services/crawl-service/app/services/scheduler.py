"""
백그라운드 자동 크롤링 스케줄러
- 앱 시작 시 즉시 크롤링 실행 (DB가 비어있을 때)
- 이후 CRAWL_INTERVAL_HOURS마다 자동 반복
- 사용자에게 완전히 투명하게 서버 내부에서만 동작
"""
import asyncio
import logging
from datetime import datetime, timezone

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from sqlalchemy import func, select

from app.core.config import settings
from app.core.database import AsyncSessionLocal
from app.models.book import Book
from app.services.crawler_service import run_crawl

logger = logging.getLogger(__name__)

STORES = ["kyobo", "aladdin", "millie"]

# 전역 스케줄러 인스턴스 (lifespan에서 start/stop)
scheduler = AsyncIOScheduler(timezone="Asia/Seoul")


async def _crawl_all_stores() -> None:
    """모든 서점 순차 크롤링 후 DB 저장 (내부 백그라운드 태스크)."""
    logger.info("🕷️  [Scheduler] 주간 정기 크롤링 시작 (일->월 00:00)")
    async with AsyncSessionLocal() as db:
        for store in STORES:
            try:
                log = await run_crawl(store=store, db=db)
                logger.info(
                    f"✅ [{store}] 크롤링 완료 — {log.books_found}건 저장"
                )
            except Exception as e:
                logger.error(f"❌ [{store}] 크롤링 실패: {e}")
    logger.info("🕷️  [Scheduler] 주간 정기 크롤링 종료")


async def _has_any_books() -> bool:
    """DB에 도서 데이터가 이미 존재하는지 확인."""
    async with AsyncSessionLocal() as db:
        result = await db.execute(select(func.count()).select_from(Book))
        count = result.scalar_one()
        return count > 0


async def start_scheduler() -> None:
    """
    스케줄러 시작:
    1. DB가 비어있으면 즉시 크롤링 실행 (첫 구동 시 데이터 확보)
    2. 매주 월요일 00:00에 정기 크롤링 등록
    """
    # DB 비어있을 때만 즉시 크롤링 (중복 수집 방지)
    if not await _has_any_books():
        logger.info("📚 [Scheduler] DB 초기 데이터 없음 → 즉시 크롤링 시작")
        asyncio.create_task(_crawl_all_stores())
    else:
        logger.info("📚 [Scheduler] DB에 기존 데이터 존재 → 정기 예약만 등록")

    # 매주 월요일 00:00 (일요일에서 월요일로 넘어가는 자정)
    scheduler.add_job(
        _crawl_all_stores,
        trigger=CronTrigger(day_of_week='mon', hour=0, minute=0),
        id="weekly_crawl",
        replace_existing=True,
    )
    scheduler.start()
    logger.info("⏰ [Scheduler] 매주 월요일 00:00 정기 크롤링 예약 완료")


def stop_scheduler() -> None:
    """앱 종료 시 스케줄러 정리."""
    if scheduler.running:
        scheduler.shutdown(wait=False)
        logger.info("🛑 [Scheduler] 종료")
