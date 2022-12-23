import requests
import os
import urllib.parse
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

    # If n=1, "song" is dict instead of list
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


def get_random_playlist() -> list:
    song_ids = get_random_songs(25)

    results = []
    with ThreadPoolExecutor(8) as pool:
        futures = []
        for song_id in song_ids:
            futures.append(pool.submit(download_song, song_id))

        for future in futures:
            results.append(future.result())

    return results


def get_songs_filtered(search_query: str) -> list:
    url = urllib.parse.urljoin(os.getenv("SUBSONIC_API_URL"), "rest/search2")
    response = requests.get(
        url,
        params={
            "u": os.getenv("SUBSONIC_USER"),
            "p": os.getenv("SUBSONIC_PASSWORD"),
            "query": search_query,
        },
    )

    response.raise_for_status()
    text_response = response.text
    dict_response = parse(text_response)

    songs = (
        dict_response.get("subsonic-response", {})
        .get("searchResult2", {})
        .get("song", [])
    )

    if not songs:
        return []
    elif type(songs) == list:
        return [x.get("@id") for x in songs]
    else:
        return [songs.get("@id")]


def get_filtered_playlist(search_query: str) -> list:
    song_ids = get_songs_filtered(search_query)
    if len(song_ids) >= 25:
        song_ids = song_ids[:25]

    results = []
    with ThreadPoolExecutor(8) as pool:
        futures = []
        for song_id in song_ids:
            futures.append(pool.submit(download_song, song_id))

        for future in futures:
            results.append(future.result())

    return results
