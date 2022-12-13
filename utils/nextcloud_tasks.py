import os
import caldav
from datetime import datetime
from dateutil.parser import parse
from typing import Tuple


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
            event_list.append((summary, hour))

    return sorted(event_list, key=lambda x: x[1], reverse=True)


def get_task_summary() -> str:
    tasks = list_tasks()
    if not tasks:
        return "sem tarefas"

    if len(tasks) >= 5:
        tasks = tasks[:5]

    tasks_text = ", ".join([x[0] for x in tasks])

    return tasks_text


if __name__ == "__main__":
    from dotenv import load_dotenv
    from datetime import datetime, timedelta, timezone

    load_dotenv()
    print(get_task_summary())
