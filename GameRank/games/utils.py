from datetime import datetime

from django.utils.dateparse import parse_date
import json
import urllib.request
import xml.etree.ElementTree as ET
from xml.etree.ElementTree import Element, SubElement, tostring

from .models import Game, Comment, Like


# Funciones auxiliares:
# - cargar juegos desde un archivo XML mediante su DOM
# - cargar juegos desde un archivo JSON mediante json.loads
# - comprobar si un a fecha es válida
# - Parámetros base a pasar a los templates


# Parser XML: cargar juegos desde un archivo XML mediante su DOM --> Listado 1
# Parsear JSON: cargar juegos desde un archivo JSON mediante json.loads --> Listado 2 y 3
# Cargar datos a la base de datos antes de lanzar servidor desde la shell de django
def load_games(formato, url, prefix): # Formato de datos, URL y prefix -> en Strings
    try:
        # Descargar el archivo utilizando urllib -> solicitud HTTP GET a la URL:
        response = urllib.request.urlopen(url)

        if formato == 'XML':
            load_xml(response, prefix)

        elif formato == 'JSON':
            load_json(response, prefix)

        else:
            print("Formato de datos NO reconocido o NO compatible.")
            return

    except Exception as e:
        print(f"Error al descargar el archivo de la API, detalles del error: {e}")


# Específico para XML:
# ej:listado1.xml (prefijo = LIS1-):
# load_games('XML', 'https://gitlab.eif.urjc.es/cursosweb/2024-2025/final-gamerank/-/raw/main/listado1.xml', 'LIS1-')
def load_xml(response, prefix):
    game_data = {}
    try:
        # Leemos y cargamos los datos del XML:
        xml_data = response.read()
        # Extraer el DOM del archivo XML: -> ElementTree
        # Usamos ET.fromstring para analizar el contenido del XML
        # desde el cuerpo de la respuesta (string)
        # Obtener la raíz (root) del árbol del XML-> <games> en listado1.xml(response.content)
        root = ET.fromstring(xml_data)

        # Recorrer todos los juegos del árbol del XML y guardarlos en la base de datos:
        # Buscar todos los elementos <game> dentro de <games> (root)
        for game_element in root.findall('game'):
            # Extraer los datos de cada juego -> Asociado al modelo Game en DB:

            # Extraer la fecha de lanzamiento -> en formato 'YYYY-MM-DD':
            # Bleach Online -> API: listado1.xml -> <release_date>2014-02-30</release_date>
            release_date = game_element.find('release_date').text
            # Verificar si "release_date" existe(!= None ó null) y es una fecha válida:
            if release_date is None or not is_valid_date(release_date):
                release_date = '2025-01-01'  # Fecha por defecto

            # Asumir que todos los campos se aportan en cada elemento <game>:
            game_data = {
                # Asociar a cada clave -> valor que se encuentre
                # en cada elemento marcado dentro de cada elemento <game>:
                # ej -> <id>1</id> -> game_data['id'] = 'LIS1-1'
                # Prefijo LIS1- añadido al ID -> listado1.xml
                'id': prefix + game_element.find('id').text,
                'title': game_element.find('title').text,
                'platform': game_element.find('platform').text,
                'genre': game_element.find('genre').text,
                'developer': game_element.find('developer').text,
                'publisher': game_element.find('publisher').text,
                'release_date': parse_date(release_date),
                'description': game_element.find('short_description').text,
                'average_rating': 0.0,
                'vote_count': 0,
                'freetogame_profile_url': game_element.find('freetogame_profile_url').text,
                'game_url': game_element.find('game_url').text,
                'thumbnail': game_element.find('thumbnail').text,
            }

            # Verificar si el juego ya existe en la base de datos para crearlo
            # ¡¡Si existe => id o title => NO se crea ni actualiza!!
            # Muchos menos tiempo y accesos a la base de datos
            if (not Game.objects.filter(id=game_data['id']).exists()
                    and not Game.objects.filter(title=game_data['title']).exists()):
                # Si no existe -> crear el juego
                # Pasarle **game_data para desempaquetar el diccionario -> enviar parejas -> clave:valor
                Game.objects.create(**game_data)
                print(f"Juego '{game_data['title']}' guardado con éxito desde la API de formato XML")

    except Exception as e:
        print(f"Error al guardar el juego '{game_data['title']}': {e}")


# Específico para JSON:
# ej:API de FreeToGame (Prefijo = LIS2-):
# load_games('JSON', 'https://www.freetogame.com/api/games', 'LIS2-')
# ej:API de MMOBomb (Prefijo = LIS3-):
# load_games('JSON', 'https://www.mmobomb.com/api1/games', 'LIS3-')
def load_json(response, prefix):
    game_data = {}
    try:
        # Leer los datos de la respuesta en formato de JSON:
        # response.read() para leer los datos binarios de la respuesta
        # json.loads() para convertirlos a un diccionario de Python
        games = json.loads(response.read())

        # Recorrer los juegos extraídos y guardarlos en la base de datos
        # Guardar sus campos del diccionario también
        for game_data in games:
            # Añadir prefijo correspondiente a la API, en la clave primaria:
            game_data['id'] = prefix + str(game_data['id'])

            # Verificar si "release_date" existe(!= None ó null) y es una fecha válida
            # Pocket Starships -> API: MMOBomb -> "release_date": null
            # Pocket Starships -> API: FreeToGame -> "release_date": "2014-03-00"
            release_date = game_data.get('release_date')
            if release_date is None or not is_valid_date(release_date):
                release_date = '2025-01-01'  # Fecha por defecto

            # Guardar juego con sus campos -> si NO existe (id o title) en la base de datos:
            # Usar update_or_create() -> pesado --> muchos accesos a la base de datos
            if (not Game.objects.filter(id=game_data['id']).exists()
                    and not Game.objects.filter(title=game_data['title']).exists()):
                Game.objects.create(
                    id=game_data['id'],
                    title=game_data.get('title'),
                    platform=game_data.get('platform'),
                    genre=game_data.get('genre'),
                    developer=game_data.get('developer'),
                    publisher=game_data.get('publisher'),
                    release_date=release_date,
                    description=game_data.get('short_description'),
                    average_rating=0.0,
                    vote_count=0,
                    # APIs -> distintos campos en el JSON:
                    # freetogame_profile_url -> FreeToGame
                    # game_url -> MMOBomb
                    freetogame_profile_url=game_data.get('freetogame_profile_url') or game_data.get('profile_url'),
                    game_url=game_data.get('game_url'),
                    thumbnail=game_data.get('thumbnail'),
                )
                print(f"Juego '{game_data['title']}' guardado con éxito desde la API de formato JSON")

    except Exception as e:
        print(f"Error al guardar el juego '{game_data['title']}': {e}")


# Función para validar si una fecha es válida
def is_valid_date(date_str):
    try:
        # Intentamos convertir la fecha de formato 'YYYY-MM-DD' a un objeto datetime
        datetime.strptime(date_str, '%Y-%m-%d')
        return True
    except ValueError:
        # Si hay un error, la fecha no es válida ó formato incorrecto
        return False
