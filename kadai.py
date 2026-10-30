import csv
import time
from urllib.parse import urljoin, urlparse
import requests
from bs4 import BeautifulSoup

START_URL = "https://musashino-u.ac.jp"
DOMAIN = urlparse(START_URL).netloc
INTERVAL = 1.0

sitemap_dict = {}
visited_urls = set()


def get_page_title_and_links(url):
    try:
        time.sleep(INTERVAL)

        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        }

        response = requests.get(url, headers=headers, timeout=10)

        if (
            response.status_code != 200
            or "text/html" not in response.headers.get("Content-Type", "")
        ):
            return None, []

        response.encoding = response.apparent_encoding
        soup = BeautifulSoup(response.text, "html.parser")

        title = soup.title.string.strip() if soup.title else "No Title"

        links = []
        for a_tag in soup.find_all("a", href=True):
            href = a_tag["href"]
            full_url = urljoin(url, href)
            full_url = urlparse(full_url)._replace(fragment="").geturl()

            if urlparse(full_url).netloc == DOMAIN and full_url not in visited_urls:
                links.append(full_url)

        return title, links

    except Exception as e:
        print(f"Error accessing {url}: {e}")
        return None, []


def crawl_sitemap(start_url):
    queue = [start_url]

    while queue:
        current_url = queue.pop(0)

        if current_url in visited_urls:
            continue

        print(f"Scanning: {current_url}")
        visited_urls.add(current_url)

        title, next_links = get_page_title_and_links(current_url)

        if title is not None:
            sitemap_dict[current_url] = title

            for link in next_links:
                if link not in visited_urls and link not in queue:
                    queue.append(link)


def save_to_csv(data_dict, filename="sitemap.csv"):
    try:
        with open(
            filename, mode="w", encoding="utf-8-sig", newline=""
        ) as file:
            writer = csv.writer(file)
            writer.writerow(["URL", "Title"])
            for url, title in data_dict.items():
                writer.writerow([url, title])
        print(f"\n[Success] CSVファイル '{filename}' を保存しました。")
    except Exception as e:
        print(f"Error saving CSV: {e}")


if __name__ == "__main__":
    print("=== 武蔵野大学サイトマップ抽出開始 ===")
    crawl_sitemap(START_URL)
    print(f"\n巡回完了。検出ページ数: {len(sitemap_dict)}")
    save_to_csv(sitemap_dict, "sitemap.csv")
