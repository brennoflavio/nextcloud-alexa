import os
import caldav
from datetime import datetime, timedelta, timezone
from dateutil.parser import parse
from typing import Tuple
import vobject
import vobject
import csv
import requests


def list_ics_events(ics_url: str, start_date: datetime, end_date: datetime) -> str:
    events_text = ""

    content = requests.get(ics_url).text
    for cal in vobject.readComponents(content):
        for component in cal.components():
            if component.name == "VEVENT" and component.dtstamp.valueRepr():
                dtstamp = component.dtstamp.valueRepr()

                if dtstamp >= start_date and dtstamp < end_date:
                    text_time = str(dtstamp.hour)

                    summary = component.summary.valueRepr()
                    if not summary:
                        summary = "Sem Descrição"

                    events_text = events_text + f" {summary} às {text_time} horas,"

    return events_text


def parse_extra_calendars(start_date: datetime, end_date: datetime):
    calendars = os.getenv("EXTRA_CALENDARS").split(",")

    event_text = ""
    for calendar in calendars:
        event_text = event_text + list_ics_events(calendar, start_date, end_date)

    return event_text


if __name__ == "__main__":
    url = ""

    print(
        list_ics_events(
            url,
            datetime(2022, 12, 1, tzinfo=timezone(timedelta(hours=-3))),
            datetime(2022, 12, 14, tzinfo=timezone(timedelta(hours=-3))),
        )
    )

    # test()
