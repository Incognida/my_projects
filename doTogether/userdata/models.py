import os
from django.db import models
from django.contrib.auth.models import AbstractUser
from .utils import id_generator


def download_img(instance, filename):
    fname, file_ext = os.path.splitext(filename)
    fname = id_generator() + file_ext
    dirname = instance.username + '_' + str(instance.id)
    return 'avatars/{}/{}'.format(dirname, fname)


class CustomUser(AbstractUser):
    SEX_CHOICES = (
        ('male', 'male'),
        ('female', 'female')
    )
    rating = models.IntegerField(default=0)
    image = models.ImageField(upload_to=download_img, null=True, blank=True)
    sex = models.CharField(max_length=6, choices=SEX_CHOICES, default='male')
    age = models.PositiveIntegerField(null=True, blank=True)

    def get_image(self):
        try:
            image = self.image.url
        except ValueError:
            image = None
        return image
