from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone


class User(AbstractUser):
    follows = models.ManyToManyField("self", symmetrical=False, blank=True)


class Post(models.Model):
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    created = models.DateTimeField(default=timezone.now)
    content = models.TextField()
    liked = models.ManyToManyField('User', related_name='likes', blank=True)

    def __str__(self):
        return f'{self.content} made by {self.author}, liked:{self.liked.all().count()}'
