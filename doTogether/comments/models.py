from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()


class Comment(models.Model):
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='sent_comments'
    )
    commented_user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='comments'
    )
    description = models.CharField(max_length=512)

    def __str__(self):
        return f"comment - {self.description}"
