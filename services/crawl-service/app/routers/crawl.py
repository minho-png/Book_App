from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc

from app.core.database import get_db
from app.models.book import CrawlLog
from app.schemas.book import CrawlStatusOut
from app.services import crawler_service

router = APIRouter(prefix="/api/crawl", tags=["crawl"])

VALID_STORES = {"kyobo", "millie", "aladdin"}


@router.post("/trigger/{store}", response_model=CrawlStatusOut)
async def trigger_crawl(
    store: str,
    db: AsyncSession = Depends(get_db),
):
    """특정 서점 크롤링 실행 (백그라운드 실행이 아닌 즉시 실행, 완료 시 결과 반환)."""
    if store not in VALID_STORES:
        raise HTTPException(
            status_code=400,
            detail=f"지원하지 않는 서점입니다. 지원 목록: {', '.join(VALID_STORES)}"
        )
    log = await crawler_service.run_crawl(store=store, db=db)
    return log


@router.post("/trigger/all", response_model=list[CrawlStatusOut])
async def trigger_all_crawl(db: AsyncSession = Depends(get_db)):
    """모든 서점 크롤링 순차 실행."""
    results = []
    for store in VALID_STORES:
        log = await crawler_service.run_crawl(store=store, db=db)
        results.append(log)
    return results


@router.get("/status", response_model=list[CrawlStatusOut])
async def crawl_status(
    limit: int = 20,
    db: AsyncSession = Depends(get_db),
):
    """최근 크롤링 이력 조회."""
    result = await db.execute(
        select(CrawlLog).order_by(desc(CrawlLog.started_at)).limit(limit)
    )
    return list(result.scalars().all())
