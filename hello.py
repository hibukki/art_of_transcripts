import feedparser
import requests_cache
import requests
from bs4 import BeautifulSoup, Tag
import re
import traceback


def fetch_transcripts(rss_url: str, cache_name: str = "transcripts_cache", expire: int = 86400):
    # enable a 1‑day cache on all requests.get() calls
    requests_cache.install_cache(cache_name, expire_after=expire)

    feed = feedparser.parse(rss_url)
    for entry in feed.entries:
        print(f"  Processing {entry.title}")
        try:
            html = (
                entry.content[0].value
                if hasattr(entry, "content")
                else entry.get("description", "")
            )
            soup = BeautifulSoup(html, "html.parser")
            a = soup.find("a", href=True)
            href_val = None
            if isinstance(a, Tag):
                href_val = a.attrs.get("href")
            if not isinstance(href_val, str):
                continue

            # follow the tinyurl to get the final google‑doc URL
            resp = requests.get(href_val)
            doc_url = resp.url

            m = re.search(r"/d/([^/]+)/", doc_url)
            if not m:
                continue

            export_url = f"https://docs.google.com/document/d/{m.group(1)}/export?format=txt"
            text = requests.get(export_url).text

            yield entry.title, text

        except Exception:
            traceback.print_exc()


def main():
    rss_url = "https://feeds.simplecast.com/zksImfUP"
    output_file = "transcripts.md"

    print(f"Gradually writing transcripts to {output_file}")

    # write transcripts as markdown, streaming as each is fetched
    with open(output_file, "w", encoding="utf-8") as f:
        for title, text in fetch_transcripts(rss_url):
            header = f"## {title}\n\n"
            f.write(header)
            f.write(text + "\n\n")
            f.flush()

    print(f"Done writing transcripts to {output_file}")
if __name__ == "__main__":
    main()
