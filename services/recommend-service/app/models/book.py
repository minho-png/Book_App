from datetime import datetime
from typing import Optional
from sqlalchemy import String, Float, Integer, DateTime, Text, ForeignKey, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.core.database import Base


class Book(Base):
    __tablename__ = "books"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    title: Mapped[str] = mapped_column(String(300), nullable=False, index=True)
    author: Mapped[str] = mapped_column(String(200), nullable=False)
    genre: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    cover_color: Mapped[Optional[str]] = mapped_column(String(20), nullable=True, default="#5B8FA8")
    rating: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    isbn: Mapped[Optional[str]] = mapped_column(String(20), nullable=True, unique=True)
    publisher: Mapped[Optional[str]] = mapped_column(String(200), nullable=True)
    published_date: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    image_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), onupdate=func.now()
    )
    crawled_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)

    # Relationships
    rankings: Mapped[list["BookRanking"]] = relationship(
        "BookRanking", back_populates="book", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<Book id={self.id} title={self.title!r}>"


class BookRanking(Base):
    __tablename__ = "book_rankings"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    book_id: Mapped[int] = mapped_column(Integer, ForeignKey("books.id"), nullable=False)
    store: Mapped[str] = mapped_column(String(50), nullable=False)   # kyobo, millie, aladdin
    category: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    rank: Mapped[int] = mapped_column(Integer, nullable=False)
    rank_date: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    book: Mapped["Book"] = relationship("Book", back_populates="rankings")

    def __repr__(self) -> str:
        return f"<BookRanking store={self.store} rank={self.rank}>"


class CrawlLog(Base):
    __tablename__ = "crawl_logs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    store: Mapped[str] = mapped_column(String(50), nullable=False)
    status: Mapped[str] = mapped_column(String(20), nullable=False)   # running, done, error
    books_found: Mapped[int] = mapped_column(Integer, default=0)
    error_message: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    started_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    finished_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
