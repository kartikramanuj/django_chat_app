import json

from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async

from .models import ChatRoom, Message, User


def printinside(func):
    def wrapper(*args, **kwargs):
        result = func(*args, **kwargs)
        print(f"Inside {func.__name__}")
        return result
    return wrapper


class ChatConsumer(AsyncWebsocketConsumer):

    @printinside
    async def connect(self):
        self.room_name = self.scope['url_route']['kwargs']['room_id']
        self.room_group_name = f"chat_{self.room_name}"

        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        await self.accept()


    @printinside
    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )


    @printinside
    async def receive(self, text_data):
        data = json.loads(text_data)
        message = data['message']
        sender_id = data['sender_id']

        # Save the message
        await self.save_message(self.room_name, sender_id, message)

        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat_message',
                'message': message,
                'sender_id': sender_id
            }
        )


    @printinside
    async def chat_message(self, event):
        await self.send(text_data=json.dumps({
            'message': event['message'],
            'sender_id': event['sender_id']
        }))


    @database_sync_to_async
    @printinside
    def save_message(self, room_id, sender_id, message):
        room = ChatRoom.objects.get(id=room_id)
        sender = User.objects.get(id=sender_id)
        return Message.objects.create(room=room, sender=sender, content=message)
