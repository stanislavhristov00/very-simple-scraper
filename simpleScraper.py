import requests
from bs4 import BeautifulSoup
import csv
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

import time
import random
import logging

BASE_URL = "https://books.toscrape.com/catalogue/page-{}.html"
END_PAGE = 10

RATING_MAP = {
    "One": 1,
    "Two": 2,
    "Three": 3,
    "Four": 4,
    "Five": 5
}

logging.basicConfig(level=logging.INFO)

session = requests.Session()
retries = Retry(
    total=5,
    backoff_factor=0.5,
    status_forcelist=[500, 502, 503, 504]
)

session.mount("https://", HTTPAdapter(max_retries=retries))

def get_soup_books_on_page(response):
    soup = BeautifulSoup(response.text, "html.parser")
    return soup.select("article.product_pod")

def extract_book_data(book):
    title = book.h3.a["title"]
    price = book.select_one(".price_color").text.strip()
    rating_class = book.select_one(".star-rating")["class"]
    
    rating = next(
        (RATING_MAP[r] for r in rating_class if r in RATING_MAP),
        None
    )

    availability = book.select_one(".availability").text.strip()
    relative_url = book.h3.a["href"]
    product_url = "https://books.toscrape.com/catalogue/" + relative_url

    return {
        "title": title,
        "price": price,
        "rating": rating,
        "availability": availability,
        "product_url": product_url
    }

def scrape_books():
    for page in range(1, END_PAGE):
        url = BASE_URL.format(page)
        for book in get_soup_books_on_page(session.get(url=url)):
            time.sleep(random.uniform(0.5, 1.5))
            yield extract_book_data(book)

with open("books3.csv", "w", newline='', encoding='utf-8') as f:
    writer = csv.DictWriter(f, fieldnames=["title", "price", "rating", "availability", "product_url"])
    writer.writeheader()

    for book in scrape_books():
        logging.info(f"Scraping book: {book['title']}")
        writer.writerow(book)

logging.info("Saved to books3.csv")