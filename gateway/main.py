from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
import httpx
import os
import logging

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("gateway")

app = FastAPI(title="BookCurator Gateway")

#── CORS 설정 (시스템의 유일한 CORS 권위자) ──────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # 실제 운영환경에서는 Vercel URL 등으로 제한 권장
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

#── 서비스 URL 설정 (환경변수 또는 로컬 기본값) ────────────────
BOOK_SERVICE_URL = os.getenv("BOOK_SERVICE_URL", "http://localhost:8001")
CRAWL_SERVICE_URL = os.getenv("CRAWL_SERVICE_URL", "http://localhost:8002")
RECOMMEND_SERVICE_URL = os.getenv("RECOMMEND_SERVICE_URL", "http://localhost:8003")

@app.get("/health")
async def health():
    return {"status": "ok", "service": "gateway-fastapi"}

def get_target_url(path: str):
    """경로에 따라 대상 서비스 URL을 결정합니다."""
    if path.startswith("api/books"):
        return f"{BOOK_SERVICE_URL}/{path}"
    elif path.startswith("api/crawl"):
        return f"{CRAWL_SERVICE_URL}/{path}"
    elif path.startswith("api/recommend"):
        return f"{RECOMMEND_SERVICE_URL}/{path}"
    # 기본값
    return f"{BOOK_SERVICE_URL}/{path}"

@app.api_route("/{path:path}", methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"])
async def proxy(request: Request, path: str):
    """요청 경로에 맞춰 적절한 서비스로 프록시합니다."""
    url = get_target_url(path)
    
    # 쿼리 파라미터 포함
    if request.query_params:
        url += f"?{request.query_params}"

    # 요청 바디 읽기
    body = await request.body()
    headers = dict(request.headers)
    headers.pop("host", None)

    async def stream_backend():
        async with httpx.AsyncClient(timeout=300.0) as client:
            async with client.stream(
                method=request.method,
                url=url,
                content=body,
                headers=headers
            ) as response:
                async for chunk in response.aiter_bytes():
                    yield chunk

    return StreamingResponse(
        stream_backend(),
        media_type="application/x-ndjson" if "recommend" in path else "application/json"
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=80)
