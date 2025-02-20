from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import Users, Songs, Artists
from .serializers import UserSerializer, SongObjectSerializer, ArtistObjectSerializer
import os
from dotenv import load_dotenv
import requests
from base64 import b64encode
import time

load_dotenv() # Coge las variables de entorno de .env
spotify_id = os.getenv("SPOTIFY_ID")
spotify_secret = os.getenv("SPOTIFY_SECRET")
token = None
token_expiration = 0

# Genera un nuevo token de acceso a no ser que ya exista uno válido
def get_access_token():
    global token, token_expiration
    if token and time.time() < token_expiration:
        # Si ya hay un token que no ha caducado todavía, se devuelve este
        return token
    
    spotify_url = 'https://accounts.spotify.com/api/token'
    auth_header = b64encode(f"{spotify_id}:{spotify_secret}".encode()).decode()
    headers = {
        'Authorization': f'Basic {auth_header}',
        'Content-Type': 'application/x-www-form-urlencoded',
    }
    data = {'grant_type': 'client_credentials'}
    # Se solicita un nuevo token
    response = requests.post(spotify_url, headers=headers, data=data)
    
    response.raise_for_status
    
    token_data = response.json()
    new_token = token_data.get('access_token')
    expires_in = token_data.get('expires_in', 3600)
    token_expiration = time.time() + expires_in
    
    return new_token


def getSpotifySong(song):
    """
        Serializa la información relevante de una canción de Spotify
    """
    # Para cada item se calcula su duración
    length_seconds = song['duration_ms'] / 1000
    length_minutes = int(length_seconds // 60)
    length_seconds = length_seconds % 60
    if length_seconds < 10:
        length = f'{length_minutes}:0{length_seconds:.0f}'
    else:
        length = f'{length_minutes}:{length_seconds:.0f}'
    # Esta será la información que se devolverá de cada canción
    track = {'title': song['name'],
        'artist': song['artists'][0]['name'],
        'album': song['album']['name'],
        'length': length,
        'url': song['external_urls']['spotify'],
        'id': song['uri'].split(':')[2]
        }
    
    return track

def getSpotifyArtist(artist):
    """
        Serializa la información relevante de un artista de Spotify
    """
    new = {'name': artist['name'],
         'genres': artist['genres'],
         'url': artist['external_urls']['spotify'],
         'id': artist['uri'].split(':')[2]
        }
    
    return new
        

def get_data(type, id):
    """
        Devuelve una cancion o artista dado su id de spotify
    """
    # Según el tipo de dato, canción o artista, se utiliza una url u otra
    if type == 'songs':
        url = f"https://api.spotify.com/v1/tracks/{id}"
    elif type == 'artists':
        url = f"https://api.spotify.com/v1/artists/{id}"
    else:
        # Si el tipo es incorrecto
        return {"error": 'Unexpected error'}
    
    token = get_access_token() # Obtención del token de acceso
    header = {
        'Authorization': f'Bearer {token}'
    }
    # LLamamos a la API de Spotify
    response = requests.get(url, headers=header)
    if response.status_code != 200:
        return {"error": 'Unexpected error'}
    
    result = response.json()
    
    if result:
        if type == 'songs':
            return {'song': getSpotifySong(result)}
        elif type == 'artists':
            return {'artist': getSpotifyArtist(result)}
    else:
        return {"message": "Canción no encontrada"}
    

class UsersAPIView(APIView):
    """
        Se encarga del GET y el POST para los usuarios
        path = api/users/
    """
    def get(self, request):
        """
            Devuelve los datos de los usuarios serializados en formato JSON
        """
        users = Users.objects.all()
        serializer = UserSerializer(users, many=True)
        return Response(serializer.data)


    def post(self, request):
        """
            Añade un nuevo usuario dados sus datos (nombre y email)
        """
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserEmailAPIView(APIView):
    """
        Se encarga del GET, PUT y DELETE para los usuarios
        path = api/users/<str:email>/
    """
    def get(self, request, email):
        """
            Devuelve los datos de un usuario en formato JSON dado su email
        """
        try:
            # El email de un usuario es su clave primaria
            user = Users.objects.get(pk=email)
            return Response(UserSerializer(user).data, status=status.HTTP_302_FOUND)
        except Users.DoesNotExist:
            return Response({"error": f'No existe el usuario {email}'}, status=status.HTTP_404_NOT_FOUND)
    
    def delete(self, request, email):
        """
            Elimina un usuario dado su email
        """
        try:
            user = Users.objects.get(pk=email)
            user.delete()
            return Response({"message": "Usuario eliminado"}, status=status.HTTP_204_NO_CONTENT)
        except Users.DoesNotExist:
            return Response({"error": f'No existe el usuario {email}'}, status=status.HTTP_404_NOT_FOUND)
        
    def put(self, request, email):
        """
            Actualiza la información de un usuario
        """
        try:
            user = Users.objects.get(pk=email)
        except Users.DoesNotExist:
            return Response({"error": f'No existe el usuario {email}'}, status=status.HTTP_404_NOT_FOUND)
        
        serializer = UserSerializer(user, data=request.data, partial = True) 
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status = status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class SearchSpotifyAPIview(APIView):
    """
        Sirve para buscar canciones o usuarios.
        path = api/search/<str:type>/<str:keyword>/
    """
    def get(self, request, type, keyword):
        """
            Busca una canción en base a unas palabras clave
        """
        # Se establecen los parámetros según el tipo de búsqueda
        if type == "songs":
            search = 'track'
        elif type == "artists":
            search = 'artist'
        else:
            return Response({"error": f"Unexpected error {type}"}, status=status.HTTP_400_BAD_REQUEST)

        token = get_access_token()
        search_header = {
            'Authorization': f'Bearer {token}'
        }
        
        search_parameters = {
            'q': keyword,
            'type': search,
            'limit': 5
        }

        # Se llama a la API de Spotify
        url = f"https://api.spotify.com/v1/search"
        response = requests.get(url, headers=search_header, params=search_parameters)
        if response.status_code != 200:
            return Response({"error": f'Unexpected error {search_parameters}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        

        if type == 'songs':
            # Según el tipo de busqueda, se usa una función u otra para coger la información relevante
            track = response.json().get('tracks', {}).get('items', [])
            songs = []
            for item in track:
                songs.append(getSpotifySong(item))
            return Response(songs)
        
        elif type == 'artists':
            results = response.json().get('artists', {}).get('items', [])
            artists = []
            for item in results:
                artists.append(getSpotifyArtist(item))
            return Response(artists)
    

class SpotifyAPIView(APIView):
    """
        Sirve para obtener informacion de una cancion o artista dado su codigo identificador.
        path = api/<str:type>/<str:id>/
    """
    def get(self, request, type, id):
        """
            Devuelve una cancion o artista dado su id de spotify
        """
        return Response(get_data(type, id))
        


class UserSpotifyAPIView(APIView):
    """
        Sirve para añadir canciones o artistas a las favoritas de un usuario, y para listar todas con información sacada de spotify.
        path = api/users/<str:type>/<str:email>/
    """
    def post(self, request, type, email):
        """
            Se añade una cancion o artista dado su id de spotify al listado de favoritos de un usuario
        """
        # Se comprueba que existe el usuario
        try:
            user = Users.objects.get(pk=email)
        except Users.DoesNotExist:
            return Response({"error": f'No existe el usuario {email}'}, status=status.HTTP_404_NOT_FOUND)
        
        if type != 'songs' and type != 'artists':
            Response({"error": f"Unexpected error {type}"}, status=status.HTTP_400_BAD_REQUEST)

        data = request.data
        
        if type == 'songs':
            # Se comprueba si la canción existe en Spotify y si es así se añade a la base de datos
            so = get_data('songs', data['code'])
            if 'song' not in so:
                return Response({'message': f'Canción con id {data['code']} no encontrada'}, status=status.HTTP_404_NOT_FOUND)
            serializer = SongObjectSerializer(data={'email': email, 'code': data['code']})
        else:
            # Se comprueba si el artista existe en Spotify y si es así se añade a la base de datos
            so = get_data('artists', data['code'])
            if 'artist' not in so:
                return Response({'message': f'Artista con id {data['code']} no encontrado'}, status=status.HTTP_404_NOT_FOUND)
            serializer = ArtistObjectSerializer(data={'email': email, 'code': data['code']})

        # Se comprueba que el objeto creado con el serializador es valido
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    

    def get(self, request, type, email):
        """
            Muestra las canciones favoritas de un usuario e información sobre ellas
        """
        # Se comprueba que existe el usuario
        try:
            user = Users.objects.get(pk=email)
        except Users.DoesNotExist:
            return Response({"error": f'No existe el usuario {email}'}, status=status.HTTP_404_NOT_FOUND)
        serializer = UserSerializer(user)

        if type == 'songs':
            song_list = []
            for song in serializer.data['songs']:
                # Se utiliza la función get_song para obtener la información de las canciones
                new_song = get_data('songs', song['code'])
                if 'song' in new_song:
                    song_list.append(new_song['song'])
            return Response({'song list': song_list})
        elif type == 'artists':
            artist_list = []
            for artist in serializer.data['artists']:
                # Se reutiliza la función get_artist para obtener la información de los artistas
                new_artist = get_data('artists', artist['code'])
                if 'artist' in new_artist:
                    artist_list.append(new_artist['artist'])
            return Response({'artist list': artist_list})
        else:
            Response({"error": f"Unexpected error {type}"}, status=status.HTTP_400_BAD_REQUEST)
        
    def delete(self, request, type, email):
        """
            Se elimina una canción de las favoritas de un usuario
        """
        # Se comprueba que existe el usuario
        try:
            user = Users.objects.get(pk=email)
        except Users.DoesNotExist:
            return Response({"error": f'No existe el usuario {email}'}, status=status.HTTP_404_NOT_FOUND)
        
        data = request.data
 

        if type == 'songs':
            try:
                item = Songs.objects.get(code=data['code'])
            except Songs.DoesNotExist:
                return Response({"error": f'No existe la cancion {data['code']} en el listado del usuario {email}'}, status=status.HTTP_404_NOT_FOUND)
            except Songs.MultipleObjectsReturned:
                # Esto no deberia pasar, ya que se ha establecido que no puede repetirse un par codigo usuario
                return Response({"error": 'Más de un elemento encontrado'}, status=status.HTTP_409_CONFLICT)
            
        elif type == 'artists':
            try:
                item = Artists.objects.get(code=data['code'])
            except Artists.DoesNotExist:
                return Response({"error": f'No existe la cancion {data['code']} en el listado del usuario {email}'}, status=status.HTTP_404_NOT_FOUND)
            except Artists.MultipleObjectsReturned:
                # Esto no deberia pasar, ya que se ha establecido que no puede repetirse un par codigo usuario
                return Response({"error": 'Más de un elemento encontrado'}, status=status.HTTP_409_CONFLICT)
            return Response(status=status.HTTP_204_NO_CONTENT)
        else:
            Response({"error": f"Unexpected error {type}"}, status=status.HTTP_400_BAD_REQUEST)

        item.delete()
        return Response({"message": "Elemento eliminado con exito"}, status=status.HTTP_204_NO_CONTENT)

