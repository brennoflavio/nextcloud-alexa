import requests
import os
import urllib.parse
import json


def get_notes() -> dict:
    url = urllib.parse.urljoin(
        os.getenv("NEXTCLOUD_URL"), "index.php/apps/notes/api/v1/notes"
    )
    response = requests.get(
        url, auth=(os.getenv("NEXTCLOUD_USERNAME"), os.getenv("NEXTCLOUD_PASSWORD"))
    )

    response.raise_for_status()
    json_response = response.json()
    json_response = sorted(json_response, key=lambda x: x.get("modified"), reverse=True)

    return json_response


def get_notes_summary() -> str:
    notes = get_notes()
    if not notes:
        return "sem notas"

    if len(notes) >= 5:
        notes = notes[:5]

    notes_text = ", ".join([x.get("title", "") for x in notes])

    return notes_text


if __name__ == "__main__":
    from dotenv import load_dotenv

    load_dotenv()

    get_notes()
