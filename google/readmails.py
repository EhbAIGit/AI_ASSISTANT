import os.path
import base64
from email import policy
from email.parser import BytesParser
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from datetime import datetime

# If modifying these SCOPES, delete the file token.json.
SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']
LAST_MAIL_FILE = 'google/lastmail.txt'

def get_message_details(service, message_id):
    msg = service.users().messages().get(userId='me', id=message_id, format='raw').execute()
    msg_str = base64.urlsafe_b64decode(msg['raw'].encode('ASCII'))
    mime_msg = BytesParser(policy=policy.default).parsebytes(msg_str)

    subject = mime_msg['subject']
    date_received = mime_msg['date']
    from_address = mime_msg['from']
    to_address = mime_msg['to']

    # Extract the text content of the email
    if mime_msg.is_multipart():
        parts = mime_msg.iter_parts()
        text_content = ''
        for part in parts:
            if part.get_content_type() == 'text/plain':
                text_content += part.get_payload(decode=True).decode(part.get_content_charset(), errors='replace')
    else:
        text_content = mime_msg.get_payload(decode=True).decode(mime_msg.get_content_charset(), errors='replace')

    return {
        'subject': subject,
        'date_received': date_received,
        'from': from_address,
        'to': to_address,
        'text_content': text_content
    }

def get_last_downloaded_date():
    if os.path.exists(LAST_MAIL_FILE):
        with open(LAST_MAIL_FILE, 'r') as file:
            return datetime.strptime(file.read().strip(), '%a, %d %b %Y %H:%M:%S %z')
    return None

def save_last_downloaded_date(date):
    with open(LAST_MAIL_FILE, 'w') as file:
        file.write(date)

def main():
    """Shows basic usage of the Gmail API.
    Lists the user's last 10 emails with details.
    """
    creds = None
    user_email = 'Maarten Dequanter <maarten.dequanter@gmail.com>'  # Replace with your actual email address

    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first time.
    if os.path.exists('google/tokenMails.json'):
        creds = Credentials.from_authorized_user_file('google/tokenMails.json', SCOPES)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('google/tokenMails.json', 'w') as token:
            token.write(creds.to_json())

    service = build('gmail', 'v1', credentials=creds)

    # Read the date of the last downloaded email
    last_downloaded_date = get_last_downloaded_date()
    query = ""
    if last_downloaded_date:
        query = f"after:{last_downloaded_date.strftime('%Y/%m/%d')}"

    # Call the Gmail API with a filter
    results = service.users().messages().list(userId='me', q=query, maxResults=50).execute()
    messages = results.get('messages', [])

    if not messages:
        print('No messages found.')
    else:
        latest_date = None
        counter = 0
        for message in messages:
            details = get_message_details(service, message['id'])
            message_date = datetime.strptime(details['date_received'], '%a, %d %b %Y %H:%M:%S %z')

            if last_downloaded_date is None or message_date > last_downloaded_date:
                
                if details['from'] != user_email:

                    counter = counter + 1

                    if latest_date is None or message_date > latest_date:
                        latest_date = message_date

                    print(f"Subject: {details['subject']}")
                    print(f"Received: {details['date_received']}")
                    print(f"From: {details['from']}")
                    print(f"To: {details['to']}")
                    print(f"Text Content: {details['text_content']}\n\n")

                    print("********************************************************")

        # Save the date of the last message downloaded
        print("\n\n")
        if latest_date:
            save_last_downloaded_date(latest_date.strftime('%a, %d %b %Y %H:%M:%S %z'))
            print ("Last mail:" + latest_date.strftime('%a, %d %b %Y %H:%M:%S %z'))

        print (str(counter) + " new mails received")

if __name__ == '__main__':
    main()
