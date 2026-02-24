from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.schemas.book import BookOut
from app.services import book_service

router = APIRouter(prefix="/api/books", tags=["books"])


@router.get("", response_model=list[BookOut])
async def list_books(
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=50, ge=1, le=200),
    genre: Optional[str] = Query(default=None),
    store: Optional[str] = Query(default=None),
    db: AsyncSession = Depends(get_db),
):
    """도서 목록 조회 (필터링, 페이지네이션)."""
    books = await book_service.get_books(db, skip=skip, limit=limit, genre=genre, store=store)
    return books


@router.get("/search", response_model=list[BookOut])
async def search_books(
    q: str = Query(..., min_length=1, description="검색 키워드 (제목/저자)"),
    limit: int = Query(default=20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
):
    """도서 키워드 검색."""
    books = await book_service.search_books(db, query=q, limit=limit)
    return books


@router.get("/{book_id}", response_model=BookOut)
async def get_book(
    book_id: int,
    db: AsyncSession = Depends(get_db),
):
    """도서 단건 조회."""
    book = await book_service.get_book_by_id(db, book_id)
    if not book:
        raise HTTPException(status_code=404, detail="도서를 찾을 수 없습니다.")
    return book
