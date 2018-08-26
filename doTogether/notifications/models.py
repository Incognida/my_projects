from django.db import models
from django.contrib.auth import get_user_model
User = get_user_model()


class Notification(models.Model):
    NTF_TYPES = (
        ('join', 'join'),
        ('like', 'like')
    )
    STATUSES = (
        ('read', 'read'),
        ('not read', 'not read')
    )
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='notifications'
    )
    ntf_type = models.CharField(choices=NTF_TYPES, max_length=4, default='join')
    status = models.CharField(choices=STATUSES, max_length=8, default='not read')
    created_at = models.DateTimeField(auto_now_add=True)

