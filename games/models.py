from django.contrib.auth.models import User
from django.db import models

class Game(models.Model):                           # Tipo de dato de la BD --> Game
    # Cambiar el tipo de 'id' (IntegerField o AutoField) -> CharField
    # --> 'PREFIJO-xxx' --> 255 chars
    # Clave primaria (modificada) -> identificador único de cada objeto de este tipo en la base de datos:
    id = models.CharField(max_length=255, primary_key=True)
    # 200 chars -> Título del juego:
    title = models.CharField(max_length=200)
    # 100 chars -> Plataforma:
    platform = models.CharField(max_length=100)
    # 100 chars -> Género:
    genre = models.CharField(max_length=100)
    # 100 chars -> Publicador:
    publisher = models.CharField(max_length=100)
    # 200 chars -> Desarrollador:
    developer = models.CharField(max_length=200)
    # AAAA-MM-DD  --> Fecha:
    release_date = models.DateField()
    # Texto largo -> Longitud dinámica --> Descripción del juego:
    description = models.TextField()
    # Número -> 2 dígitos con 1 decimal --> Media de votos:
    average_rating = models.DecimalField(max_digits=2, decimal_places=1, default=0)
    # Número entero --> Número de votos:
    vote_count = models.IntegerField(default=0)
    # URL -> 500 chars --> URL del juego en FreeToGame:
    freetogame_profile_url = models.URLField(max_length=500)
    # URL -> 500 chars --> URL del juego:
    game_url = models.URLField(max_length=500)
    # URL -> 500 chars --> URL de la miniatura:
    thumbnail = models.URLField(max_length=500)

    # null=True -> Permite que el campo sea null
    # blank=True -> Permite que no se rellene el campo en un formulario
    # default=0 -> Valor por defecto del campo -> 0 si no se introduce nada

    # -> game.is_followed_by_user(user) => True o False
    def is_followed_by_user(self, user):
        # Comprobar si el User autenticado sigue el juego o no
        if not user.is_authenticated:   # Ver si está autenticado primero
            return False
        # Ver si existe relación UserGameFollow del User con el Game en la base de datos:
        return UserGameFollow.objects.filter(user=user, game=self).exists()

    def __str__(self):      # Forma de llamar al objeto -> Título del juego
        return self.title


class Comment(models.Model):                        # Tipo de dato de la BD --> Comment
    # ForeignKey -> Relación con Game --> Campo 'comments' de un dato tipo Game
    # --> Contiene todos los datos tipo Comment de ese Game --> game.comments
    # on_delete=models.CASCADE --> Si se borra un Game -> se borran todos los 'coments' (datos tipo Comment) asociados
    game = models.ForeignKey(Game, related_name='comments', on_delete=models.CASCADE)
    # 100 chars -> si no se introduce nada ->"Anonymous" --> Nombre del usuario:
    user = models.CharField(max_length=100, default="Anonymous")
    # Texto largo --> Longitud dinámica -> Comentario en si:
    text = models.TextField()
    # Número entero --> Valoración
    # -> Puede ser null si no se valora y se comenta, por lo que puede ir en blanco en el form:
    rating = models.IntegerField(null=True, blank=True)
    # Fecha y hora del comentario -> automáticamente al crear o actualizar el objeto:
    timestamp = models.DateTimeField(auto_now=True)

    # @ property -> Decorador -> definir un método en una clase que puede ser accedido como si fuera un atributo/campo
    # Número de likes:
    @property
    def likes_count(self):
        return self.likes.filter(like=True).count()

    # Número de dislikes:
    @property
    def dislikes_count(self):
        return self.likes.filter(dislike=True).count()

    def __str__(self):       # Forma de llamar al objeto Comment
        return f"Comment by {self.user} of {self.game.title} on {self.timestamp}"


class Like(models.Model):        # Tipo de dato de la BD --> Like o Dislike
    # ForeignKey -> Relación con Comment --> Campo 'likes' de un dato tipo Comment
    comment = models.ForeignKey(Comment, related_name='likes', on_delete=models.CASCADE)
    # ForeignKey -> Relación con User --> Campo 'likes' de un dato tipo User
    user = models.ForeignKey(User, related_name='likes', on_delete=models.CASCADE)
    # BooleanField -> Campo de tipo booleano => Like
    like = models.BooleanField(default=False)
    # BooleanField -> Campo de tipo booleano => Dislike
    dislike = models.BooleanField(default=False)
    # Fecha y hora del like -> Automáticamente al crear o actualizar el objeto:
    timestamp = models.DateTimeField(auto_now=True)

    # Clase Meta: --> Opciones adicionales del modelo Like en la base de datos
    # -> contiene metadatos ya de la base de datos
    class Meta:
        # Un User y un Comment solo puedan estar relacionados una vez en la tabla del modelo `Like`
        unique_together = ('comment', 'user')

    def is_valid_vote(self):
        # Solo válido si no están ambos a True
        return not (self.like and self.dislike)

    def __str__(self):
        if self.like:
            status = "👍 Like"
        elif self.dislike:
            status = "👎 Dislike"
        else:
            status = "❓ No vote"
        return f"{status} by {self.user.username} on {self.comment.game.title}"


class UserGameFollow(models.Model):     # Tipo de dato de la BD --> UserGameFollow --> Seguidores de los juegos (users)
    # ForeignKey: Punteros a un campo de otro modelo de la BD
    # User(django) -> campo 'followed_games' en objeto User => user.followed_games
    # Game -> campo 'followers' en objeto Game => game.followers
    # --> Contiene todos los datos tipo UserGameFollow de ese User ó Game
    # on_delete=models.CASCADE --> Si se borra un Game o User -> se borran todos los datos tipo UserGameFollow asociados
    user = models.ForeignKey(User, related_name='followed_games', on_delete=models.CASCADE)
    game = models.ForeignKey(Game, related_name='followers', on_delete=models.CASCADE)
    # Fecha y hora del seguimiento -> automáticamente al crear el objeto:
    followed_at = models.DateTimeField(auto_now_add=True)

    # Clase Meta: --> Opciones adicionales del modelo UserGameFollow en la base de datos
    # -> contiene metadatos ya de la base de datos
    class Meta:
        # Restricción de unicidad -> Un usuario no puede seguir el mismo juego dos veces => solo 1 vez
        # Un User y un Game solo puedan estar relacionados una vez en la tabla del modelo `UserGameFollow`
        # No puede haber dos UserGameFollow pertenecientes al mismo User y Game en la base de datos
        # Le damos nombre a la restricción: 'unique_user_game_follow'
        constraints = [
            models.UniqueConstraint(fields=['user', 'game'], name='unique_user_game_follow')
        ]

    def __str__(self):      # Forma de llamar al objeto UserGameFollow
        return f"{self.user.username} follows {self.game.title}"


class Profile(models.Model):                # Tipo de dato de la BD --> Datos del perfil del user
    # Usuario a asignar el perfil -> user.profile:
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    # 50 chars -> Tipo de fuente (default: Arial)
    font_type = models.CharField(max_length=50, default="Arial")
    # 10 chars -> Tamaño de fuente (default: 12px)
    font_size = models.CharField(max_length=10, default="18px")

    def __str__(self):
        return self.user.username

class ValidPassword(models.Model):          # Tipo de dato de la BD --> ValidPassword -> Contraseñas globales de acceso sin registro
    # 255 chars -> Password a verificar para acceso sin registro -> globales
    value = models.TextField(unique=True)

    def __str__(self):      # Forma de llamar al objeto -> Password en si
        return self.value
