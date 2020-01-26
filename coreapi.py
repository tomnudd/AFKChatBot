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

import json

import dialogflow
from google.api_core.exceptions import InvalidArgument

from google.oauth2 import service_account
dialogflow_key = json.load(open('dump-egdwhn-1f8a18afdc13.json'))
credentials = (service_account.Credentials.from_service_account_info(dialogflow_key))
session_client = dialogflow.SessionsClient(credentials=credentials)

DIALOGFLOW_PROJECT_ID = 'jimmys4life-egdwhn'
SESSION_ID = '8921672436578789054'
session = session_client.session_path(DIALOGFLOW_PROJECT_ID, SESSION_ID)

text_to_be_analyzed = "how is you?"
text_input = dialogflow.types.TextInput(text=text_to_be_analyzed, language_code="en-GB")
query_input = dialogflow.types.QueryInput(text=text_input)

try:
    response = session_client.detect_intent(session=session, query_input=query_input)
except InvalidArgument:
    print("ok")
print("Query text:", response.query_result.query_text)
print("Detected intent:", response.query_result.intent.display_name)
print("Detected intent confidence:", response.query_result.intent_detection_confidence)
print("Fulfillment text:", response.query_result.fulfillment_text)

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

def start(email=None, password=None):
    try:
        client = EchoBot(email, password)
        client.listen()
    except:
        print("dis cos tan")

start()
