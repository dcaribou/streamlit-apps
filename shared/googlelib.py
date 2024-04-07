from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

import os

# If modifying these scopes, delete the file token.json.
SCOPES = ["https://www.googleapis.com/auth/calendar.readonly"]

def authenticate(credentials_file_path: str) -> Credentials:
    """Authenticate the user using OAuth 2.0.

    :param credentials_file_path: Path to the credentials file.
    :type credentials_file_path: str
    :return: A valid credentials object.
    :rtype: Credentials
    """
    creds = None
    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists("token.json"):
        creds = Credentials.from_authorized_user_file("token.json", SCOPES)
        return creds
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                credentials_file_path, SCOPES
            )
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open("token.json", "w") as token:
            token.write(creds.to_json())
        return creds

def fetch_calendar_events(credentials: Credentials):
    """Fetch calendar events from Google Calendar API and return them as a list.

    :param credentials: _description_
    :type credentials: Credentials
    :return: _description_
    :rtype: _type_
    """

    # Build the Google Calendar API client
    service = build('calendar', 'v3', credentials=credentials)

    # Call the API to fetch the calendar events
    events_result = service.events().list(calendarId='primary', maxResults=10).execute()
    events = events_result.get('items', [])

    return events
