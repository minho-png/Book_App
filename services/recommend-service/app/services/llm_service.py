"""
LLM Service - Google Gemini API 연동
GOOGLE_MODEL_NAME 환경변수로 모델명 동적 지정
JSON 스트리밍 응답 생성
"""
import json
import logging
from typing import AsyncGenerator

import google.generativeai as genai
from google.generativeai.types import GenerationConfig

from app.core.config import settings

logger = logging.getLogger(__name__)


def _get_client(api_key: Optional[str] = None) -> genai.GenerativeModel:
    """Gemini 클라이언트 생성 (제공된 키 또는 환경변수 기반)."""
    target_key = api_key or settings.GOOGLE_API_KEY
    if not target_key:
        raise ValueError("Google API Key가 설정되지 않았습니다.")
        
    genai.configure(api_key=target_key)
    return genai.GenerativeModel(
        model_name=settings.GOOGLE_MODEL_NAME,
        generation_config=GenerationConfig(
            temperature=0.7,
            max_output_tokens=2048,
        ),
    )


def _build_prompt(query: str, books_context: str, max_books: int) -> str:
    return f"""당신은 한국 도서 추천 전문 큐레이터입니다.
사용자 요청: "{query}"

현재 서점 베스트셀러 데이터:
{books_context}

지시사항:
1. 사용자 요청에 가장 적합한 도서 {max_books}권을 선정하세요.
2. 먼저 자연스러운 한국어로 1~2 문단의 추천 이유를 작성하세요.
3. 그 다음 아래 JSON 형식으로 도서 목록을 출력하세요:

### BOOKS_JSON ###
[
  {{
    "id": "1",
    "title": "도서제목",
    "author": "저자명",
    "genre": "장르",
    "rating": 4.5,
    "description": "간단한 설명 (50자 이내)",
    "cover_color": "#HEX색상코드",
    "rankings": {{"kyobo": 1, "aladdin": 2}}
  }}
]
### END_JSON ###

### SOURCES_JSON ###
[
  {{"store": "kyobo", "category": "종합 베스트셀러", "confidence": 95}},
  {{"store": "aladdin", "category": "주간 베스트", "confidence": 88}}
]
### END_SOURCES ###

JSON 형식을 정확히 유지하세요. 마크다운 코드블록은 사용하지 마세요."""


async def stream_recommendation(
    query: str,
    books_context: str,
    max_books: int = 6,
    api_key: Optional[str] = None,
) -> AsyncGenerator[str, None]:
    """
    Gemini API 스트리밍으로 추천 텍스트+JSON 청크 생성.
    StreamChunk JSON line을 yield.
    """
    model = _get_client(api_key=api_key)
    prompt = _build_prompt(query, books_context, max_books)

    try:
        response = await model.generate_content_async(
            prompt,
            stream=True,
        )

        full_text = ""
        books_sent = False
        sources_sent = False

        async for chunk in response:
            if not chunk.text:
                continue

            full_text += chunk.text

            # 텍스트 파트를 실시간 스트리밍 (JSON 구분자 이전까지)
            if "### BOOKS_JSON ###" not in full_text:
                text_part = chunk.text
                yield json.dumps({"type": "text", "data": text_part}, ensure_ascii=False) + "\n"
            else:
                # 텍스트 파트가 있고 books/sources 파싱 가능할 때
                if not books_sent and "### END_JSON ###" in full_text:
                    try:
                        books_raw = full_text.split("### BOOKS_JSON ###")[1].split("### END_JSON ###")[0].strip()
                        books_data = json.loads(books_raw)
                        yield json.dumps({"type": "books", "data": books_data}, ensure_ascii=False) + "\n"
                        books_sent = True
                    except (json.JSONDecodeError, IndexError) as e:
                        logger.warning(f"books JSON 파싱 실패: {e}")

                if not sources_sent and "### END_SOURCES ###" in full_text:
                    try:
                        sources_raw = full_text.split("### SOURCES_JSON ###")[1].split("### END_SOURCES ###")[0].strip()
                        sources_data = json.loads(sources_raw)
                        yield json.dumps({"type": "sources", "data": sources_data}, ensure_ascii=False) + "\n"
                        sources_sent = True
                    except (json.JSONDecodeError, IndexError) as e:
                        logger.warning(f"sources JSON 파싱 실패: {e}")

        yield json.dumps({"type": "done", "data": None}) + "\n"

    except Exception as e:
        logger.error(f"LLM 스트리밍 오류: {e}")
        yield json.dumps({"type": "error", "data": str(e)}, ensure_ascii=False) + "\n"
