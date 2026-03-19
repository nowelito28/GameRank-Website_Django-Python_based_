from django.contrib import messages
from django.core.paginator import Paginator
from django.http import Http404, JsonResponse, HttpResponse
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
import xml.etree.ElementTree as ET
from django.utils.translation import gettext as _
from urllib.parse import urlencode

from .forms import RatingCommentForm
from .models import Game, Comment, UserGameFollow, Like
from .utils import load_games


# GET / -> Muestra el listado de juegos con sus comentarios --> guardados en la base de datos
def main(request):
    # Cargamos los datos de las APIs: XML(1) y JSON(2):
    load_games('XML', 'https://gitlab.eif.urjc.es/cursosweb/2024-2025/final-gamerank/-/raw/main/listado1.xml', 'LIS1-')
    load_games('JSON', 'https://www.freetogame.com/api/games', 'LIS2-')
    load_games('JSON', 'https://www.mmobomb.com/api1/games', 'LIS3-')

    # Filtrado de juegos desde la petición GET
    # Parámetros de la URL -> ej => ?platform=PC+(Windows)&genre=ARPG&publisher=101XP
    platform = request.GET.get('platform', '').strip()
    genre = request.GET.get('genre', '').strip()
    publisher = request.GET.get('publisher', '').strip()

    # Obtener todos los juegos de la base de datos:
    games = Game.objects.all()

    # Generar query string sin el parámetro 'page'
    query_params = {}

    # Si se le ha pasado el parámetro en el body -> filtrar juegos:
    if platform:
        games = games.filter(platform=platform)
        query_params['platform'] = platform
    if genre:
        games = games.filter(genre=genre)
        query_params['genre'] = genre
    if publisher:
        games = games.filter(publisher=publisher)
        query_params['publisher'] = publisher

    # Construir la query string -> ej: platform=PC&genre=Action
    query_string = urlencode(query_params)

    # Mensaje info de filtrado:
    if platform or genre or publisher:
        if games.exists():
            messages.success(request, _("%(count)d games found with selected filters!!!") % {"count": games.count() })
        else:
            messages.warning(request, _("No games match the selected filters!!!"))

    # Listar juegos por puntuación ascendente -> de mayor a menor (descendente) puntuación:
    games = games.order_by('-average_rating')

    # Asignar a cada Game -> nuevo atributo dinámico no persistente -> no se guarda en la base de datos
    # Debido a que varía dependiendo del User
    for game in games:
        game.is_following = game.is_followed_by_user(request.user)

    # Configuración de la paginación (30 juegos por página) -> separa games en páginas:
    paginator = Paginator(games, 30)
    # Número de página actual en el campo 'page' del cuerpo de la petición GET:
    page_number = request.GET.get('page')
    # Games de la página actual:
    games_page = paginator.get_page(page_number)

    # Renderizar plantilla html --> games/main.html -> pasando el listado de juegos de la página
    # y parámetros de los filtros si se ha hecho filtrado de juegos:
    return render(request, 'games/main.html', {
        'games': games_page,
        'query_string': query_string,
    })



# GET /rated_games -> Muestra los juegos que ha votado el usuario
def rated_games(request):
    # Si no está autenticado, redirigir al login:
    if not request.user.is_authenticated:
        messages.error(request, _("Login required to access this page!!!"))
        return redirect('login')

    # Juegos que el usuario ha puntuado (y comentado):
    # values_list('game', flat=True) -> lista plana de ids de games asociados al user
    # filter(id__in=rated_game_ids) -> filtrar games con id en la lista rated_games_ids
    # order_by('-rating') -> Ordenar por puntuación descendente (mayor a menor)
    rated_game_ids = Comment.objects.filter(user=request.user, rating__gte=0).values_list('game', flat=True)
    rated_games = Game.objects.filter(id__in=rated_game_ids).order_by('-average_rating')

    # Buscar tabla NN UserGameFollow -> juegos seguidos por el User mediante ForeignKeys
    # values_list() -> obtener solo los lista (no de tuplas) de valores **id** de cada Game de la columna game
    followed_games = UserGameFollow.objects.filter(user=request.user).values_list('game', flat=True)

    # Para cada juego, agregamos los comentarios asociados
    rated_game_details = []
    for game in rated_games:
        # Única valoración del usuario (si existe)
        rated_comment = Comment.objects.filter(game=game, user=request.user, rating__gte=0).first()

        if rated_comment:
            comments = [rated_comment]

            # Obtener resto de comentarios para este juego y el usuario
            other_comments = (Comment.objects.filter(game=game, user=request.user)
                              .exclude(id=rated_comment.id).order_by('-timestamp'))

            # Añadir comentarios restantes:
            comments += list(other_comments)

        else:
            # Sin valoración -> Obtener los comentarios para este juego y el usuario
            # (NUNCA PASA -> VISTA DE RATED GAMES)
            comments = Comment.objects.filter(game=game, user=request.user).order_by('-timestamp')

        # Paginación (5 comentarios por página):
        paginator = Paginator(comments, 5)
        # Identificador único para cada page de valoraciones de cada juego
        # (parámetro en la URL: page_{game.id})
        page_number = request.GET.get(f"page_{game.id}", 1)
        page_comments = paginator.get_page(page_number)

        # Contexto de cada juego con sus comentarios
        rated_game_details.append({
            'game': game,
            'comments': page_comments
        })

    # Paginación (5 juegos por página)
    paginator = Paginator(rated_game_details, 5)
    page_number = request.GET.get("page")
    page_rated_games = paginator.get_page(page_number)

    # Renderizar plantilla html --> games/rated_games.html con los juegos que ha votado el usuario y los seguidos
    return render(request, 'games/rated_games.html',
                  {'rated_games': page_rated_games, 'followed_games': followed_games})


# GET /followed_games -> Muestra los juegos que ha seguido el usuario
def followed_games(request):
    # Si no está autenticado, redirigir al login:
    if not request.user.is_authenticated:
        messages.error(request, _("Login required to access this page!!!"))
        return redirect('login')

    # Juegos seguidos por el usuario -> ordenados descendentemente (mayor a menor):
    # --> Acceso indirecto a tablas NN UserGameFollow del user con acceso a cada juego seguido
    followed_games = (UserGameFollow.objects.filter(user=request.user).
    select_related('game').order_by('-game__average_rating'))

    # Paginación (5 juegos por página)
    paginator = Paginator(followed_games, 5)
    page_number = request.GET.get("page")
    followed_games_page = paginator.get_page(page_number)

    # Renderizar plantilla html --> games/followed_games.html con los juegos que ha seguido el usuario
    return render(request, 'games/followed_games.html', {'followed_games': followed_games_page})


# GET /follow/<game_id> -> User follows a Game -> new UserGameFollow
@login_required
def follow_game(request, game_id):
    try:
        # get_object_or_404 -> devuelve un objeto concreto (Game con id=game_id) si existe en la base de datos
        # sino devuelve un 404
        game = get_object_or_404(Game, id=game_id)
    except Http404:
        # Plantilla de error 404
        return render(request, 'games/404error.html', status=404)

    # Crear relación única entre User y Game -> UserGameFollow
    UserGameFollow.objects.get_or_create(user=request.user, game=game)

    # Renderizar plantilla con mensajes de info --> con redirección a main
    return render(request, 'games/follow.html', {
        'action': 'follow',
        'game': game,
    })

# GET /unfollow/<game_id> -> User unfollows a Game -> delete UserGameFollow
@login_required
def unfollow_game(request, game_id):
    try:
        # get_object_or_404 -> devuelve un objeto concreto (Game con id=game_id) si existe en la base de datos
        # sino devuelve un 404
        game = get_object_or_404(Game, id=game_id)
    except Http404:
        # Plantilla de error 404
        return render(request, 'games/404error.html', status=404)

    # Eliminar relación única entre User y Game -> UserGameFollow
    UserGameFollow.objects.filter(user=request.user, game=game).delete()

    # Renderizar plantilla con mensajes de info --> con redirección a main
    return render(request, 'games/follow.html', {
        'action': 'unfollow',
        'game': game,
    })

# GET /<game_id> -> Detalles de un juego
# POST /<game_id> -> Procesar formulario de valoración y comentario
def game_detail(request, game_id):
    try:
        # get_object_or_404 -> devuelve un objeto concreto
        # -> (Game con id=game_id (str)) si existe en la base de datos
        # -> sino devuelve un 404
        game = get_object_or_404(Game, id=game_id)
    except Http404:
        # Plantilla de error 404
        return render(request, 'games/404error.html', status=404)

    # Status por defecto: 200
    status = 200

    # Comprobar si el User autenticado sigue el juego o no
    game.is_following = game.is_followed_by_user(request.user)

    # Definir formulario a pasar/recibir de la plantilla:
    # None si es GET (se crea)
    # request.POST si es POST -> datos rellenados del formulario
    rating_comment_form = RatingCommentForm(request.POST or None)

    # Verificar si se debe activar HTMX -> argumento 'htmx_toggle':
    is_dynamic = request.GET.get('htmx_toggle') == 'true'

    # Procesar formulario de valoración:
    # Verificar:
    # -> método POST
    # -> se envió el formulario de valoración y comentario relleno ('rate_comment_game.rating' y 'rate_comment_game.text')
    # -> es válido
    if request.method == 'POST' and 'rate_comment' in request.POST:
        if rating_comment_form.is_valid():
            # Datos válidos del user -> cleaned_data -> diccionario con datos del form
            # 'rating' = nombre del campo del formulario -> rating_comment_form (igual con 'text')
            rating = rating_comment_form.cleaned_data['rating']
            text = rating_comment_form.cleaned_data['text']

            # Verificar si ambos campos están vacíos o si el campo de comentario tiene solo espacios
            if rating is None and not text.strip():  # Error si ambos campos están vacíos
                messages.error(request, _("Please provide a rating and/or a comment!"))
                status = 401

            else: # Si se proporciona una valoración -> modificar valoración media:

                if rating is not None:
                    # Verificar si el juego ya ha sido valorado por el user:
                    existing_rating_comment = Comment.objects.filter(game=game,
                                                                     user=request.user,
                                                                     rating__gte=0).first()

                    if existing_rating_comment:
                        # Modificar media de puntuación existente del juego:
                        total_rating = game.average_rating * game.vote_count
                        total_rating = total_rating - existing_rating_comment.rating + rating

                        if game.vote_count == 1:
                            # Si solo hay una valoración, y se cambia a 0
                            game.average_rating = 0.0 if rating == 0 else round(rating, 1)
                        else:
                            game.average_rating = round(total_rating / game.vote_count, 1)

                        # Actualizar valoración (y comentario si tiene) existente:
                        existing_rating_comment.rating = rating
                        existing_rating_comment.text = text
                        existing_rating_comment.save()
                        messages.success(request, _("Your rating has been updated!!!"))

                    else:
                        # Actualizar campos del modelo Game:
                        game.vote_count += 1  # Incrementar contador de votos

                        # Modificar media de puntuación nueva:
                        # Calcular suma total de las valoraciones previas:
                        total_rating = game.average_rating * (game.vote_count - 1)
                        # Sumar la nueva valoración:
                        total_rating += rating

                        if game.vote_count == 1:
                            game.average_rating = 0.0 if rating == 0 else round(rating, 1)
                        else:
                            game.average_rating = round(total_rating / game.vote_count, 1)

                        # Crear un Comment -> valoración (y comentario) hecha:
                        Comment.objects.create(
                            game=game,  # Guardar dueño del comentario, si no está logado -> Anonymous
                            user=request.user.username if request.user.is_authenticated else _('Anonymous'),
                            rating=rating,
                            text=text
                        )

                        messages.success(request, _("Your rating has been saved!!!"))

                    # Guardar cambios en la base de datos:
                    game.save()

                else:

                    # Crear un Comment -> Comentario hecho (solo):
                    Comment.objects.create(
                        game=game,  # Guardar dueño del comentario, si no está logado -> Anonymous
                        user=request.user.username if request.user.is_authenticated else _('Anonymous'),
                        text=text
                    )
                    # messages -> Django envía mensajes de diferentes niveles implícitamente a la plantilla que se renderiza
                    messages.success(request, _("Your comment has been saved!!!"))

        else:
            messages.error(request, _("Please provide a rating and/or a comment!"))
            status = 401


    # Obtener todos los comentarios del juego
    # ordenados por fecha => timestamp (recientes a antiguos -> descendente):
    comments = Comment.objects.filter(game=game).order_by('-timestamp')

    # Paginar comentarios -> 5 comentarios por página:
    paginator = Paginator(comments, 5)
    # Obtener número de la página actual
    # -> campo 'page' del body del GET /details:
    page_number = request.GET.get('page')
    # Comentarios a mostrar en el template (página actual):
    comments_page = paginator.get_page(page_number)

    # Si es solicitud HTMX (cabecera) y está activo el modo dinámico:
    if request.headers.get('HX-Request'):
        # Si es dinámica -> solo renderizamos la sección de comentarios:
        return render(request, 'games/comments_section.html', {
            'comments': comments_page,
        })

    return render(request, 'games/details.html', {
        'game': game,
        'comments': comments_page,
        'is_following': game.is_following,
        'is_dynamic': is_dynamic,
        'rating_comment_form': rating_comment_form,
    }, status=status)


# GET /help -> Ayuda/Funcionalidad de la aplicación games
def help_view(request):
    return render(request, 'games/help.html')


# GET /<game_id>.json -> JSON de un juego
def game_json(request, game_id):
    # Si el id del juego no está en la base de datos -> 404
    try:
        game = get_object_or_404(Game, id=game_id)
    except Http404:
        return render(request, 'games/404error.html', status=404)

    # Comentarios y valoraciones asociados al juego:
    comments = Comment.objects.filter(game=game)
    num_comments = comments.filter(text__isnull=False).exclude(text__exact="").count()
    num_ratings = comments.exclude(rating=None).count()

    # Campos del juego en formato JSON
    data = {
        'id': game.id,
        'title': game.title,
        'platform': game.platform,
        'genre': game.genre,
        'developer': game.developer,
        'publisher': game.publisher,
        'release_date': game.release_date,
        'description': game.description,
        'average_rating': game.average_rating,
        'vote_count': game.vote_count,
        'freetogame_profile_url': game.freetogame_profile_url,
        'game_url': game.game_url,
        'thumbnail': game.thumbnail,
        'num_comments': num_comments,
        'num_ratings': num_ratings,
    }

    # Devolver el diccionario en formato JSON:
    return JsonResponse(data)


# GET /<game_id>.xml -> XML de un juego
def game_xml(request, game_id):
    # Si el id del juego no está en la base de datos -> 404
    try:
        game = get_object_or_404(Game, id=game_id)
    except Http404:
        return render(request, 'games/404error.html', status=404)

    # Comentarios y valoraciones asociados al juego:
    comments = Comment.objects.filter(game=game)
    num_comments = comments.filter(text__isnull=False).exclude(text__exact="").count()
    num_ratings = comments.exclude(rating=None).count()

    # Crear el DOM del XML -> root = <game>
    root = ET.Element("game")

    # Campos del juego en formato XML:
    ET.SubElement(root, "id").text = game.id
    ET.SubElement(root, "title").text = game.title
    ET.SubElement(root, "platform").text = game.platform
    ET.SubElement(root, "genre").text = game.genre
    ET.SubElement(root, "developer").text = game.developer
    ET.SubElement(root, "publisher").text = game.publisher
    ET.SubElement(root, "release_date").text = str(game.release_date)
    ET.SubElement(root, "description").text = game.description
    ET.SubElement(root, "average_rating").text = str(game.average_rating)
    ET.SubElement(root, "vote_count").text = str(game.vote_count)
    ET.SubElement(root, "freetogame_profile_url").text = game.freetogame_profile_url
    ET.SubElement(root, "game_url").text = game.game_url
    ET.SubElement(root, "thumbnail").text = game.thumbnail
    ET.SubElement(root, "num_comments").text = str(num_comments)
    ET.SubElement(root, "num_ratings").text = str(num_ratings)
    # Pasar el DOM del XML en string
    xml_str = ET.tostring(root, encoding='utf-8', method='xml')

    # Devolver el string en formato XML -> Django serializara el string en XML:
    return HttpResponse(xml_str, content_type='application/xml')


# GET /like/<comment_id> -> Like/Dislike via HTMX
# POST /like/<comment_id> -> Like/Dislike via POST HTMX usando query strings -> ?like_type=...
# Se mantiene el csrf_token
def like_comment(request, comment_id):
    # Si no está autenticado, redirigir al login:
    if not request.user.is_authenticated:
        messages.error(request, _("Login required to like a comment!!!"))
        return redirect('login')

    # Buscar comentario por id del objeto
    # Si el id del comentario no está en la base de datos -> 404
    try:
        comment = get_object_or_404(Comment, id=comment_id)
    except Http404:
        return render(request, 'games/404error.html', status=404)

    # Obtener o crear objeto de Like:
    like_obj, created = Like.objects.get_or_create(
        comment=comment,
        user=request.user,
    )

    if request.method == 'POST':
        # Query strings --> Formulario HTMX de like -> tipo
        like_type = request.POST.get("like_type")

        if like_type == 'like':
            if like_obj.like:
                # Anular like
                like_obj.like = False
            elif not like_obj.like:
                # Dar like
                like_obj.like = True
            # Dislike a False
            like_obj.dislike = False

        else:
            if like_obj.dislike:
                # Anular dislike
                like_obj.dislike = False
            elif not like_obj.dislike:
                # Dar dislike
                like_obj.dislike = True
            # Like a False
            like_obj.like = False

        # Guardar cambios en la base de datos
        like_obj.save()

    # Para GET y POST:
    # Solo renderizar botones de like y dislike -> para realizar formulario:
    return render(request, 'games/like.html', {
        'comment': comment,
        'user': request.user,
        'like': like_obj,
        'like_options': [('like', '👍 '+_('Like')), ('dislike', '👎 '+_('Dislike'))],
    })
