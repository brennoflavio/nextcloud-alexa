import requests
import os
import urllib.parse
import json
from fuzzywuzzy import process
import re


def strip_links(s: str) -> str:
    return re.sub(
        r"http\S+",
        "link",
        s,
        flags=re.MULTILINE,
    )


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

    notes_text = ", ".join([strip_links(x.get("title", "")) for x in notes])

    return notes_text


def get_single_note(name: str) -> str:
    notes = get_notes()

    choices = [x.get("title", "") for x in notes]
    extract = process.extractOne(name, choices)

    if extract:
        title = extract[0]
        note = [x for x in notes if x.get("title", "") == title]

        if note:
            text_note = "".join(
                [
                    x
                    for x in strip_links(note[0].get("content")).replace("\n", " ")
                    if (x.isalnum() or x == " ") and x != "x"
                ]
            ).strip()
            if len(text_note) >= 6000:
                text_note = text_note[:6000]

            while "  " in text_note:
                text_note = text_note.replace("  ", " ")

            return text_note

    return "Nota não encontrada"


if __name__ == "__main__":
    from dotenv import load_dotenv

    load_dotenv()

    # print(get_notes_summary())
    print(get_single_note("nas"))
