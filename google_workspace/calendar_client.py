from datetime import datetime, timedelta, timezone
from .auth import get_service


class Calendar:
    def __init__(self, calendar_id="primary"):
        self.service = get_service("calendar", "v3")
        self.calendar_id = calendar_id

    def list_events(self, days_ahead=7, max_results=20):
        now = datetime.now(timezone.utc)
        time_max = now + timedelta(days=days_ahead)
        result = (
            self.service.events()
            .list(
                calendarId=self.calendar_id,
                timeMin=now.isoformat(),
                timeMax=time_max.isoformat(),
                maxResults=max_results,
                singleEvents=True,
                orderBy="startTime",
            )
            .execute()
        )
        return result.get("items", [])

    def create_event(self, title, start, end, description=None, location=None, attendees=None):
        """
        start / end: datetime objects or ISO strings like "2026-03-01T10:00:00-05:00"
        attendees: list of email strings
        """
        if isinstance(start, datetime):
            start = start.isoformat()
        if isinstance(end, datetime):
            end = end.isoformat()

        event = {
            "summary": title,
            "start": {"dateTime": start},
            "end": {"dateTime": end},
        }
        if description:
            event["description"] = description
        if location:
            event["location"] = location
        if attendees:
            event["attendees"] = [{"email": e} for e in attendees]

        result = (
            self.service.events()
            .insert(calendarId=self.calendar_id, body=event)
            .execute()
        )
        return result

    def update_event(self, event_id, **kwargs):
        event = self.service.events().get(calendarId=self.calendar_id, eventId=event_id).execute()
        for key, value in kwargs.items():
            event[key] = value
        result = (
            self.service.events()
            .update(calendarId=self.calendar_id, eventId=event_id, body=event)
            .execute()
        )
        return result

    def delete_event(self, event_id):
        self.service.events().delete(calendarId=self.calendar_id, eventId=event_id).execute()

    def list_calendars(self):
        result = self.service.calendarList().list().execute()
        return result.get("items", [])
