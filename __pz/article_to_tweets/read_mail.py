from __future__ import print_function

from datetime import datetime, timezone
import os.path
import base64
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# If modifying these scopes, delete the file token.json.
SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']

# run main and manually go through oauth flow 
# now you can read emails with token.json file that was created 

def main():
    """Shows basic usage of the Gmail API.
    Lists the user's Gmail labels.
    """
    creds = None
    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                './credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token.json', 'w') as token:
            token.write(creds.to_json())

    try:
        # Call the Gmail API
        service = build('gmail', 'v1', credentials=creds)
        results = service.users().labels().list(userId='me').execute()
        labels = results.get('labels', [])

        if not labels:
            print('No labels found.')
            return
        print('Labels:')
        for label in labels:
            print(label['name'])

    except HttpError as error:
        # TODO(developer) - Handle errors from gmail API.
        print(f'An error occurred: {error}')


import os.path
import base64
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials

# If modifying these SCOPES, delete the file token.json.
SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']



def parse_parts(parts):
    """
    Utility function that parses the content of an email partition
    """
    data_text = ''
    if parts['mimeType'] == "text/plain":
        # if the email part is text plain
        if 'data' in parts['body']:
            text = parts['body']["data"]
            text = base64.urlsafe_b64decode(text).decode()
            data_text += text
    elif parts['mimeType'] == "text/html":
        # if the email part is an HTML content
        # we can extract the HTML string and save it.
        if 'data' in parts['body']:
            text = parts['body']["data"]
            text = base64.urlsafe_b64decode(text).decode()
            data_text += text
    if 'parts' in parts:
        for part in parts['parts']:
            data_text += parse_parts(part)
    return data_text

def readEmails():
    """Shows basic usage of the Gmail API.
    Lists the user's Gmail labels.
    """
    creds = None
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'my_cred_file.json', SCOPES)
            creds = flow.run_local_server(port=0)
        with open('token.json', 'w') as token:
            token.write(creds.to_json())

    try:
        service = build('gmail', 'v1', credentials=creds)
        results = service.users().messages().list(userId='me', labelIds=['INBOX'], q="is:unread").execute()
        messages = results.get('messages', [])

        if not messages:
            print('No new messages.')
        else:
            for message in messages:
                msg = service.users().messages().get(userId='me', id=message['id']).execute()                
                payload = msg['payload']
                headers = payload['headers']
                
                data = {}
                if 'parts' in payload:
                    text = parse_parts(payload)
                    data['text'] = text
                
                for header in headers:
                    name = header['name']
                    if name.lower() == 'from':
                        data['from'] = header['value']
                    if name.lower() == 'date':
                        data['date'] = header['value']
                    if name.lower() == 'subject':
                        data['subject'] = header['value']
                        
                # Here you can specify the email you're looking for

                if  'zdunekpawel@protonmail.com'.upper() in data['from'].upper():
                    date = data['date']
                    subject = data['subject']
                    txt =data['text'].splitlines()[0]
                    date_object = datetime.strptime(date, '%a, %d %b %Y %H:%M:%S %z')
                    now = datetime.now(timezone.utc)
                    is_today = (date_object.day == now.day and date_object.month == now.month and date_object.year == now.year)

                    return date,subject,txt,date_object

    except Exception as error:
        print(f'An error occurred: {error}')
        return None,None,None , None 

if __name__ == '__main__':
    #main()
    date,subject,txt,is_today=readEmails()
    print(date,subject,txt,is_today)