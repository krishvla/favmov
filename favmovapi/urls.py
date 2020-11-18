from django.urls import path
from . import views

urlpatterns = [
    path('', views.ApiOverview.as_view(), name='api-overview'),
    path('register/', views.RegisterApi.as_view(), name='register'),
    path('gettoken/', views.GetToken.as_view(), name='gettoken'),
    path('movies/', views.MoviesList.as_view(), name='movies'),
    path('collection/', views.Collection.as_view(), name='collection'),
    path('collection/<str:collection_id>/', views.Collection.as_view(), name="collection-update"),
    path('request-count/', views.RequestCountView.as_view(), name='request-count'),
    path('request-count/reset/', views.RequestCountReset.as_view(), name='request-count-reset'),
]