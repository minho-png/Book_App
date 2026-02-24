"""
Book Service - 도서 비즈니스 로직
DB 조회, 필터링, 베스트셀러 컨텍스트 생성
"""
import logging
from typing import Optional

from sqlalchemy import select, desc, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.book import Book, BookRanking

logger = logging.getLogger(__name__)


async def get_books(
    db: AsyncSession,
    skip: int = 0,
    limit: int = 50,
    genre: Optional[str] = None,
    store: Optional[str] = None,
) -> list[Book]:
    """도서 목록 조회 (필터링, 페이지네이션)."""
    query = select(Book).options(selectinload(Book.rankings))

    if genre:
        query = query.where(Book.genre.ilike(f"%{genre}%"))

    if store:
        query = query.join(Book.rankings).where(BookRanking.store == store)

    query = query.order_by(desc(Book.crawled_at)).offset(skip).limit(limit)
    result = await db.execute(query)
    return list(result.scalars().unique().all())


async def get_book_by_id(db: AsyncSession, book_id: int) -> Optional[Book]:
    """도서 ID로 단건 조회."""
    result = await db.execute(
        select(Book)
        .options(selectinload(Book.rankings))
        .where(Book.id == book_id)
    )
    return result.scalars().first()


async def get_bestseller_context(db: AsyncSession, limit: int = 30) -> str:
    """
    LLM 프롬프트용 베스트셀러 컨텍스트 문자열 생성.
    각 서점 상위 도서를 정형화된 텍스트로 반환.
    """
    # 최신 랭킹 기준 상위 도서
    result = await db.execute(
        select(Book)
        .options(selectinload(Book.rankings))
        .join(Book.rankings)
        .order_by(BookRanking.rank)
        .limit(limit)
    )
    books = list(result.scalars().unique().all())

    if not books:
        return "현재 베스트셀러 데이터가 없습니다. (크롤링 필요)"

    lines = []
    for book in books:
        store_ranks = ", ".join(
            f"{r.store} {r.rank}위" for r in book.rankings
        )
        desc = book.description[:60] + "..." if book.description and len(book.description) > 60 else (book.description or "")
        lines.append(
            f"- [{book.genre or '종합'}] {book.title} / {book.author} "
            f"| 평점: {book.rating or 'N/A'} | {store_ranks} | {desc}"
        )

    return "\n".join(lines)


async def search_books(db: AsyncSession, query: str, limit: int = 20) -> list[Book]:
    """제목/저자 키워드 검색."""
    result = await db.execute(
        select(Book)
        .options(selectinload(Book.rankings))
        .where(
            Book.title.ilike(f"%{query}%") | Book.author.ilike(f"%{query}%")
        )
        .limit(limit)
    )
    return list(result.scalars().unique().all())
