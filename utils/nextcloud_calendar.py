import os
import caldav
from datetime import datetime, timezone, timedelta
from dateutil.parser import parse
from typing import Tuple
from utils.ics_calendar import parse_extra_calendars
from unidecode import unidecode


def parse_event_card(event_card: str) -> Tuple[str, str]:
    splitted_card = event_card.split("\n")
    summary = [x for x in splitted_card if "SUMMARY" in x]
    if summary:
        text_summary = summary[0].replace("SUMMARY:", "")
    else:
        text_summary = "Sem descrição"

    dtstart = [x for x in splitted_card if "DTSTART" in x]
    if dtstart:
        parsed_dtstart = "".join([x for x in dtstart[0] if x.isdigit()])
        dt = parse(parsed_dtstart)
        if not dt.tzinfo:
            dt = dt.replace(tzinfo=timezone.utc)
    else:
        dt = datetime.now(tz=timedelta(timezone(hours=-3)))

    return text_summary, dt


def list_events(start_date: datetime, end_date: datetime) -> str:
    client = caldav.DAVClient(
        url=os.getenv("CALENDAR_URL"),
        username=os.getenv("NEXTCLOUD_USERNAME"),
        password=os.getenv("NEXTCLOUD_PASSWORD"),
    )

    principal = client.principal()

    calendar = principal.calendar(name=os.getenv("CALENDAR_NAME"))

    events_fetched = calendar.search(
        start=start_date, end=end_date, event=True, expand=True
    )

    event_list = [*parse_extra_calendars(start_date, end_date)]

    for event in events_fetched:
        summary, dt = parse_event_card(event.data)
        event_list.append((summary, dt))

    event_list = sorted(
        event_list,
        key=lambda x: x[1].replace(
            tzinfo=x[1].tzinfo if x[1].tzinfo else timezone(timedelta(hours=-3))
        ),
    )
    events_text = ""
    for event in event_list:
        dt = event[1]

        if dt.hour:
            dt = dt.astimezone(timezone(timedelta(hours=-3)))
            event_str = f" {event[0]} às {str(dt.hour)} horas"
            if dt.minute:
                event_str = event_str + f" e {str(dt.minute)} minutos"
        else:
            event_str = f" {event[0]} o dia inteiro"

        event_str = event_str + ","

        events_text = events_text + event_str

    return events_text


def create_event(event_query: str) -> None:
    # <descrição do evento> no dia <número> as <numero> horas
    event_query = unidecode(event_query).lower()
    day_connector = "no dia"
    hour_connector = "as"

    first_split = event_query.split(day_connector)
    second_split = " ".join(first_split[1].split(hour_connector))

    event_summary = first_split[0].strip()

    day = None
    hour = None
    for n in second_split.split(" "):
        try:
            int_n = int(n.strip())
            if not day:
                day = int_n
            else:
                hour = int_n
        except Exception:
            continue

    if not day or not hour:
        return

    event_date = datetime.now(tz=timezone(timedelta(hours=-3)))
    while True:
        if event_date.day == day:
            break
        event_date = event_date + timedelta(days=1)

    event_date = event_date.replace(hour=hour, minute=0, second=0, microsecond=0)

    client = caldav.DAVClient(
        url=os.getenv("CALENDAR_URL"),
        username=os.getenv("NEXTCLOUD_USERNAME"),
        password=os.getenv("NEXTCLOUD_PASSWORD"),
    )

    principal = client.principal()

    calendar = principal.calendar(name=os.getenv("CALENDAR_NAME"))

    calendar.save_event(
        dtstart=event_date,
        dtend=event_date + timedelta(minutes=30),
        summary=event_summary,
    )
