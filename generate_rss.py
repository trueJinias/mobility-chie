from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup
from feedgen.feed import FeedGenerator
import datetime

TARGET_URL = "https://mobility-chiebukuro.jp/"
OUTPUT_FILE = "mobility.xml"

def fetch_articles():
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()
        page.goto(TARGET_URL)
        page.wait_for_load_state("networkidle")
        html = page.content()
        browser.close()

    soup = BeautifulSoup(html, "html.parser")
    articles = []

    # 記事カードを取得（サイト構造に合わせて調整済み）
    for item in soup.select("a.c-article-card"):
        title = item.select_one(".c-article-card__title").text.strip()
        link = item["href"]
        if not link.startswith("http"):
            link = TARGET_URL.rstrip("/") + "/" + link.lstrip("/")
        date = datetime.datetime.now().isoformat()

        articles.append({
            "title": title,
            "link": link,
            "date": date
        })

    return articles

def generate_rss(articles):
    fg = FeedGenerator()
    fg.title("Mobility Chiebukuro RSS")
    fg.link(href=TARGET_URL)
    fg.description("Auto-generated RSS feed for mobility-chiebukuro.jp")

    for a in articles:
        fe = fg.add_entry()
        fe.title(a["title"])
        fe.link(href=a["link"])
        fe.pubDate(a["date"])

    fg.rss_file(OUTPUT_FILE)

if __name__ == "__main__":
    articles = fetch_articles()
    generate_rss(articles)
    print("RSS生成完了:", OUTPUT_FILE)
