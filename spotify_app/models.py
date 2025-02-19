from django.db import models

class Users(models.Model):
    """
        Modelo de los usuarios de la aplicación
    """
    # Solo puede haber un usuario para cada email, por lo que también se usará como clave primaria
    email = models.TextField(unique=True, primary_key=True)
    name = models.TextField()
    
    def __str__(self):
        return self.email


class Songs(models.Model):
    """
        Cada instancia de esta clase contiene el codigo de Spotify perteneciente a una cancion de las favoritas de un usuario, identificado por su email
    """
    code = models.TextField()
    # email es la clave foranea de Users, relacionando ambas tablas
    # Al eliminar un usuario se eliminarán sus canciones favoritas, de ahi que on_delete=models.CASCADE
    email = models.ForeignKey(Users, related_name='songs', on_delete=models.CASCADE)
    
    class Meta:
        # Con esto se establece que no se puede repetir un par code email en el modelo
        unique_together = ('code', 'email')
    
class Artists(models.Model):
    """
        Cada instancia de esta clase contiene el codigo de Spotify perteneciente a un artista de los favoritos de un usuario, identificado por su email
    """
    code = models.TextField()
    # email es la clave foranea de Users, relacionando ambas tablas
    email = models.ForeignKey(Users, related_name='artists', on_delete=models.CASCADE)

    class Meta:
        # Con esto se establece que no se puede repetir un par code email en el modelo
        unique_together = ('code', 'email')