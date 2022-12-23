import os
from datetime import datetime
from typing import Tuple, List
import requests
import icalendar
import recurring_ical_events


def list_ics_events(
    ics_url: str, start_date: datetime, end_date: datetime
) -> List[Tuple[str, datetime]]:
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
