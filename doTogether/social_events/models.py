from django.db import models
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError

User = get_user_model()


def validate_lt(value):
    if not (-90.0 <= value <= 90.0):
        raise ValidationError("latitude degrees's valid range is [-90, 90] ")


def validate_ln(value):
    if not (-180.0 <= value <= 180.0):
        raise ValidationError("latitude degrees's valid range is [-180, 180] ")


class Event(models.Model):
    owner = models.ForeignKey(
        User, on_delete=models.CASCADE,
        related_name='hosted_events',
    )
    members = models.ManyToManyField(User, related_name='events')
    black_list = models.ManyToManyField(User, related_name='black_events')
    category = models.ForeignKey(
        'Category', on_delete=models.CASCADE,
        related_name='events'
    )
    subcategories = models.ManyToManyField('Subcategory', related_name='events')
    description = models.CharField(max_length=256)
    latitude = models.FloatField(validators=[validate_lt])
    longitude = models.FloatField(validators=[validate_ln])
    max_members = models.IntegerField(default=2)
    starts_at = models.DateTimeField(auto_now_add=True)
    ends_at = models.DateTimeField(blank=True, null=True)
    ended = models.BooleanField(default=False)

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)
        self.members.add(self.owner)

    def can_connect(self, user):
        if self.members.filter(id=user.pk).exists:
            return False
        if self.black_list.filter(id=user.pk).exists:
            return False
        return True

    def connect(self, user):
        if self.can_connect(user):
            Notification.put_notification(self.owner, data={'user': user.pk})

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
        null=True, blank=True, related_name='subcategories'
    )
    title = models.CharField(max_length=100)

    def __str__(self):
        return f"title - {self.title}"
