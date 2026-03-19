from django.contrib import messages
from django.shortcuts import redirect
from django.utils.translation import gettext as _

from .models import ValidPassword


# Clase middleware -> interceptará peticiones entrantes antes de que lleguen a las vistas!!!
class PasswordMiddleware:

    # Constructor del middleware:
    def __init__(self, get_response):
        # Guardar referencia a la siguiente vista solicitada:
        self.get_response = get_response

    # Se llama en cada petición HTTP
    # -> decide si se deja pasar o redirigir al login global:
    def __call__(self, request):
        # Definir paths de la app permitidos sin login global:
        allowed_paths = ['/', '/static/', '/favicon.ico', '/global_login/']

        # Comprobar si path de la vista solicitada
        # -> NO pertenece a los paths permitidos => ver si tiene la cookie de sesión <-> redirigir al login global
        # -> SI pertenece a los paths permitidos -> ***seguir con la petición***
        if any(request.path == path for path in allowed_paths):
            return self.get_response(request)

        # Cookie de sesión con la contraseña global -> si existe:
        password_cookie = request.COOKIES.get('global_pass')
        if password_cookie:
            # Verificar si la contraseña es válida en la base de datos
            # -> para continuar con la vista solicitada
            if ValidPassword.objects.filter(value=password_cookie).exists():
                return self.get_response(request)

        # También puede llevar la contraseña en la cabecera Authorization:
        # Obtener cabecera Authorization si la hay -> y si empieza con 'Basic ':
        auth_header = request.META.get('HTTP_AUTHORIZATION')
        if auth_header and auth_header.startswith('Basic '):
            # Extraer solo la password
            password = auth_header.replace('Basic ', '').strip()
            # Verificar si la contraseña es válida en la base de datos
            # -> para continuar con la vista solicitada
            if ValidPassword.objects.filter(value=password).exists():
                return self.get_response(request)

        # Si NO hay cookie de sesión con la contraseña: Solo redirigimos al login global
        # Si es incorrecta: igual pero con mensaje de error
        if password_cookie:
            messages.error(request, _("Invalid password"))

        return redirect('/global_login/')
