from django.urls import path
from . import game_views, user_views

urlpatterns = [ # Definición de rutas a partir del path principal --> http://ip:puerto/...
    # -->  path definido en urls.py del proyecto para la app games
    # main = http://ip:puerto/ -> Página principal de la app:
    path('', game_views.main, name='main'),
    # global_login = http://ip:puerto/global_login -> Formulario login de password global de acceso:
    path('global_login/', user_views.global_login_view, name='global_login'),
    # login = http://ip:puerto/login -> Formulario de inicio de sesión:
    path('login/', user_views.login_view, name='login'),
    # profile = http://ip:puerto/profile -> Perfil del usuario:
    path('profile/', user_views.user_profile, name='user_profile'),
    # rated_games = http://ip:puerto/rated_games -> Juegos que ha votado el usuario:
    path('rated_games/', game_views.rated_games, name='rated_games'),
    # followed_games = http://ip:puerto/followed_games -> Juegos que ha seguido el usuario:
    path('followed_games/', game_views.followed_games, name='followed_games'),
    # user_settings = http://ip:puerto/user_settings -> Formulario de configuración del usuario:
    path('user_settings/', user_views.user_settings, name='user_settings'),
    # help = http://ip:puerto/help -> Ayuda/Funcionalidad de la app:
    path('help/', game_views.help_view, name='help'),
    # register = http://ip:puerto/register -> Formulario de registro:
    path('register/', user_views.register, name='register'),
    # logout = http://ip:puerto/logout -> Gestionar logout de un usuario:
    path('logout/', user_views.logout_view, name='logout'),
    # follow_game = http://ip:puerto/follow_game/<game_id> -> User follows a Game:
    path('follow_game/<str:game_id>', game_views.follow_game, name='follow_game'),
    # unfollow_game = http://ip:puerto/unfollow_game/<game_id> -> User unfollows a Game:
    path('unfollow_game/<str:game_id>', game_views.unfollow_game, name='unfollow_game'),
    # like = http://ip:puerto/like/<comment_id> -> Dar like a un comentario:
    path('like/<int:comment_id>', game_views.like_comment, name='like'),
    # set_language = http://ip:puerto/set-language/<lang_code> -> Cambiar idioma: es o en
    path('set-language/<str:lang_code>/', user_views.set_language, name='set_language'),
    # game_json = http://ip:puerto/<game_id>.json -> JSON de un juego:
    path('<str:game_id>.json', game_views.game_json, name='game_json'),
    # game_xml = http://ip:puerto/<game_id>.xml -> XML de un juego:
    path('<str:game_id>.xml', game_views.game_xml, name='game_xml'),
    # game_detail = http://ip:puerto/<game_id> -> Detalles de un juego:
    path('<str:game_id>/', game_views.game_detail, name='game_detail'),
]