from django.urls import path
from .views import UsersAPIView, UserEmailAPIView, SearchSpotifyAPIview, SpotifyAPIView, UserSpotifyAPIView

urlpatterns = [
    path('users/', UsersAPIView.as_view(), name='users-list-create'),
    path('users/<str:email>/', UserEmailAPIView.as_view(), name='users-detail-view'),
    path('search/<str:type>/<str:keyword>/', SearchSpotifyAPIview.as_view(), name='search-songs-artists'),
    path('<str:type>/<str:id>/', SpotifyAPIView.as_view(), name='get-songs-artists'),
    path('users/<str:type>/<str:email>/', UserSpotifyAPIView.as_view(), name='user-songs-artists'),
]