from .models import Game, Comment

# Contexto base a pasar a todos los templates => Middleware:
def stats(request):
    games_count = Game.objects.count()
    comments_count = Comment.objects.count()

    # Referencia a la vista anterior:
    # request.META -> diccionario de Django que tiene todas las cabeceras HTTP (headers) de la solicitud del navegador:
    # 'HTTP_REFERER' → URL de página desde la que vino el user
    # Si 'HTTP_REFERER' no existe (acceso directo) -> devuelve '/' (main)
    referer = request.META.get('HTTP_REFERER', '/')

    voted_games_count = 0
    user_comments_count = 0

    # Si el usuario está autenticado, calcula sus juegos votados y sus comentarios
    if request.user.is_authenticated:
        comments = Comment.objects.filter(user=request.user.username)

        # Contamos los juegos votados (rating >= 0) y sin duplicados (aunque no debería haberlos)
        voted_games = comments.filter(rating__gte=0).values('game').distinct()
        voted_games_count = voted_games.count()

        # Contamos los comentarios del usuario que tienen texto (campo 'text' no vacío)
        user_comments_count = comments.filter(text__isnull=False).exclude(text__exact="").count()

    # Valores únicos para los filtros:
    # Listas (flat=True) con los parámetros disponibles en la base de datos
    # distinct() -> elimina duplicados
    platforms = Game.objects.values_list('platform', flat=True).distinct().order_by('platform')
    genres = Game.objects.values_list('genre', flat=True).distinct().order_by('genre')
    publishers = Game.objects.values_list('publisher', flat=True).distinct().order_by('publisher')

    return {
        'games_count': games_count,
        'comments_count': comments_count,
        'voted_games_count': voted_games_count,
        'user_comments_count': user_comments_count,
        'previous_page': referer,
        'platforms': platforms,
        'genres': genres,
        'publishers': publishers,
    }