import streamlit as st
from shared.googlelib import (
        authenticate,
        fetch_calendars,
        fetch_calendar_events
    )
import pandas as pd
import altair as alt

CREDENTIALS_FILE_PATH = "client_secret_153639038451-8r2mq88ll6utdkb5fe2aacelccpl10mp.apps.googleusercontent.com.json"

@st.cache_data
def load_events(_credentials, calendars: list[str]):
    return fetch_calendar_events(_credentials, calendars)

@st.cache_data
def load_calendars(_credentials):
    return fetch_calendars(_credentials)

st.title("Calendar Analytics")

creds = authenticate(CREDENTIALS_FILE_PATH)

calendars = load_calendars(creds)

calendar_selection = {}
with st.sidebar:
    st.header("Calendars")
    for calendar in calendars:
        calendar_name = calendar["summary"]
        calendar_selection[calendar_name] = st.checkbox(
            label=calendar_name,
            value=True
        )

focused_calendars = [calendar for calendar, selected in calendar_selection.items() if selected]
events = load_events(creds, focused_calendars)

events_df = pd.json_normalize(events)

with st.sidebar:
    st.header("Filters")
    timeoffset = st.slider(
        label="Time offset in days",
        min_value=0,
        max_value=120,
        value=30
    )
    exclude_events = st.multiselect(
        label="Exclude events",
        options=events_df["summary"].unique(),
    )

# curate events_df

events_df["start.dateTime"] = pd.to_datetime(events_df["start.dateTime"], utc=True).dt.tz_convert("Europe/Madrid")
events_df["end.dateTime"] = pd.to_datetime(events_df["end.dateTime"], utc=True).dt.tz_convert("Europe/Madrid")
events_df["duration"] = pd.to_timedelta(events_df["end.dateTime"] - events_df["start.dateTime"])
events_df["duration_in_minutes"] = events_df["duration"].dt.total_seconds() / 60
events_df = events_df[
    (events_df["start.dateTime"] > pd.Timestamp.now(tz="Europe/Madrid") - pd.Timedelta(days=timeoffset)) &
    (events_df["start.dateTime"] < pd.Timestamp.now(tz="Europe/Madrid"))
]
events_df = events_df[~events_df["summary"].isin(exclude_events)]

# create visualizations

st.altair_chart(
    altair_chart=alt.Chart(events_df).mark_arc().encode(
        color="summary",
        theta="sum(duration_in_minutes)",
        tooltip=["summary", "sum(duration_in_minutes)"]
    ),
    use_container_width=True
)

with st.expander("Show raw data"):
    st.dataframe(events_df)
