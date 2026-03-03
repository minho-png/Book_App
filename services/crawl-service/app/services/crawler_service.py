"""
Crawler Service - Selenium + ChromeDriver (headless) 기반
각 서점(교보문고, 알라딘, 밀리의서재) 베스트셀러 크롤링
"""
import asyncio
import logging
import time
import os
from datetime import datetime
from typing import Optional

from selenium import webdriver
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.config import settings
from app.models.book import Book, BookRanking, CrawlLog

logger = logging.getLogger(__name__)

STORE_COLORS = {
    "kyobo":   "#C4956A",
    "millie":  "#7BA08A",
    "aladdin": "#5B8FA8",
}

GENRE_MAP = {
    "소설": "소설",
    "자기계발": "자기계발",
    "경제": "경제/경영",
    "경영": "경제/경영",
    "역사": "역사/문화",
    "과학": "과학",
    "에세이": "에세이",
    "시": "시/에세이",
    "아동": "아동",
    "청소년": "청소년",
}


def _build_chrome_driver() -> webdriver.Chrome:
    """공통 ChromeDriver 생성 (headless, 봇 감지 우회)."""
    opts = Options()
    opts.add_argument("--headless=new")
    opts.add_argument("--no-sandbox")
    opts.add_argument("--disable-dev-shm-usage")
    opts.add_argument("--disable-gpu")
    opts.add_argument("--disable-software-rasterizer")
    opts.add_argument("--remote-debugging-port=9222")
    opts.add_argument("--window-size=1920,1080")
    opts.add_argument(
        "--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/122.0.0.0 Safari/537.36"
    )
    # 봇 감지 방지
    opts.add_experimental_option("excludeSwitches", ["enable-automation"])
    opts.add_experimental_option("useAutomationExtension", False)

    # Docker 환경 등에서 시스템 chromedriver를 우선 사용하도록 설정
    chromedriver_path = "/usr/bin/chromedriver"
    if not os.path.exists(chromedriver_path):
        chromedriver_path = "/usr/local/bin/chromedriver"
        
    if os.path.exists(chromedriver_path):
        logger.info(f"Using system chromedriver: {chromedriver_path}")
        service = Service(executable_path=chromedriver_path)
    else:
        logger.info("System chromedriver not found. Installing via ChromeDriverManager...")
        service = Service(ChromeDriverManager().install())
    
    driver = webdriver.Chrome(service=service, options=opts)
    driver.execute_cdp_cmd(
        "Page.addScriptToEvaluateOnNewDocument",
        {"source": "Object.defineProperty(navigator, 'webdriver', {get: () => undefined})"},
    )
    return driver


def _scroll_to_bottom(driver):
    """지연 로딩된 이미지를 위해 페이지 끝까지 스크롤."""
    last_height = driver.execute_script("return document.body.scrollHeight")
    while True:
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(1)
        new_height = driver.execute_script("return document.body.scrollHeight")
        if new_height == last_height:
            break
        last_height = new_height


def _safe_find(driver, by: By, selector: str, timeout: int = 10) -> Optional[object]:
    """None 반환하는 safe WebDriverWait 래퍼."""
    try:
        return WebDriverWait(driver, timeout).until(
            EC.presence_of_element_located((by, selector))
        )
    except TimeoutException:
        return None


# ── 교보문고 ─────────────────────────────────────────────────────────────────

def _crawl_kyobo_sync() -> list[dict]:
    """교보문고 종합 베스트셀러 크롤링 (동기)."""
    driver = _build_chrome_driver()
    books: list[dict] = []
    try:
        # 최신 URL로 업데이트
        url = "https://product.kyobobook.co.kr/bestseller/online"
        driver.get(url)
        time.sleep(settings.CRAWL_DELAY_SECONDS + 2)
        
        # 스크롤하여 이미지 로드 유도
        _scroll_to_bottom(driver)

        wait = WebDriverWait(driver, 20)
        try:
            items = wait.until(
                EC.presence_of_all_elements_located(
                    (By.CSS_SELECTOR, "li.prod_item")
                )
            )
        except TimeoutException:
            logger.warning("[kyobo] 상품 목록을 찾지 못했습니다.")
            return books

        for rank, item in enumerate(items[:20], start=1):
            try:
                # 새 사이트 구조에 맞춘 셀렉터
                title_el = item.find_element(By.CSS_SELECTOR, ".prod_name, a.prod_info")
                author_el = item.find_element(By.CSS_SELECTOR, ".prod_author")
                title = title_el.text.strip()
                author = author_el.text.strip().split(" ·")[0] # 저자 정보 분리

                try:
                    genre_el = item.find_element(By.CSS_SELECTOR, ".prod_category")
                    genre = GENRE_MAP.get(genre_el.text.strip(), genre_el.text.strip())
                except NoSuchElementException:
                    genre = "종합"

                try:
                    img_el = item.find_element(By.CSS_SELECTOR, ".prod_thumb_box img")
                    image_url = img_el.get_attribute("src")
                    # data-src 속성이 있는 경우 우선 사용
                    image_url = img_el.get_attribute("data-src") or image_url
                except NoSuchElementException:
                    image_url = None

                books.append({
                    "title": title,
                    "author": author,
                    "genre": genre,
                    "cover_color": STORE_COLORS["kyobo"],
                    "image_url": image_url,
                    "rank": rank,
                    "store": "kyobo",
                    "category": "종합 베스트셀러",
                })
            except Exception as e:
                logger.debug(f"[kyobo] item 파싱 실패: {e}")
                continue
    except Exception as e:
        logger.error(f"[kyobo] 크롤링 오류: {e}")
    finally:
        driver.quit()
    return books


# ── 알라딘 ───────────────────────────────────────────────────────────────────

def _crawl_aladdin_sync() -> list[dict]:
    """알라딘 베스트셀러 크롤링 (동기)."""
    driver = _build_chrome_driver()
    books: list[dict] = []
    try:
        url = "https://www.aladin.co.kr/shop/common/wbest.aspx?BestType=Bestseller&BranchType=1&CID=0&cnt=20&SortOrder=1"
        driver.get(url)
        time.sleep(settings.CRAWL_DELAY_SECONDS + 1)
        
        _scroll_to_bottom(driver)

        wait = WebDriverWait(driver, 20)
        try:
            items = wait.until(
                EC.presence_of_all_elements_located(
                    (By.CSS_SELECTOR, "div.ss_book_box")
                )
            )
        except TimeoutException:
            logger.warning("[aladdin] 상품 목록을 찾지 못했습니다.")
            return books

        for rank, item in enumerate(items[:20], start=1):
            try:
                # 정교한 셀렉터로 업데이트
                title_el = item.find_element(By.CSS_SELECTOR, "a.bo3")
                # 저자 링크가 여러개일 수 있으므로 AuthorSearch 포함된 링크 활용
                author_els = item.find_elements(By.CSS_SELECTOR, "a[href*='AuthorSearch']")
                title = title_el.text.strip()
                author = author_els[0].text.strip() if author_els else "저자 미상"

                try:
                    # 첫 번째 li 태그의 텍스트에서 카테고리 추출 시도
                    category_el = item.find_element(By.CSS_SELECTOR, "div.ss_book_list ul li")
                    genre_text = category_el.text.strip()
                    genre = genre_text.split("]")[0].replace("[", "") if "]" in genre_text else "종합"
                    genre = GENRE_MAP.get(genre, genre)
                except NoSuchElementException:
                    genre = "종합"

                try:
                    img_el = item.find_element(By.CSS_SELECTOR, "img.front_cover")
                    image_url = img_el.get_attribute("src")
                except NoSuchElementException:
                    image_url = None

                books.append({
                    "title": title,
                    "author": author,
                    "genre": genre,
                    "cover_color": STORE_COLORS["aladdin"],
                    "image_url": image_url,
                    "rank": rank,
                    "store": "aladdin",
                    "category": "주간 베스트",
                })
            except Exception as e:
                logger.debug(f"[aladdin] item 파싱 실패: {e}")
                continue
    except Exception as e:
        logger.error(f"[aladdin] 크롤링 오류: {e}")
    finally:
        driver.quit()
    return books


# ── 밀리의서재 ───────────────────────────────────────────────────────────────

def _crawl_millie_sync() -> list[dict]:
    """밀리의서재 베스트셀러 크롤링 (동기)."""
    driver = _build_chrome_driver()
    books: list[dict] = []
    try:
        url = "https://www.millie.co.kr/v3/today/more/best/bookstore/total"
        driver.get(url)
        # JS 렌더링 및 페이지 구성 대기
        time.sleep(settings.CRAWL_DELAY_SECONDS + 3)
        _scroll_to_bottom(driver)

        wait = WebDriverWait(driver, 25)
        try:
            # v3 그리드 리스트 아이템
            items = wait.until(
                EC.presence_of_all_elements_located(
                    (By.CSS_SELECTOR, "div.book-list li")
                )
            )
        except TimeoutException:
            logger.warning("[millie] 상품 목록을 찾지 못했습니다.")
            return books

        for rank, item in enumerate(items[:20], start=1):
            try:
                # Millie v3 메타데이터 추출 (Title: 뒤에서 2번째 p, Author: 마지막 p)
                meta_els = item.find_elements(By.CSS_SELECTOR, "a.book-data p")
                if len(meta_els) < 2: continue
                
                title = meta_els[-2].text.strip()
                author = meta_els[-1].text.strip()

                try:
                    img_el = item.find_element(By.CSS_SELECTOR, "a.book-cover-link img")
                    image_url = img_el.get_attribute("src")
                except NoSuchElementException:
                    image_url = None

                books.append({
                    "title": title,
                    "author": author,
                    "genre": "종합",
                    "cover_color": STORE_COLORS["millie"],
                    "image_url": image_url,
                    "rank": rank,
                    "store": "millie",
                    "category": "베스트셀러",
                })
            except Exception as e:
                logger.debug(f"[millie] item 파싱 실패: {e}")
                continue
    except Exception as e:
        logger.error(f"[millie] 크롤링 오류: {e}")
    finally:
        driver.quit()
    return books


# ── DB 저장 헬퍼 ──────────────────────────────────────────────────────────────

async def _upsert_books(db: AsyncSession, raw_books: list[dict], store: str) -> int:
    """크롤링된 도서 데이터를 DB에 upsert하고 저장 건수를 반환."""
    saved = 0
    for raw in raw_books:
        # 기존 도서 조회 (title + author 기준)
        result = await db.execute(
            select(Book).where(
                Book.title == raw["title"],
                Book.author == raw["author"],
            )
        )
        book = result.scalars().first()

        if book is None:
            book = Book(
                title=raw["title"],
                author=raw["author"],
                genre=raw.get("genre"),
                description=raw.get("description"),
                cover_color=raw.get("cover_color", "#5B8FA8"),
                rating=raw.get("rating"),
                image_url=raw.get("image_url"),
                crawled_at=datetime.utcnow(),
            )
            db.add(book)
            await db.flush()
        else:
            book.crawled_at = datetime.utcnow()
            if raw.get("description"):
                book.description = raw["description"]
            if raw.get("rating"):
                book.rating = raw["rating"]

        # 랭킹 저장
        ranking = BookRanking(
            book_id=book.id,
            store=store,
            category=raw.get("category", "베스트셀러"),
            rank=raw["rank"],
        )
        db.add(ranking)
        saved += 1

    await db.commit()
    return saved


# ── Public API ────────────────────────────────────────────────────────────────

CRAWLERS = {
    "kyobo":   _crawl_kyobo_sync,
    "millie":  _crawl_millie_sync,
    "aladdin": _crawl_aladdin_sync,
}


async def run_crawl(store: str, db: AsyncSession) -> CrawlLog:
    """
    지정된 서점 크롤링 실행.
    Selenium은 동기 코드이므로 asyncio.to_thread로 별도 스레드에서 실행.
    """
    from app.models.book import CrawlLog as CrawlLogModel

    log = CrawlLogModel(store=store, status="running", started_at=datetime.utcnow())
    db.add(log)
    await db.commit()
    await db.refresh(log)

    try:
        crawler_fn = CRAWLERS.get(store)
        if crawler_fn is None:
            raise ValueError(f"알 수 없는 서점: {store}")

        logger.info(f"[{store}] 크롤링 시작")
        raw_books: list[dict] = await asyncio.to_thread(crawler_fn)
        logger.info(f"[{store}] {len(raw_books)}건 수집 완료")

        count = await _upsert_books(db, raw_books, store)

        log.status = "done"
        log.books_found = count
        log.finished_at = datetime.utcnow()
    except Exception as e:
        logger.error(f"[{store}] 크롤링 실패: {e}")
        log.status = "error"
        log.error_message = str(e)
        log.finished_at = datetime.utcnow()

    await db.commit()
    await db.refresh(log)
    return log
