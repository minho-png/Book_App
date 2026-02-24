from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.schemas.book import RecommendRequest
from app.services import book_service, llm_service

router = APIRouter(prefix="/api/recommend", tags=["recommend"])


@router.post("")
async def recommend(
    request: RecommendRequest,
    db: AsyncSession = Depends(get_db),
):
    """
    LLM 스트리밍 도서 추천.
    응답은 JSON Lines (newline-delimited JSON) 형식:
      {"type": "text",    "data": "..."}
      {"type": "books",   "data": [...]}
      {"type": "sources", "data": [...]}
      {"type": "done",    "data": null}
    """
    # DB 베스트셀러 컨텍스트 생성
    books_context = await book_service.get_bestseller_context(db, limit=30)

    async def event_generator():
        async for chunk in llm_service.stream_recommendation(
            query=request.query,
            books_context=books_context,
            max_books=request.max_books,
            api_key=request.google_api_key,
        ):
            yield chunk

    return StreamingResponse(
        event_generator(),
        media_type="application/x-ndjson",
        headers={"X-Content-Type-Options": "nosniff"},
    )
