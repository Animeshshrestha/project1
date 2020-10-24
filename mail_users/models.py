from django.db import models
from django.contrib.auth.models import User

class CustomUser(User):

    def __str__(self):
        return self.email

class UserEmail(models.Model):

    sender = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, related_name="sender", null=True)
    receiver = models.ManyToManyField(CustomUser, blank=False)
    subject = models.CharField(max_length=255)
    message_text = models.TextField(blank=True)
    created_at= models.DateTimeField(auto_now=False, auto_now_add=True)
    is_read = models.BooleanField(default=False)
    is_archived = models.BooleanField(default=False)

    def __str__(self):
        return self.subject

    def email_subject(self):
        return self.subject

