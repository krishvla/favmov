from django.contrib import admin
from .models import Genres, Movies, Collections, RequestCount
# Register your models here.

admin.site.register(Genres)
admin.site.register(Movies)
admin.site.register(Collections)
admin.site.register(RequestCount)
