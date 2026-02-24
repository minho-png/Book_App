from datetime import datetime
from typing import Optional, Dict
from pydantic import BaseModel, Field


# ── Book ──────────────────────────────────────────────────────────────────────

class BookRankingOut(BaseModel):
    store: str
    category: Optional[str] = None
    rank: int
    rank_date: datetime

    class Config:
        from_attributes = True


class BookOut(BaseModel):
    id: int
    title: str
    author: str
    genre: Optional[str] = None
    description: Optional[str] = None
    cover_color: Optional[str] = "#5B8FA8"
    rating: Optional[float] = None
    isbn: Optional[str] = None
    publisher: Optional[str] = None
    published_date: Optional[str] = None
    image_url: Optional[str] = None
    crawled_at: Optional[datetime] = None
    rankings: list[BookRankingOut] = []

    class Config:
        from_attributes = True


class BookCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=300)
    author: str = Field(..., min_length=1, max_length=200)
    genre: Optional[str] = None
    description: Optional[str] = None
    cover_color: Optional[str] = "#5B8FA8"
    rating: Optional[float] = Field(None, ge=0, le=5)
    isbn: Optional[str] = None
    publisher: Optional[str] = None
    published_date: Optional[str] = None
    image_url: Optional[str] = None


# ── Recommend / Chat ───────────────────────────────────────────────────────────

class RecommendRequest(BaseModel):
    query: str = Field(..., min_length=1, max_length=500, description="사용자 도서 추천 요청")
    max_books: int = Field(default=6, ge=1, le=20)


class SourceData(BaseModel):
    store: str                   # kyobo | millie | aladdin
    category: str
    confidence: int = Field(ge=0, le=100)


# Server-Sent Event / JSON Streaming chunk
class StreamChunk(BaseModel):
    type: str   # "text" | "books" | "sources" | "done" | "error"
    data: object


# ── Crawling ───────────────────────────────────────────────────────────────────

class CrawlStatusOut(BaseModel):
    id: int
    store: str
    status: str
    books_found: int
    error_message: Optional[str] = None
    started_at: datetime
    finished_at: Optional[datetime] = None

    class Config:
        from_attributes = True
