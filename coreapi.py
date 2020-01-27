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
import random

import json

from chatterbot import ChatBot
from chatterbot.trainers import ChatterBotCorpusTrainer

chatbot = ChatBot("ManMetCrack")

# Create a new trainer for the chatbot
trainer = ChatterBotCorpusTrainer(chatbot)

# Train the chatbot based on the english corpus
trainer.train("chatterbot.corpus.english")

SCOPES = ['https://www.googleapis.com/auth/calendar.readonly']

def randomJoke():
    jokes = ["Knock knock. Who's there? Doctor. Doctor Who?",
    "How about a magic trick?",
    "How about some light reading? https://www.linkedin.com/in/karl-southern/"]

    return random.choice(jokes)

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

seen_users = set()
spoken_to = set()

class EchoBot(Client):
    def onMessage(self, author_id, message_object, thread_id, thread_type, **kwargs):
        self.markAsDelivered(thread_id, message_object.uid)
        self.markAsRead(thread_id)

        print("{} from {} in {}".format(message_object, thread_id, thread_type.name))

        if message_object.text:
            if "bot" in message_object.text.lower():
                seen_users.add(author_id)
            if "turn it off" in message_object.text.lower():
                seen_users.remove(author_id)

        if author_id != self.uid:
            output = calendar()
            if len(output) > 0:
                if author_id not in seen_users:
                    joke = randomJoke()
                    if message_object.text and "bot" in message_object.text.lower():
                        joke = ""
                        self.send(fbchat.Message(text="Hi, how are you?"), thread_id=thread_id, thread_type=thread_type)
                    elif message_object.text and "event" in message_object.text.lower():
                        joke = ""
                        self.send(fbchat.Message(text="Sorry! I am busy with event: " + str(output[0]) + "."), thread_id=thread_id, thread_type=thread_type)
                    elif author_id not in spoken_to:
                        joke = ""
                        self.send(fbchat.Message(text="Sorry! I am busy with event: " + str(output[0]) + ". Say \"bot\" to talk to the bot! For any question you might ask..."), thread_id=thread_id, thread_type=thread_type)
                        self.sendLocalImage("onandoff.gif", thread_id=thread_id, thread_type=thread_type)
                        spoken_to.add(author_id)
                    else:
                        joke = ""
                        self.send(fbchat.Message(text="Say \"bot\" to talk to the bot! "), thread_id=thread_id, thread_type=thread_type)

                    if joke == "How about a magic trick?":
                        self.sendLocalImage("yeet.gif", thread_id=thread_id, thread_type=thread_type)
                else:
                    rsp = chatbot.get_response(message_object.text or "I like this!")
                    self.send(fbchat.Message(text=rsp), thread_id=thread_id, thread_type=thread_type)

def start(email=None, password=None):
    try:
        client = EchoBot(email, password)
        client.listen()
    except:
        print("dis cos tan")

start()
