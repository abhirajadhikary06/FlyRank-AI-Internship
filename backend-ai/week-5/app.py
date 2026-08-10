import os
import json
import time
import re
from datetime import datetime, timezone
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup
from flask import Flask, jsonify

app = Flask(__name__)

BASE_URL = "https://books.toscrape.com/"
CATALOGUE_START = urljoin(BASE_URL, "catalogue/page-1.html")
CACHE_DIR = "cache"
OUTPUT_DIR = "output"
REQUEST_DELAY_SECONDS = 0.5
TIMEOUT_SECONDS = 10

HEADERS = {
    "User-Agent": "FlyRankInternship-A9/1.0 (+https://github.com/YOUR-USERNAME/YOUR-REPO)"
}

os.makedirs(CACHE_DIR, exist_ok=True)
os.makedirs(OUTPUT_DIR, exist_ok=True)


def now_utc():
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def cache_path_for(url: str) -> str:
    safe = re.sub(r"[^a-zA-Z0-9]+", "_", url).strip("_")
    return os.path.join(CACHE_DIR, f"{safe}.html")


def fetch_html(url: str, stats: dict, allow_retry=True) -> str:
    path = cache_path_for(url)

    if os.path.exists(path):
        stats["cache_hits"] += 1
        with open(path, "r", encoding="utf-8") as f:
            return f.read()

    for attempt in range(1, 3 if allow_retry else 2):
        try:
            if stats["last_real_request_at"] is not None:
                elapsed = time.time() - stats["last_real_request_at"]
                if elapsed < REQUEST_DELAY_SECONDS:
                    time.sleep(REQUEST_DELAY_SECONDS - elapsed)

            response = requests.get(
                url,
                headers=HEADERS,
                timeout=TIMEOUT_SECONDS,
            )
            stats["last_real_request_at"] = time.time()
            stats["pages_fetched"] += 1

            if response.status_code == 200:
                html = response.text
                with open(path, "w", encoding="utf-8") as f:
                    f.write(html)
                return html

            if response.status_code in (403, 404):
                raise requests.HTTPError(f"HTTP {response.status_code} for {url}")

            if response.status_code >= 500 and attempt == 1:
                time.sleep(1)
                continue

            raise requests.HTTPError(f"HTTP {response.status_code} for {url}")

        except requests.Timeout as e:
            if attempt == 1:
                time.sleep(1)
                continue
            raise e
        except requests.RequestException as e:
            if attempt == 1 and allow_retry:
                time.sleep(1)
                continue
            raise e

    raise RuntimeError(f"Failed to fetch {url}")


def parse_catalogue_page(html: str, page_url: str):
    soup = BeautifulSoup(html, "html.parser")
    links = []

    for article in soup.select("article.product_pod h3 a"):
        href = article.get("href")
        if href:
            links.append(urljoin(page_url, href))

    next_link = soup.select_one("li.next a")
    next_url = urljoin(page_url, next_link["href"]) if next_link and next_link.get("href") else None
    return links, next_url


def rating_text_from_class(tag):
    if not tag:
        return None
    classes = tag.get("class", [])
    rating_words = {"One", "Two", "Three", "Four", "Five"}
    for c in classes:
        if c in rating_words:
            return c
    return None


def clean_price(text: str):
    if not text:
        return None
    m = re.search(r"([0-9]+\.[0-9]+)", text)
    return float(m.group(1)) if m else None


def extract_description(soup: BeautifulSoup):
    desc = soup.select_one("#product_description")
    if not desc:
        return None
    p = desc.find_next_sibling("p")
    return p.get_text(" ", strip=True) if p else None


def validate_record(record: dict):
    required = [
        "title",
        "product_url",
        "price_text",
        "price_gbp",
        "availability_text",
        "rating_text",
        "description",
        "source_page",
        "fetched_at",
    ]

    for key in required:
        if key not in record:
            return False, f"missing field: {key}"

    if not isinstance(record["title"], str) or not record["title"].strip():
        return False, "title must be a non-empty string"
    if not isinstance(record["product_url"], str) or not record["product_url"].startswith("https://"):
        return False, "product_url must be an absolute https URL"
    if not isinstance(record["price_text"], str):
        return False, "price_text must be a string"
    if not isinstance(record["price_gbp"], (int, float)):
        return False, "price_gbp must be numeric"
    if not isinstance(record["availability_text"], str):
        return False, "availability_text must be a string"
    if not isinstance(record["rating_text"], str):
        return False, "rating_text must be a string"
    if record["description"] is not None and not isinstance(record["description"], str):
        return False, "description must be string or null"
    if not isinstance(record["source_page"], str):
        return False, "source_page must be a string"
    if not isinstance(record["fetched_at"], str):
        return False, "fetched_at must be a string"

    return True, None


def scrape():
    start_time = now_utc()
    started = time.time()

    stats = {
        "start_time": start_time,
        "duration_seconds": 0,
        "pages_fetched": 0,
        "cache_hits": 0,
        "valid_records": 0,
        "invalid_records": 0,
        "failed_pages": 0,
        "last_real_request_at": None,
    }

    catalogue_pages = []
    page_url = CATALOGUE_START
    seen_pages = set()

    try:
        html = fetch_html(page_url, stats)
        for _ in range(3):
            catalogue_pages.append(page_url)
            seen_pages.add(page_url)
            _, next_url = parse_catalogue_page(html, page_url)
            if not next_url or next_url in seen_pages:
                break
            page_url = next_url
            html = fetch_html(page_url, stats)
    except Exception:
        stats["failed_pages"] += 1
        raise

    book_urls = []
    for cat_url in catalogue_pages:
        html = fetch_html(cat_url, stats)
        links, _ = parse_catalogue_page(html, cat_url)
        book_urls.extend(links)

    # deliberate fake URL support for Stage 5 testing
    if os.environ.get("ADD_FAKE_URL") == "1":
        book_urls.append("https://books.toscrape.com/catalogue/this-page-does-not-exist/index.html")

    unique_urls = list(dict.fromkeys(book_urls))

    raw_records = []
    seen_products = set()

    for product_url in unique_urls:
        try:
            html = fetch_html(product_url, stats)
            soup = BeautifulSoup(html, "html.parser")

            title = soup.select_one(".product_main h1")
            price = soup.select_one(".product_main .price_color")
            availability = soup.select_one(".product_main .availability")
            rating_tag = soup.select_one(".product_main .star-rating")

            record = {
                "title": title.get_text(strip=True) if title else None,
                "product_url": product_url,
                "price_text": price.get_text(strip=True) if price else None,
                "availability_text": availability.get_text(" ", strip=True) if availability else None,
                "rating_text": rating_text_from_class(rating_tag),
                "description": extract_description(soup),
                "source_page": None,
                "fetched_at": now_utc(),
            }

            # find source page from breadcrumb/cached catalogue not reliable here, so store first catalogue page as required provenance
            record["source_page"] = catalogue_pages[0] if catalogue_pages else CATALOGUE_START

            # normalize
            record["price_gbp"] = clean_price(record["price_text"])

            valid, reason = validate_record(record)
            if valid:
                if record["product_url"] not in seen_products:
                    raw_records.append(record)
                    seen_products.add(record["product_url"])
                    stats["valid_records"] += 1
            else:
                stats["invalid_records"] += 1
                with open(os.path.join(OUTPUT_DIR, "errors.json"), "a", encoding="utf-8") as f:
                    pass

        except Exception as e:
            stats["failed_pages"] += 1
            with open(os.path.join(OUTPUT_DIR, "errors.json"), "a", encoding="utf-8") as f:
                pass
            continue

    errors = []
    good_records = []
    for record in raw_records:
        valid, reason = validate_record(record)
        if valid:
            good_records.append(record)
        else:
            errors.append({"record": record, "reason": reason})

    with open(os.path.join(OUTPUT_DIR, "books.json"), "w", encoding="utf-8") as f:
        json.dump(good_records, f, indent=2, ensure_ascii=False)

    with open(os.path.join(OUTPUT_DIR, "errors.json"), "w", encoding="utf-8") as f:
        json.dump(errors, f, indent=2, ensure_ascii=False)

    stats["duration_seconds"] = round(time.time() - started, 2)
    stats["catalogue_pages"] = len(catalogue_pages)
    stats["discovered"] = len(book_urls)
    stats["unique_urls"] = len(unique_urls)
    stats["detail_pages"] = len(unique_urls)

    with open(os.path.join(OUTPUT_DIR, "run-report.json"), "w", encoding="utf-8") as f:
        json.dump(stats, f, indent=2, ensure_ascii=False)

    return {
        "catalogue_pages": len(catalogue_pages),
        "discovered": len(book_urls),
        "unique_urls": len(unique_urls),
        "detail_pages": len(unique_urls),
        "valid_records": stats["valid_records"],
        "invalid_records": stats["invalid_records"],
        "failed_pages": stats["failed_pages"],
        "cache_hits": stats["cache_hits"],
        "pages_fetched": stats["pages_fetched"],
    }


@app.route("/")
def home():
    return jsonify({
        "message": "Polite scraper is ready. Visit /scrape to run it."
    })


@app.route("/scrape")
def run_scrape():
    result = scrape()
    return jsonify(result)


if __name__ == "__main__":
    app.run(debug=True)
