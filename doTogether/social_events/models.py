from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()


class Event(models.Model):
    owner = models.ForeignKey(
        User, on_delete=models.CASCADE,
        related_name='hosted_events',
    )
    members = models.ManyToManyField(User, related_name='events')
    category = models.ForeignKey(
        'Category', on_delete=models.CASCADE,
        related_name='events'
    )
    description = models.CharField(max_length=256)
    latitude = models.FloatField()
    longitude = models.FloatField()
    max_members = models.IntegerField(default=2)
    starts_at = models.DateTimeField(auto_now_add=True)
    ends_at = models.DateTimeField(blank=True, null=True)

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        self.members.add(self.owner)

    def __str__(self):
        return f"name - {self.owner.username}, title - {self.category}"


class Category(models.Model):
    class Meta:
        verbose_name = 'Category'
        verbose_name_plural = 'Categories'

    title = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.title}"


class Subcategory(models.Model):
    class Meta:
        verbose_name = 'Subcategory'
        verbose_name_plural = 'Subcategories'

    category = models.ForeignKey(
        Category, on_delete=models.SET_NULL,
        null=True, blank=True, related_name='categories'
    )
    title = models.CharField(max_length=100)

    def __str__(self):
        return f"title - {self.title}"
