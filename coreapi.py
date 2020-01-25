## contains code from the Google examples on
import datetime
from datetime import timezone
import dateutil.parser
import pickle
import os.path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
import fbchat
from fbchat import Client

SCOPES = ['https://www.googleapis.com/auth/calendar.readonly']

def calendar():
    creds = None
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)

    service = build('calendar', 'v3', credentials=creds)

    # Call the Calendar API
    now = datetime.datetime.utcnow().isoformat() + 'Z' # 'Z' indicates UTC time
    print('Getting the upcoming 10 events')
    events_result = service.events().list(calendarId='primary', timeMin=now, maxResults=10, singleEvents=True, orderBy='startTime').execute()
    events = events_result.get('items', [])

    current = datetime.datetime.now(datetime.timezone.utc)

    event_list = []

    if events and len(events) > 0:
        for event in events:
            start = dateutil.parser.parse(event['start'].get('dateTime', event['start'].get('date')))
            end = dateutil.parser.parse(event['end'].get('dateTime', event['end'].get('date')))

            if current > start and current < end:
                event_list.append(event["summary"])

    return event_list

class EchoBot(Client):
    def onMessage(self, author_id, message_object, thread_id, thread_type, **kwargs):
        self.markAsDelivered(thread_id, message_object.uid)
        self.markAsRead(thread_id)

        print("{} from {} in {}".format(message_object, thread_id, thread_type.name))

        if author_id != self.uid:
            if len(calendar()) > 0:
                self.send(fbchat.Message(text="Please stop talking to me"), thread_id=thread_id, thread_type=thread_type)

client = EchoBot("NIL", "NIL")
client.listen()

if __name__ == '__main__':
    calendar()
