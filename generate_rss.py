from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup
from feedgen.feed import FeedGenerator
import datetime

# 複数のカテゴリーページURLを指定
TARGET_URLS = [
    "https://mobility-chiebukuro.jp/category/%e7%b7%8f%e5%8b%95%e5%93%a1%e3%83%81%e3%83%83%e3%83%97%e3%82%b9%ef%bc%88%e5%9b%bd%e5%86%85%e7%b7%a8%ef%bc%89/",
    "https://mobility-chiebukuro.jp/category/%e7%b7%8f%e5%8b%95%e5%93%a1%e3%83%81%e3%83%83%e3%83%97%e3%82%b9%ef%bc%88%e5%9b%bd%e5%a4%96%e7%b7%a8%ef%bc%89/",
    "https://mobility-chiebukuro.jp/category/%e3%83%a2%e3%83%93%e3%83%aa%e3%83%86%e3%82%a3%e3%83%bb%e3%83%9e%e3%83%8d%e3%82%b8%e3%83%a1%e3%83%b3%e3%83%88%e3%81%ab%e9%96%a2%e3%81%99%e3%82%8b%e8%ab%96%e6%96%87/",
    "https://mobility-chiebukuro.jp/category/%e9%81%8e%e7%96%8e%e5%9c%b0%e3%83%bb%e4%ba%a4%e9%80%9a%e7%a9%ba%e7%99%bd%e5%9c%b0%e3%81%ae%e3%83%a2%e3%83%93%e3%83%aa%e3%83%86%e3%82%a3%e3%81%ab%e9%96%a2%e3%81%99%e3%82%8b%e8%ab%96%e6%96%87/",
    "https://mobility-chiebukuro.jp/category/%e4%b8%96%e7%95%8c%e3%83%a2%e3%83%93%e3%83%aa%e3%83%86%e3%82%a3%e3%83%8b%e3%83%a5%e3%83%bc%e3%82%b9/",
    "https://mobility-chiebukuro.jp/category/%e5%9c%b0%e5%9f%9f%e3%81%a7%e3%81%ae%e7%89%a9%e8%aa%9e/",
    "https://mobility-chiebukuro.jp/category/%e4%ba%ba%e7%89%a9%e3%81%ab%e3%81%be%e3%81%a4%e3%82%8f%e3%82%8b%e7%89%a9%e8%aa%9e/"
]

def fetch_articles(url):
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()
        page.goto(url)
        page.wait_for_load_state("networkidle")
        html = page.content()
        browser.close()

    soup = BeautifulSoup(html, "html.parser")
    articles = []

    for item in soup.select("a.brz-a.brz-container-link"):
        title_elem = item.select_one(".brz-text")
        if not title_elem:
            continue
        title = title_elem.text.strip()
        link = item["href"]
        if not link.startswith("http"):
            link = url.rstrip("/") + "/" + link.lstrip("/")
        date = datetime.datetime.now().isoformat()

        articles.append({
            "title": title,
            "link": link,
            "date": date
        })

    return articles

def generate_rss(all_articles):
    fg = FeedGenerator()
    fg.title("Mobility Chiebukuro RSS")
    fg.link(href="https://mobility-chiebukuro.jp/")
    fg.description("Auto-generated RSS feed for mobility-chiebukuro.jp")

    # 重複除去（URLで一意化）
    unique_articles = {a["link"]: a for a in all_articles}.values()

    for a in unique_articles:
        fe = fg.add_entry()
        fe.title(a["title"])
        fe.link(href=a["link"])
        fe.pubDate(a["date"])

    fg.rss_file("mobility.xml")

if __name__ == "__main__":
    all_articles = []
    for url in TARGET_URLS:
        all_articles.extend(fetch_articles(url))
    generate_rss(all_articles)
    print("RSS生成完了: mobility.xml")
