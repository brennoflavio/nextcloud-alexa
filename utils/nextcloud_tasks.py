import os
import caldav
from datetime import datetime, timedelta, timezone
from dateutil.parser import parse
from typing import Tuple
from uuid import uuid4
from fuzzywuzzy import process
import requests


def finish_ics(ics: str) -> str:
    splitted_ics = ics.split("\n")
    dt = datetime.now(tz=timezone(timedelta(hours=-3))).strftime("%Y%m%dT%H%M%S")

    cleaned_ics = []
    for row in splitted_ics:
        if (
            "DTSTAMP:" in row
            or "LAST-MODIFIED:" in row
            or "STATUS:" in row
            or "PERCENT-COMPLETE:" in row
            or "COMPLETED:" in row
        ):
            continue
        cleaned_ics.append(row)

    final_ics = []
    for row in cleaned_ics:
        final_ics.append(row)
        if "BEGIN:VTODO" in row:
            final_ics.append(f"DTSTAMP:{dt}")
            final_ics.append(f"LAST-MODIFIED:{dt}")
            final_ics.append(f"STATUS:COMPLETED")
            final_ics.append(f"PERCENT-COMPLETE:100")
            final_ics.append(f"COMPLETED:{dt}")
    return ("\n".join(final_ics)).strip()


def create_ical_card(summary) -> str:
    dt = datetime.now(tz=timezone(timedelta(hours=-3))).strftime("%Y%m%dT%H%M%S")
    ical_base = f"""
BEGIN:VCALENDAR
VERSION:2.0
PRODID:-//Nextcloud Alexa
BEGIN:VTODO
UID:{str(uuid4())}
CREATED:{dt}
LAST-MODIFIED:{dt}
DTSTAMP:{dt}
SUMMARY:{summary}
END:VTODO
END:VCALENDAR
    """
    return ical_base.strip()


def parse_task_card(task_card: str) -> Tuple[str, str]:
    splitted_card = task_card.split("\n")

    status = [x for x in splitted_card if "STATUS" in x]
    if status:
        status = status[0].replace("STATUS:", "")

    if status == "COMPLETED":
        return None, None

    summary = [x for x in splitted_card if "SUMMARY" in x]
    if summary:
        text_summary = summary[0].replace("SUMMARY:", "")
    else:
        text_summary = "Sem descrição"

    last_modified = [x for x in splitted_card if "LAST-MODIFIED" in x]
    if last_modified:
        last_modified = last_modified[0].replace(
            "LAST-MODIFIED:", ""
        )  # 20221202T005048Z
        last_modified = parse(last_modified)

    return text_summary, last_modified


def list_tasks() -> str:
    client = caldav.DAVClient(
        url=os.getenv("TASK_URL"),
        username=os.getenv("NEXTCLOUD_USERNAME"),
        password=os.getenv("NEXTCLOUD_PASSWORD"),
    )

    principal = client.principal()
    calendar = principal.calendar(name=os.getenv("TASK_LIST_NAME"))
    events_fetched = calendar.search()

    event_list = []
    for event in events_fetched:
        summary, hour = parse_task_card(event.data)
        if hour:
            event_list.append((summary, hour, event.data, event))

    return sorted(event_list, key=lambda x: x[1].replace(tzinfo=None), reverse=True)


def get_task_summary() -> str:
    tasks = list_tasks()
    if not tasks:
        return "sem tarefas"

    if len(tasks) >= 5:
        tasks = tasks[:5]

    tasks_text = ", ".join([x[0] for x in tasks])

    return tasks_text


def create_task(summary: str):
    client = caldav.DAVClient(
        url=os.getenv("TASK_URL"),
        username=os.getenv("NEXTCLOUD_USERNAME"),
        password=os.getenv("NEXTCLOUD_PASSWORD"),
    )

    principal = client.principal()
    calendar = principal.calendar(name=os.getenv("TASK_LIST_NAME"))

    ical = create_ical_card(summary)
    calendar.add_event(ical)


def finish_task(task_name: str):
    tasks = list_tasks()
    if not tasks:
        return

    choices = [x[0] for x in tasks]
    extract = process.extractOne(task_name, choices)

    if extract:
        summary = extract[0]
        task = [x for x in tasks if x[0] == summary]
        ics = task[0][2]
        ics = finish_ics(ics)
        url = task[0][3].url

        response = requests.put(
            url,
            data=ics,
            auth=(os.getenv("NEXTCLOUD_USERNAME"), os.getenv("NEXTCLOUD_PASSWORD")),
        )
        response.raise_for_status()


if __name__ == "__main__":
    from dotenv import load_dotenv
    from datetime import datetime, timedelta, timezone

    load_dotenv()
    # print(get_task_summary())
    # finish_task("arrumar fechadura")
