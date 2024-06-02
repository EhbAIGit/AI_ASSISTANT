'''
This script will now list the files in the specified folder, provide links to view 
and print the content of any .txt files in the folder.

Set folder id to the correct folder id,  you can easily see the id by clicking on the folder in google drive
and look in the url.

'''


import os.path
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload
import io

# If modifying these SCOPES, delete the file token.json.
SCOPES = ['https://www.googleapis.com/auth/drive.readonly']

# Specify the folder ID
folder_id = '1AqIIQ1vlkS0NellZI4DkkUmnV-pGBIG3'

def main():
    """Shows basic usage of the Google Drive API.
    Lists the user's files in a specific folder along with view, download, and edit links.
    If a file is a .txt file, it also reads and prints the content.
    """
    creds = None
    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first time.
    if os.path.exists('google/tokenDocs.json'):
        creds = Credentials.from_authorized_user_file('google/tokenDocs.json', SCOPES)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'google/credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('google/tokenDocs.json', 'w') as token:
            token.write(creds.to_json())

    drive_service = build('drive', 'v3', credentials=creds)

    # Call the Drive v3 API
    query = f"'{folder_id}' in parents"
    results = drive_service.files().list(q=query, fields="nextPageToken, files(id, name, mimeType, webViewLink, webContentLink)").execute()
    items = results.get('files', [])

    if not items:
        print('No files found.')
    else:
        print('Files:')
        for item in items:
            name = item.get('name')
            file_id = item.get('id')
            mime_type = item.get('mimeType')
            web_view_link = item.get('webViewLink')
            web_content_link = item.get('webContentLink', f"https://drive.google.com/uc?id={file_id}&export=download")
            edit_link = f"https://docs.google.com/document/d/{file_id}/edit"

            print(f"Name: {name}")
            print(f"ID: {file_id}")
            print(f"MIME Type: {mime_type}")
            print(f"View Link: {web_view_link}")


            # If the file is a text file, download and print its content
            if mime_type == 'text/plain':
                request = drive_service.files().get_media(fileId=file_id)
                fh = io.BytesIO()
                downloader = MediaIoBaseDownload(fh, request)
                done = False
                while not done:
                    status, done = downloader.next_chunk()
                    print(f"Download {int(status.progress() * 100)}%.")

                fh.seek(0)
                content = fh.read().decode('utf-8')
                if (content) :
                    print(f"Content of {name}:\n{content}\n")
                else :
                    print("empty file. \n")


                print ("****************************************")

if __name__ == '__main__':
    main()
