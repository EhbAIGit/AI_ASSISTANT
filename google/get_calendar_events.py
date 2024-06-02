import os.path
from datetime import datetime, timedelta
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

# If modifying these SCOPES, delete the file token.json.
SCOPES = ['https://www.googleapis.com/auth/calendar.events']

def main():
    """Shows basic usage of the Google Calendar API.
    Lists the user's events for the next 7 days.
    """
    creds = None
    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first time.
    if os.path.exists('google/tokenCalendar.json'):
        creds = Credentials.from_authorized_user_file('google/tokenCalendar.json', SCOPES)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'google/credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('google/tokenCalendar.json', 'w') as token:
            token.write(creds.to_json())

    service = build('calendar', 'v3', credentials=creds)

    # Call the Calendar API
    now = datetime.utcnow().isoformat() + 'Z'  # 'Z' indicates UTC time
    end = (datetime.utcnow() + timedelta(days=7)).isoformat() + 'Z'
    print('Getting the upcoming events for the next 7 days')
    events_result = service.events().list(calendarId='primary', timeMin=now, timeMax=end,
                                          singleEvents=True,
                                          orderBy='startTime').execute()
    events = events_result.get('items', [])

    if not events:
        print('No upcoming events found.')
    else:
        for event in events:
            start = event['start'].get('dateTime', event['start'].get('date'))
            end = event['end'].get('dateTime', event['end'].get('date'))
            summary = event.get('summary', 'No Title')
            location = event.get('location', 'No Location')
            description = event.get('description', 'No Description')
            print(f"Event: {summary}")
            print(f"Start: {start}")
            print(f"End: {end}")
            print(f"Location: {location}")
            print(f"Description: {description}\n")

if __name__ == '__main__':
    main()
