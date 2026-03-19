from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from django.shortcuts import get_object_or_404
from .models import chat, MessageHistory
from account.models import CustomUser
from .serializers import ChatSerializer, MessageHistorySerializer

# Chat API (Send a message or view all chats with a user)
class ChatView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        sender = request.user
        receiver_id = request.data.get("receiver_id")
        message = request.data.get("message")

        if not receiver_id or not message:
            return Response({"error": "Missing fields"}, status=status.HTTP_400_BAD_REQUEST)

        receiver = get_object_or_404(CustomUser, id=receiver_id)

        new_chat = chat.objects.create(sender=sender, receiver=receiver, message=message)

        return Response(ChatSerializer(new_chat).data, status=status.HTTP_201_CREATED)

    def get(self, request):
        user = request.user
        chats = chat.objects.filter(sender=user) | chat.objects.filter(receiver=user)
        chats = chats.order_by("timestamp")
        return Response(ChatSerializer(chats, many=True).data)


# Message History API
class MessageHistoryView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, user_id):
        current_user = request.user
        other_user = get_object_or_404(CustomUser, id=user_id)
        chats = chat.objects.filter(
            (Q(sender=current_user) & Q(receiver=other_user)) |
            (Q(sender=other_user) & Q(receiver=current_user))
        ).order_by("timestamp")
        return Response(ChatSerializer(chats, many=True).data)


# consumers.py (WebSocket consumer for 1-1 chat)
from channels.generic.websocket import AsyncWebsocketConsumer
import json
from django.contrib.auth import get_user_model
from channels.db import database_sync_to_async
from .models import chat

User = get_user_model()

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.user = self.scope["user"]
        self.other_user_id = self.scope["url_route"]["kwargs"]["user_id"]
        self.room_name = f"chat_{min(self.user.id, int(self.other_user_id))}_{max(self.user.id, int(self.other_user_id))}"
        self.room_group_name = f"chat_{self.room_name}"

        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        data = json.loads(text_data)
        message = data["message"]
        sender = self.user
        receiver = await self.get_user(int(self.other_user_id))

        chat_obj = await self.create_chat(sender, receiver, message)

        await self.channel_layer.group_send(
            self.room_group_name,
            {
                "type": "chat_message",
                "message": message,
                "sender": sender.username
            }
        )

    async def chat_message(self, event):
        await self.send(text_data=json.dumps({
            "message": event["message"],
            "sender": event["sender"]
        }))

    @database_sync_to_async
    def get_user(self, user_id):
        return CustomUser.objects.get(id=user_id)

    @database_sync_to_async
    def create_chat(self, sender, receiver, message):
        return chat.objects.create(sender=sender, receiver=receiver, message=message)


# Optional: Fix model class name
class Chat(models.Model):
    sender = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name="chat_sender")
    receiver = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name="chat_receiver")
    message = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.sender.username}-{self.receiver.username}"


class MessageHistory(models.Model):
    chats = models.ManyToManyField(Chat, related_name="message_history_chats")
