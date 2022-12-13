import os
import caldav
from datetime import datetime
from dateutil.parser import parse
from typing import Tuple
from utils.ics_calendar import parse_extra_calendars


def parse_event_card(event_card: str) -> Tuple[str, str]:
    splitted_card = event_card.split("\n")
    summary = [x for x in splitted_card if "SUMMARY" in x]
    if summary:
        text_summary = summary[0].replace("SUMMARY:", "")
    else:
        text_summary = "Sem descrição"

    dtstamp = [x for x in splitted_card if "DTSTAMP" in x]
    if dtstamp:
        text_time = dtstamp[0].replace("DTSTAMP:", "")  # 20221207T123733Z
        text_time = str(parse(text_time).hour)
    else:
        text_time = "Sem horário"

    return text_summary, text_time


def list_events(start_date: datetime, end_date: datetime) -> str:
    client = caldav.DAVClient(
        url=os.getenv("CALENDAR_URL"),
        username=os.getenv("CALENDAR_USERNAME"),
        password=os.getenv("CALENDAR_PASSWORD"),
    )

    principal = client.principal()

    calendar = principal.calendar(name=os.getenv("CALENDAR_NAME"))

    events_fetched = calendar.search(
        start=start_date, end=end_date, event=True, expand=True
    )

    events_text = ""

    for event in events_fetched:
        summary, hour = parse_event_card(event.data)
        events_text = events_text + f" {summary} às {hour} horas,"

    extra_calendars = parse_extra_calendars(start_date, end_date)

    return events_text + extra_calendars


if __name__ == "__main__":
    from dotenv import load_dotenv
    from datetime import datetime, timedelta, timezone

    load_dotenv()
    print(
        list_events(
            datetime(2022, 12, 1, tzinfo=timezone(timedelta(hours=-3))),
            datetime(2022, 12, 14, tzinfo=timezone(timedelta(hours=-3))),
        )
    )
