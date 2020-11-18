from rest_framework import serializers
from .models import Collections, Movies, Genres

class GenreSerializer(serializers.ModelSerializer):
    class Meta:
        model = Genres
        fields = ['name']
    def to_representation(self, obj):
        return obj.name

class MoviesSerializer(serializers.ModelSerializer):
    genres = GenreSerializer(many=True, read_only=True)
    # for g in genres:
    #     print(g)
    class Meta:
        model = Movies
        fields = ['title', 'description', 'genres', 'uuid']

class CollectionSerializer(serializers.ModelSerializer):
    movies = MoviesSerializer(many=True, read_only=True)
    class Meta:
        model = Collections
        fields = ['title', 'description', 'movies']

class CollectionsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Collections
        fields = ['title', 'description', 'uuid']