from rest_framework import serializers
from .models import Users, Songs, Artists

class SongObjectSerializer(serializers.ModelSerializer):
    """
        Este serializador devuelve todos los elementos del modelo Songs
    """
    class Meta:
        model = Songs
        fields = '__all__'
    
class SongUserSerializer(serializers.ModelSerializer):
    """
        Este serializador devuelve el codigo de cada instancia del modelo Songs
    """
    class Meta:
        model = Songs
        fields = ('code', )

class ArtistObjectSerializer(serializers.ModelSerializer):
    """
        Este serializador devuelve todos los elementos del modelo Artists
    """
    class Meta:
        model = Artists
        fields = '__all__'

class ArtistUserSerializer(serializers.ModelSerializer):
    """
        Este serializador devuelve el codigo de cada instancia del modelo Artists
    """
    class Meta:
        model = Artists
        fields = ('code', )

class UserSerializer(serializers.ModelSerializer):
    """
        Este serializador devuelve todos los elementos del modelo Users, 
        añadiendo el listado de instancias de songs y artists relacionadas con el email del usuario
        a traves del SongUserSerializer y ArtistUserSerializer
    """
    songs = SongUserSerializer(many=True)
    artists = ArtistUserSerializer(many=True)
    class Meta:
        model = Users
        fields = ('email', 'name', 'songs', 'artists', )
