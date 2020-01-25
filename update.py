import fbchat

from fbchat import Client

def within_calendar_frame():
    return True

class EchoBot(Client):
    def onMessage(self, author_id, message_object, thread_id, thread_type, **kwargs):
        self.markAsDelivered(thread_id, message_object.uid)
        self.markAsRead(thread_id)

        print("{} from {} in {}".format(message_object, thread_id, thread_type.name))

        if author_id != self.uid:
            if within_calendar_frame():
                self.send(fbchat.Message(text="Please stop talking to me"), thread_id=thread_id, thread_type=thread_type)

client = EchoBot("NIL", "NIL")
client.listen()
