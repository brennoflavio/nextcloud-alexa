import requests
import os
import urllib.parse
import json
from fuzzywuzzy import process
import re
from utils.text_utils import strip_links, strip_html
from unidecode import unidecode
from tempfile import NamedTemporaryFile
from xmltodict import parse
from concurrent.futures import ThreadPoolExecutor
from uuid import uuid4


def get_random_songs(n: int) -> list:
    url = urllib.parse.urljoin(os.getenv("SUBSONIC_API_URL"), "rest/getRandomSongs")
    response = requests.get(
        url,
        params={
            "u": os.getenv("SUBSONIC_USER"),
            "p": os.getenv("SUBSONIC_PASSWORD"),
            "size": f"{n}",
        },
    )

    response.raise_for_status()
    text_response = response.text
    dict_response = parse(text_response)

    song_ids = [
        x.get("@id")
        for x in dict_response.get("subsonic-response", {})
        .get("randomSongs", {})
        .get("song", [])
    ]

    return song_ids


def download_song(song_id: str) -> str:
    url = urllib.parse.urljoin(os.getenv("SUBSONIC_API_URL"), "rest/stream")
    response = requests.get(
        url,
        params={
            "u": os.getenv("SUBSONIC_USER"),
            "p": os.getenv("SUBSONIC_PASSWORD"),
            "id": song_id,
            "format": "mp3",
        },
    )
    response.raise_for_status()

    music_url = f"music/{str(uuid4())}.mp3"
    with open(music_url, "wb+") as f:
        f.write(response.content)
        f.flush()

    url = urllib.parse.urljoin(os.getenv("APP_URL"), music_url)

    return url


def get_random_playlist() -> str:
    song_ids = get_random_songs(5)

    results = []
    with ThreadPoolExecutor(8) as pool:
        futures = []
        for song_id in song_ids:
            futures.append(pool.submit(download_song, song_id))

        for future in futures:
            results.append(future.result())

    response = "<speak>"
    for result in results:
        response = response + f"<audio src='{result}'/>"
    response = response + "</speak>"

    print(response, flush=True)

    return response


if __name__ == "__main__":
    from dotenv import load_dotenv

    load_dotenv()
    # print(get_random_songs())
    # print(get_share())
    # print(download_song("track-78"))
    print(get_random_playlist())
