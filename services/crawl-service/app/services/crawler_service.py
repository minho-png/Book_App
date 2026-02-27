"""
Crawler Service - Selenium + ChromeDriver (headless) 기반
각 서점(교보문고, 알라딘, 밀리의서재) 베스트셀러 크롤링
"""
import asyncio
import logging
import time
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
        url = "https://www.kyobobook.co.kr/bestSellerNew/bestseller.laf?mallGb=KOR&orderClick=DAa"
        driver.get(url)
        time.sleep(settings.CRAWL_DELAY_SECONDS)

        wait = WebDriverWait(driver, 15)
        try:
            items = wait.until(
                EC.presence_of_all_elements_located(
                    (By.CSS_SELECTOR, "ul.list_type01 li.list_item")
                )
            )
        except TimeoutException:
            logger.warning("[kyobo] 상품 목록을 찾지 못했습니다.")
            return books

        for rank, item in enumerate(items[:20], start=1):
            try:
                title_el = item.find_element(By.CSS_SELECTOR, ".title strong")
                author_el = item.find_element(By.CSS_SELECTOR, ".author")
                title = title_el.text.strip()
                author = author_el.text.strip().split(" 지음")[0]

                try:
                    genre_el = item.find_element(By.CSS_SELECTOR, ".category")
                    genre = GENRE_MAP.get(genre_el.text.strip(), genre_el.text.strip())
                except NoSuchElementException:
                    genre = "종합"

                try:
                    img_el = item.find_element(By.CSS_SELECTOR, "img")
                    image_url = img_el.get_attribute("src")
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
                time.sleep(0.3)
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
        time.sleep(settings.CRAWL_DELAY_SECONDS)

        wait = WebDriverWait(driver, 15)
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
                title_el = item.find_element(By.CSS_SELECTOR, "a.bo3")
                author_el = item.find_element(By.CSS_SELECTOR, "span.ss_f_g2_3")
                title = title_el.text.strip()
                author = author_el.text.strip().split(" |")[0]

                try:
                    rating_el = item.find_element(By.CSS_SELECTOR, "span.CoverStarBasic")
                    rating = float(rating_el.text.strip())
                except (NoSuchElementException, ValueError):
                    rating = None

                try:
                    desc_el = item.find_element(By.CSS_SELECTOR, "div.ss_f_g2_2")
                    description = desc_el.text.strip()
                except NoSuchElementException:
                    description = None

                try:
                    img_el = item.find_element(By.CSS_SELECTOR, "img")
                    image_url = img_el.get_attribute("src")
                except NoSuchElementException:
                    image_url = None

                books.append({
                    "title": title,
                    "author": author,
                    "genre": "종합",
                    "rating": rating,
                    "description": description,
                    "cover_color": STORE_COLORS["aladdin"],
                    "image_url": image_url,
                    "rank": rank,
                    "store": "aladdin",
                    "category": "주간 베스트",
                })
                time.sleep(0.3)
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
        # 사용자 요청 URL로 업데이트
        url = "https://www.millie.co.kr/v3/today/more/best/bookstore/total"
        driver.get(url)
        time.sleep(settings.CRAWL_DELAY_SECONDS + 2)   # JS 렌더링 대기 시간 증가

        wait = WebDriverWait(driver, 20)
        try:
            # v3 리스트 페이지의 아이템 셀렉터 (일반적인 패턴: div.book-list-item or li)
            # Millie v3는 보통 div나 li 내부에 정보를 담음
            items = wait.until(
                EC.presence_of_all_elements_located(
                    (By.CSS_SELECTOR, "li") # 혹은 클래스명이 바뀔 수 있으므로 범용적인 li 시도 후 필터링
                )
            )
        except TimeoutException:
            logger.warning("[millie] 상품 목록을 찾지 못했습니다.")
            return books

    # v3 리스트 페이지 특징에 맞춰 파싱 로직 강화
        found_count = 0
        for item in items:
            if found_count >= 20: break
            try:
                # v3에서는 p.title, p.author 또는 .title, .author 클래스 사용
                # 여러 시퀀스를 시도하여 유연하게 대응
                title = None
                author = None
                
                for selector in [".title", ".book-title", "p.title", "strong"]:
                    try:
                        title_el = item.find_element(By.CSS_SELECTOR, selector)
                        title = title_el.text.strip()
                        if title: break
                    except NoSuchElementException: continue
                
                if not title: continue # 제목 없으면 넘김

                for selector in [".author", ".book-author", "p.author", "span.author"]:
                    try:
                        author_el = item.find_element(By.CSS_SELECTOR, selector)
                        author = author_el.text.strip()
                        if author: break
                    except NoSuchElementException: continue

                try:
                    img_el = item.find_element(By.CSS_SELECTOR, "img")
                    image_url = img_el.get_attribute("src")
                except NoSuchElementException:
                    image_url = None

                books.append({
                    "title": title,
                    "author": author or "저자 미상",
                    "genre": "종합",
                    "cover_color": STORE_COLORS["millie"],
                    "image_url": image_url,
                    "rank": found_count + 1,
                    "store": "millie",
                    "category": "베스트셀러",
                })
                found_count += 1
                time.sleep(0.1)
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
