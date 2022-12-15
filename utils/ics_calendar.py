import os
import caldav
from datetime import datetime, timedelta, timezone
from dateutil.parser import parse
from typing import Tuple
import vobject
import vobject
import csv
import requests
import icalendar
import recurring_ical_events
import urllib.request
from typing import Tuple, List


def list_ics_events(
    ics_url: str, start_date: datetime, end_date: datetime
) -> List[Tuple[str, datetime]]:
    events_text = ""

    ical_string = requests.get(ics_url).text
    calendar = icalendar.Calendar.from_ical(ical_string)
    events = recurring_ical_events.of(calendar).between(start_date, end_date)

    final_events = []
    for event in events:
        start = event["DTSTART"].dt
        summary = event["SUMMARY"]

        final_events.append((str(summary), start))

    return final_events


def parse_extra_calendars(start_date: datetime, end_date: datetime):
    calendars = os.getenv("EXTRA_CALENDARS").split(",")

    final = []
    for calendar in calendars:
        final.extend(list_ics_events(calendar, start_date, end_date))

    return final


if __name__ == "__main__":
    from dotenv import load_dotenv

    load_dotenv()

    print(
        parse_extra_calendars(
            datetime(2022, 12, 15, tzinfo=timezone(timedelta(hours=-3))),
            datetime(2022, 12, 16, tzinfo=timezone(timedelta(hours=-3))),
        )
    )

    # test()
