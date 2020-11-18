from django.db import models
import uuid
from django.contrib.auth.models import User

# Create your models here.

class Genres(models.Model):
    name = models.CharField(max_length=100, null=False, unique=True)

    def __str__(self):
        return f'{self.name}'

class Movies(models.Model):
    title = models.CharField(max_length=100, null=False)
    description = models.TextField()
    genres = models.ManyToManyField(Genres)
    uuid = models.UUIDField(primary_key=False)

    def __str__(self):
        params = {
            'title': self.title,
            'description': self.description,
            'genres': self.genres,
            'uuid': self.uuid,
        }
        return '{title} - {description} - {genres} - {uuid}'.format(**params)

class Collections(models.Model):
    uuid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=100, null=False)
    description = models.TextField()
    movies = models.ManyToManyField(Movies)
    user =  models.ForeignKey(User, on_delete=models.SET_NULL, null=True)

class RequestCount(models.Model):
    count = models.IntegerField()
    

