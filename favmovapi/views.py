from django.shortcuts import render
import requests, json
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.status import HTTP_400_BAD_REQUEST, HTTP_404_NOT_FOUND, HTTP_200_OK
from .models import Collections, Movies, Genres, RequestCount
from .serializer import CollectionSerializer, CollectionsSerializer, GenreSerializer
from collections import Counter

# Create your views here.

class ApiOverview(APIView):
    def get(self, request, *args, **kwargs):
        t = {"message": "Hi VAmsi"}
        return Response(t)

class RegisterApi(APIView):
    """
    Stores User Details in database
    """
    def post(self, request, *args, **kwargs):
        """
        Fetched user filled data from the form.
        required Fields:
            :username: Unique Username
            :password: Password for that user name
            :email: Email of the user.
        """
        data = request.POST
        try:
            if not User.objects.filter(username=data['username']).exists(): #Checking whether any user exists with taht username
                user_obj = User.objects.create_user(data['username'], data['email'], data['password'])
                user_obj.save()
                token, _ = Token.objects.get_or_create(user=user_obj) #generating token and sving in Database

                return Response({'token': token.key}, status=HTTP_200_OK)

            else:
                return Response({'error': 'Username is Taken, Please try with differnt one..'}, status=HTTP_400_BAD_REQUEST)
        except Exception as err:
            print(err)
            return Response({'error': 'Error Occured Try Again Later.'}, status=HTTP_400_BAD_REQUEST)

class GetToken(APIView):
    """
    Returns Token for the user
    """
    def post(self, request, *args, **kwargs):
        """
        Validates the credentials from POST method and returns Token.
        :username: username of the user
        :password: password of the user
        """
        data = request.POST
        username = data['username']
        password = data['password']
        if username is None or password is None:
            return Response({'error': 'Please provide both username and password'}, status=HTTP_400_BAD_REQUEST)
        user = authenticate(username=username, password=password)
        if user is None:
            return Response({'error': 'Invalid Credentials'}, status=HTTP_404_NOT_FOUND)
        token, _ = Token.objects.get_or_create(user=user)

        return Response({'token': token.key}, status=HTTP_200_OK)

class MoviesList(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
    def get(self, request, format=None):
        context = {}
        page_number = request.GET.get('page', False)
        if page_number:
            page = int(page_number)
            if page > 1:
                context['next'] = f'http://localhost:8000/api/movies?page={page + 1}'
                context['previous'] = f'http://localhost:8000/api/movies?page={page - 1}'
            elif page_number == 1:
                context['next'] = f'http://localhost:8000/api/movies?page={page + 1}'
                context['previous'] = f'http://localhost:8000/api/movies'
        else:
            context['next'] = f'http://localhost:8000/api/movies?page=2'

        movies = self.get_movies(request, page_number)
        context['count'] = movies['count']
        context['data'] = movies['movies']
        return Response(context)
    
    def get_movies(self, request, page_number=False):
        """
        Get's movie data from Third Party API
        :page_number: Page number that needs to be requested from API.
        """
        if page_number:
            url = f"https://demo.credy.in/api/v1/maya/movies/?page={page_number}"
        else:
            url = "https://demo.credy.in/api/v1/maya/movies/"
        
        payload = {}
        headers = {
            'Authorization': 'Basic aU5kM2pETVlSS3NOMXBqUVBNUnoybnJxN045OXE0VHNwOUVZOWNNMDpOZTVEb1RRdDdwOHFyZ2tQZHRlblRLOHpkNk1vcmNDUjV2WFpJSk5mSnd2ZmFmWmZjT3M0cmV5YXNWWWRkVHlYQ3o5aGNMNUZHR0lWeHczcTAyaWJuQkxoYmxpdnFRVHA0QklDOTNMWkhqNE9wcHVIUVV6d3VnY1l1N1RJQzVIMQ=='
        }

        response = requests.request("GET", url, headers=headers, data = payload)
        data = json.loads(response.text)
        return {'count': data['count'], 'movies': data['results']}

class Collection(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        """
        Gets the collection Data from the database.
        """
        collection_id = self.kwargs.get('collection_id', False) #checking if any collection id is given
        if collection_id: #if provided then fetching all the information related to that collection including list if movies
            try:
                collection = Collections.objects.get(uuid = collection_id)
                serialize = CollectionSerializer(collection, many=False)
                return Response(serialize.data)
            except Collections.DoesNotExist:
                return Response({'Error: ': 'Collection Does Not Exists'})
            except Exception as err:
                return Response({'Error: ': str(err)})
        else: #else fetching all the collections and the favorites genres list
            try:
                context = {}
                token = (request.META.get('HTTP_AUTHORIZATION')).split(' ')[-1]
                collections = Collections.objects.filter(user = Token.objects.get(key=token).user)
                serialize = CollectionsSerializer(collections, many=True)
                context['is_success'] = True
                context['data'] = {
                    'collections': serialize.data
                }
                genres_list = []
                for collection in collections:
                    for movie in collection.movies.all():
                        genres = movie.genres.all()
                        genres_serializer = GenreSerializer(genres, many=True)
                        genres_list = genres_list + genres_serializer.data
                most_3 = [ genre[0] for genre in Counter(genres_list).most_common(3)]
                context['favourite_genres'] = most_3
                return Response(context)
            except Collections.DoesNotExist:
                return Response({'Error: ': 'Collection Does Not Exists'})
            except Exception as err:
                return Response({'Error: ': str(err)})
    
    def post(self, request, *args, **kwargs):
        """
        Saves the Data into collection model
        """
        context = {}
        token = (request.META.get('HTTP_AUTHORIZATION')).split(' ')[-1]
        data = request.data
        collection_obj = Collections()
        collection_obj.title = data['title']
        collection_obj.description = data['description']
        collection_obj.user = Token.objects.get(key=token).user
        collection_obj.save()

        for movie in data['movies']:
            movie_obj, created = self.save_movie(request, movie)
            if created:
                for genre in movie['genres'].split(','):
                    genre_obj, genre_created = self.save_genre(request, genre)
                    movie_obj.genres.add(genre_obj)

            collection_obj.movies.add(movie_obj)

        context['collection_uuid'] = collection_obj.uuid

        return Response(context)

    def put(self, request, *args, **kwargs):
        """
        Updating Collection Object with the provided data.
        """
        collection_id = self.kwargs['collection_id']
        try:
            data = request.data
            collection_obj = Collections.objects.filter(uuid = collection_id)
            collection_obj.update(title = data['title'], description = data['description'])
            collection_obj = Collections.objects.get(uuid = collection_id)
            for movie in data['movies']:
                movie_obj, created = self.save_movie(request, movie)
                if created:
                    for genre in movie['genres'].split(','):
                        genre_obj, genre_created = self.save_genre(request, genre)
                        movie_obj.genres.add(genre_obj)

                collection_obj.movies.add(movie_obj)

        except Collections.DoesNotExist:
            return Response({'Error: ': 'Collection Does Not Exists'})
        except Exception as err:
            return Response({'Error: ': str(err)})
        
        return Response({'Message': 'Updated Collection'})

    def delete(self, request, *args, **kwargs):
        """
        Deleting the Collection
        """
        collection_id = self.kwargs['collection_id']
        try:
            collection_obj = Collections.objects.filter(uuid = collection_id).delete()
        except Collections.DoesNotExist:
            return Response({'Error: ': 'Collection Does Not Exists'})
        except Exception as err:
            return Response({'Error: ': str(err)})
        return Response({'Message': 'Deleted Collection'})

    def save_movie(self, request, movie):
        """
        Saving the Movie Objects into database
        :movie: Dictionary that contains information about movie.
        """
        movie_obj, created = Movies.objects.get_or_create(
                title = movie['title'],
                description = movie['description'],
                uuid = movie['uuid'],
            )
        return (movie_obj, created)
    
    def save_genre(self, request, genre):
        """
        Saving the genre Objects into database
        :movie: Dictionary that contains information about Genre.
        """
        genre_obj, genre_created = Genres.objects.get_or_create(name = genre)

        return (genre_obj, genre_created)

class RequestCountView(APIView):
    """
    Geting Request count
    """
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        context = {}
        context['requests'] = (RequestCount.objects.all().first()).count

        return Response(context)

class RequestCountReset(APIView):
    """
    Resetting Request count
    """
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        RequestCount.objects.all().update(count = 0)
        return Response({'message': 'request count reset successfully'})