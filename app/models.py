from django.db import models

# Create your models here.
from django.db import models
from django.contrib.auth.models import User

class Profile(models.Model):
    user = models.OneToOneField(User,on_delete=models.CASCADE)
    image = models.ImageField(
        upload_to='profile_photos/',
        default='default.png'
    )

    def __str__(self):
        return self.user.username




class ChatHistory(models.Model):
    user = models.ForeignKey(User,on_delete=models.CASCADE)

    question = models.TextField()

    answer = models.TextField()

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

from django.contrib.auth.models import User
from django.db import models



from django.db import models
from django.contrib.auth.models import User


class UploadedDocument(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE
    )

    file = models.FileField(
        upload_to="documents/"
    )

    uploaded_at = models.DateTimeField(
        auto_now_add=True
    )


class ChatSession(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE
    )

    document = models.ForeignKey(
        UploadedDocument,
        on_delete=models.CASCADE,
        related_name="chats"
    )

    title = models.CharField(
        max_length=255,
        default="New Chat"
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )


class ChatMessage(models.Model):
    session = models.ForeignKey(
        ChatSession,
        on_delete=models.CASCADE
    )

    role = models.CharField(
        max_length=20
    )

    message = models.TextField()

    created_at = models.DateTimeField(
        auto_now_add=True
    )