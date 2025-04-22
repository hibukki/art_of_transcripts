import feedparser
import requests_cache
import requests
from bs4 import BeautifulSoup
import re
import traceback


def fetch_transcripts(rss_url: str, cache_name: str = "transcripts_cache", expire: int = 86400):
    # enable a 1‑day cache on all requests.get() calls
    requests_cache.install_cache(cache_name, expire_after=expire)

    feed = feedparser.parse(rss_url)
    transcripts: dict[str, str] = {}

    for entry in feed.entries:
        print(f"Processing {entry.title}")
        try:
            html = (
                entry.content[0].value
                if hasattr(entry, "content")
                else entry.get("description", "")
            )
            soup = BeautifulSoup(html, "html.parser")
            a = soup.find("a", href=True)
            if not a:
                continue

            # follow the tinyurl to get the final google‑doc URL
            resp = requests.get(a["href"])
            doc_url = resp.url

            m = re.search(r"/d/([^/]+)/", doc_url)
            if not m:
                continue

            export_url = f"https://docs.google.com/document/d/{m.group(1)}/export?format=txt"
            text = requests.get(export_url).text

            transcripts[entry.title] = text

        except Exception:
            traceback.print_exc()

    return transcripts


def main():
    rss_url = "https://feeds.simplecast.com/zksImfUP"
    for title, text in fetch_transcripts(rss_url).items():
        print(f"=== {title} ===\n")
        print(text)
        print("\n")


if __name__ == "__main__":
    main()
