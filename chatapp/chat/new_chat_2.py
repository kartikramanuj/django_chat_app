# models.py (updated)
from django.db import models
from account.models import CustomUser

class Chat(models.Model):
    sender = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name="chat_sender")
    receiver = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name="chat_receiver")
    message = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.sender.username}-{self.receiver.username}"

class MessageHistory(models.Model):
    chats = models.ManyToManyField(Chat, related_name="message_history_chats")


# serializers.py
from rest_framework import serializers
from .models import Chat, MessageHistory

class ChatSerializer(serializers.ModelSerializer):
    class Meta:
        model = Chat
        fields = '__all__'

class MessageHistorySerializer(serializers.ModelSerializer):
    chats = ChatSerializer(many=True)

    class Meta:
        model = MessageHistory
        fields = '__all__'


# views.py
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .models import Chat, MessageHistory, CustomUser
from .serializers import ChatSerializer, MessageHistorySerializer

class ChatView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, user_id):
        chats = Chat.objects.filter(
            (models.Q(sender=request.user) & models.Q(receiver__id=user_id)) |
            (models.Q(sender__id=user_id) & models.Q(receiver=request.user))
        ).order_by('timestamp')
        serializer = ChatSerializer(chats, many=True)
        return Response(serializer.data)

    def post(self, request, user_id):
        receiver = CustomUser.objects.get(id=user_id)
        message = request.data.get('message')
        chat = Chat.objects.create(sender=request.user, receiver=receiver, message=message)
        return Response(ChatSerializer(chat).data)

class MessageHistoryView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        histories = MessageHistory.objects.all()
        serializer = MessageHistorySerializer(histories, many=True)
        return Response(serializer.data)


# urls.py
from django.urls import path
from .views import ChatView, MessageHistoryView

urlpatterns = [
    path('chat/<int:user_id>/', ChatView.as_view(), name='chat_view'),
    path('chat/history/', MessageHistoryView.as_view(), name='chat_history'),
]


# consumers.py (WebSocket logic explained)
import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from .models import Chat, CustomUser

class ChatConsumer(AsyncWebsocketConsumer):

    async def connect(self):
        # Get sender and receiver from URL route kwargs
        self.sender_id = self.scope['user'].id
        self.receiver_id = self.scope['url_route']['kwargs']['user_id']

        # Unique room name based on sorted user IDs
        self.room_name = f"chat_{min(self.sender_id, self.receiver_id)}_{max(self.sender_id, self.receiver_id)}"
        self.room_group_name = f"chat_{self.room_name}"

        # Add channel to group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        await self.accept()

    async def disconnect(self, close_code):
        # Leave group on disconnect
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        # Parse incoming message
        data = json.loads(text_data)
        message = data['message']

        # Save message to DB
        chat = await self.save_message(self.sender_id, self.receiver_id, message)

        # Broadcast to room
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat_message',
                'message': message,
                'sender_id': self.sender_id
            }
        )

    async def chat_message(self, event):
        # Send message to WebSocket
        await self.send(text_data=json.dumps({
            'message': event['message'],
            'sender_id': event['sender_id']
        }))

    @database_sync_to_async
    def save_message(self, sender_id, receiver_id, message):
        sender = CustomUser.objects.get(id=sender_id)
        receiver = CustomUser.objects.get(id=receiver_id)
        return Chat.objects.create(sender=sender, receiver=receiver, message=message)


# routing.py
from django.urls import re_path
from .consumers import ChatConsumer

websocket_urlpatterns = [
    re_path(r"ws/chat/(?P<user_id>\d+)/$", ChatConsumer.as_asgi()),
]
