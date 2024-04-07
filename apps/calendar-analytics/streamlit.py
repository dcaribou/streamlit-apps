import streamlit as st
from shared.googlelib import (
        authenticate,
        fetch_calendars,
        fetch_calendar_events
    )
import pandas as pd

CREDENTIALS_FILE_PATH = "client_secret_153639038451-8r2mq88ll6utdkb5fe2aacelccpl10mp.apps.googleusercontent.com.json"

@st.cache_data
def load_events(_credentials, calendars: list[str]):
    return fetch_calendar_events(_credentials, calendars)

def as_dataframe(events: list[dict]):
    """Converts a list of dicts representing calendar events to a flattened pandas DataFrame.
    Calendar events are represented as follows:
    ```
    {
        "kind": "calendar#event",
        "etag": "\"2799450179276000\"",
        "id": "ikog8tbg6tavulu62ctavnch4o",
        "status": "confirmed",
        "htmlLink": "https://www.google.com/calendar/event?eid=aWtvZzh0Ymc2dGF2dWx1NjJjdGF2bmNoNG8gZGF2aWRjYXJhbXV4b0Bt",
        "created": "2014-05-10T12:31:29.000Z",
        "updated": "2014-05-10T12:31:29.638Z",
        "summary": "Exam",
        "colorId": "10",
        "creator": {
            "email": "davidcaramuxo@gmail.com",
            "displayName": "David Cariboo",
            "self": true
        },
        "organizer": {
            "email": "davidcaramuxo@gmail.com",
            "displayName": "David Cariboo",
            "self": true
        },
        "start": {
            "dateTime": "2014-06-03T08:00:00+02:00",
            "timeZone": "Europe/Madrid"
        },
        "end": {
            "dateTime": "2014-06-03T12:00:00+02:00",
            "timeZone": "Europe/Madrid"
        },
        "iCalUID": "ikog8tbg6tavulu62ctavnch4o@google.com",
        "sequence": 0,
        "reminders": {
            "useDefault": true
        },
        "eventType": "default"
        }
    ```
    """
    df = pd.DataFrame(events)
    return df

st.title("Calendar Analytics")

creds = authenticate(CREDENTIALS_FILE_PATH)
calendars = fetch_calendars(creds)

all_calendars = map(lambda x: x["summary"], calendars)  
focused_calendars = st.multiselect(
    label="Calendars",
    options=all_calendars,
    default=all_calendars
)

events = load_events(creds, focused_calendars)

events_df = as_dataframe(events)
st.dataframe(events_df)

st.json(calendars)
