import requests
import os
import urllib.parse
import json
from fuzzywuzzy import process
import re
from utils.text_utils import strip_links, strip_html
from unidecode import unidecode


def get_news() -> list:
    url = urllib.parse.urljoin(
        os.getenv("NEXTCLOUD_URL"), "index.php/apps/news/api/v1-3/items"
    )
    response = requests.get(
        url,
        auth=(os.getenv("NEXTCLOUD_USERNAME"), os.getenv("NEXTCLOUD_PASSWORD")),
        params={"type": "3", "getRead": "false", "batchSize": "5"},
    )

    response.raise_for_status()
    json_response = response.json()

    return json_response.get("items")


def get_news_summary() -> str:
    news = get_news()
    if not news:
        return "sem notícias"

    if len(news) >= 5:
        news = news[:5]

    news_text = ", ".join(
        [strip_links(strip_html(unidecode(x.get("title")))) for x in notes]
    )

    return news_text


if __name__ == "__main__":
    from dotenv import load_dotenv

    load_dotenv()
    print(get_news())
