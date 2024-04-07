import streamlit as st
from shared.googlelib import authenticate, fetch_calendar_events
import pandas as pd


st.title("Calendar Analytics")

CREDENTIALS_FILE_PATH = "client_secret_153639038451-8r2mq88ll6utdkb5fe2aacelccpl10mp.apps.googleusercontent.com.json"

creds = authenticate(CREDENTIALS_FILE_PATH)
events = fetch_calendar_events(creds)

def as_dataframe():
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

events_df = as_dataframe()
st.dataframe(events_df)
st.json(events)
