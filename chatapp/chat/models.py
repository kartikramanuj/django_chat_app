from django.db import models
from django.conf import settings

# accounts/models.py
from django.contrib.auth.models import AbstractUser
from django.db import models

class CustomUser(AbstractUser):
    phone = models.CharField(max_length=15, unique=True, default="+91 1234567890")

    REQUIRED_FIELDS = ['email', "username"]
    USERNAME_FIELD = 'phone'  # login with phone

    def __str__(self):
        return self.phone

# User = settings.AUTH_USER_MODEL
User = CustomUser


class ChatRoom(models.Model):
    participants = models.ManyToManyField(settings.AUTH_USER_MODEL)

# http://10.215.2.225
class Message(models.Model):
    room = models.ForeignKey(ChatRoom, on_delete=models.CASCADE, related_name='messages')
    sender = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['timestamp']
