from django.contrib.auth import login, logout
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.contrib import messages
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.utils.translation import gettext as _
from django.utils import translation
from urllib.parse import urlparse
from django.conf import settings

from .forms import UserSettingsForm, PasswordAuthForm
from .models import Comment, Profile, ValidPassword


# GET /global_login -> Verificar contraseñas globales de acceso (mandar formulario)
# POST /global_login -> Procesar el formulario de login de contraseña global
# -> Solo se loguea una vez -> Mandar cookie para mantener sesión
# 1º inicio de sesión -> Guardar cookie -> Redirigir a la página principal
# 2º inicio de sesión -> login con user y contraseña
def global_login_view(request):
    # Si NO hay ninguna contraseña global en la base de datos todavía
    # -> Creamos la primera por defecto:
    if not ValidPassword.objects.exists():
        ValidPassword.objects.create(value='xx34d23')

    if request.method == 'POST':
        # Respuesta del formulario:
        form = PasswordAuthForm(request.POST)

        # Verificar formulario válido:
        if form.is_valid():
            # Obtener campo password del formulario:
            password = form.cleaned_data['password']

            # Verificar si la contraseña está en la base de datos:
            if ValidPassword.objects.filter(value=password).exists():
                # Redirigir al usuario al main con la contraseña guardada en cookie -> global_pass:
                response = redirect('main')
                response.set_cookie('global_pass', password)
                return response

        # Renderizar plantilla del login de password global de acceso -> error de contraseña inválida:
        messages.error(request, _("Invalid password"))
        return render(request, 'games/global_login.html', {'form': form}, status=401)

    else:
        # Crear formulario de password global -> Renderizar plantilla del login de password global de acceso:
        form = PasswordAuthForm()
        return render(request, 'games/global_login.html', {'form': form})


# GET /login -> Interfaz de login de un usuario
# POST /login -> Procesar el formulario de login
def login_view(request):
    if request.method == "POST":
        # Procesar el formulario de inicio de sesión de django recibido con el POST
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            # Si es válido (crsf_token) y credenciales correctas -> Obtener el User autenticado
            user = form.get_user()

            # Crear perfil para el User si NO existe:
            # hasattr(user, 'profile') -> Verifica si objeto User (usuario autenticado de Django)
            # tiene un atributo llamado 'profile' (Profile):
            if not hasattr(user, 'profile'):
                Profile.objects.create(user=user)

            # Realizar el login en la base de datos
            login(request, user)

            # Redirigir al usuario a la página principal
            return redirect('user_profile')

        else:
            # Mensaje de error:
            messages.error(request, _("Invalid username or password!!!"))
            # Si el formulario no es válido, se renderiza con errores
            return render(request, 'games/login.html', status=401, context={'form': form})

    else:
        # Inicializar el formulario de inicio de sesión de django y pasarlo a la plantilla
        form = AuthenticationForm()

    # Renderizar la plantilla de inicio de sesión:
    return render(request, 'games/login.html', {'form': form})


# GET /profile -> Muestra el perfil del usuario
def user_profile(request):
    # Si no está autenticado, redirigir al login:
    if not request.user.is_authenticated:
        messages.error(request, _("Login required to access this page!!!"))
        return redirect('login')

    # Votaciones realizadas por el usuario:
    # rating__isnull=False -> filtrar por valores no nulos:
    votes = Comment.objects.filter(user=request.user, rating__isnull=False)

    # Número de votos del user:
    vote_count = votes.count()

    # Puntuación media del usuario:
    # Obtener todas las valoraciones del usuario:
    # values_list() -> obtener solo los lista de valores de la columna rating
    # flat=True => lista plana (no de tuplas)
    ratings = votes.values_list('rating', flat=True)

    # Calcular la suma de todas las valoraciones y la valoración media:
    total_rating = sum(ratings)
    if vote_count > 0:
        average_rating = 0.0 if total_rating == 0 else total_rating / vote_count
    else:
        average_rating = 0

    context = {
        'vote_count': vote_count,
        'average_rating': average_rating,
    }

    # Renderizar plantilla html --> games/profile.html con datos necesarios
    return render(request, 'games/profile.html', context)


# GET /user_settings -> Formulario de configuración del usuario
# POST /user_settings -> Procesar el formulario de configuración del usuario
def user_settings(request):
    success_message = None  # Inicializamos una variable para el mensaje de éxito

    # Si no está autenticado, redirigir al login:
    if not request.user.is_authenticated:
        messages.error(request, _("Login required to access this page!!!"))
        return redirect('login')

    if request.method == 'POST':
        form = UserSettingsForm(request.POST)
        if form.is_valid():
            # Obtener los datos del formulario de un solo bloque:
            cleaned_data = form.cleaned_data

            # Obtener los datos del diccionario cleaned_data:
            alias = cleaned_data.get('alias')
            font_type = cleaned_data.get('font_type')
            font_size = cleaned_data.get('font_size')

            # Actualizar el perfil del usuario con los nuevos datos:
            if alias:
                request.user.username = alias   # Alias = nombre del usuario
                request.user.save()
            if font_type:
                request.user.profile.font_type = font_type
            if font_size:
                request.user.profile.font_size = font_size

            # Guardar los cambios en la base de datos:
            request.user.profile.save()

            # Asignamos un mensaje de éxito para mostrar en el template:
            success_message = _("Settings updated successfully!")
            # Renderizar con datos actuales en el formulario

    else:
        # Rellenar el formulario con los datos actuales del usuario:
        form = UserSettingsForm(initial={
            'alias': request.user.username,
            'font_type': request.user.profile.font_type,
            'font_size': request.user.profile.font_size
        })

    # Renderizar la plantilla de configuración del usuario con datos actuales en el formulario
    return render(request, 'games/user_settings.html', {'form': form, 'success_message': success_message})


# GET /logout -> Gestionar logout de un usuario
# @login_required -> decorador asegura que solo Users autenticados puedan ejecutar las vistas
@login_required
def logout_view(request):
    # Realizar el logout solo con la solicitud
    logout(request)
    # Redirigir al usuario a la página principal:
    return redirect('main')


# GET /register -> Gestionar el registro de un nuevo usuario:
# POST /register -> Procesar el formulario de registro
def register(request):
    if request.method == 'POST':
        # Procesar el formulario de registro de django recibido con el POST
        form = UserCreationForm(request.POST)
        if form.is_valid():
            # Si es válido (crsf_token) -> crear el User en la base de datos
            form.save()
            messages.success(request, _("Account created successfully! Please log in:"))
            # Redirigir al user al login:
            return redirect('login')

    else:
        # Crear formulario de registro de django y pasarlo a la plantilla:
        form = UserCreationForm()
    # Renderizar la plantilla de registro:
    return render(request, 'games/register.html', {'form': form})


# GET /set-language/<lang_code> -> Cambiar el idioma del usuario: es o en (español o inglés)
def set_language(request, lang_code):
    if lang_code in ['es', 'en']:
        # Detectar la URL anterior (sin repetir un POST) -> hacer get solo
        referer = request.META.get('HTTP_REFERER', '/')
        # Eliminamos query strings o POST data -> para no volver a enviar de nuevo el mismo formulario:
        path = urlparse(referer).path

        # Redirigir al usuario a la misma URL con el nuevo idioma:
        response = redirect(path)
        # Cambiar cookie de idioma:
        response.set_cookie(settings.LANGUAGE_COOKIE_NAME, lang_code)
        # Activar el nuevo idioma en Django -> Solo inglés o español:
        translation.activate(lang_code)
        return response

    # Plantilla de error 404
    return render(request, 'games/404error.html', status=404)