from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from django.utils.translation import gettext as _, activate

from .models import Game, Comment, UserGameFollow, ValidPassword


class GameRankTests(TestCase):

    def setUp(self):
        # Crear user:
        self.user = User.objects.create_user(username="testuser", password="testpass")

        # Simular login por contraseña global:
        ValidPassword.objects.create(value="123")
        # reverse("global_login") → devuelve URL "/global_login" de la app
        response = self.client.post(reverse("global_login"), {"password": "123"})
        self.assertEqual(response.status_code, 302)
        # Asegurarse de que la cookie esté activa:
        self.client.cookies["global_pass"] = "123"

        # Hacer logueo personal del user -> user relacionado con el client:
        self.client.login(username="testuser", password="testpass")

        self.game = Game.objects.create(
            id="LIS-0001", title="Game Of Thrones Winter Is Coming", genre="Strategy",
            platform="PC", publisher="HBO", developer="HBO Devs",
            release_date="2020-01-01", description="Test game",
            freetogame_profile_url="https://example.com", game_url="https://example.com",
            thumbnail="https://example.com"
        )



    def test_home_page(self):
        # reverse("main") → devuelve URL "/" de la app
        response = self.client.get(reverse("main"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Game Of Thrones Winter Is Coming")


    def test_game_detail(self):
        # reverse("game_detail", args=[self.game.id]) → devuelve URL "/<game_id>" de la app
        response = self.client.get(reverse("game_detail", args=[self.game.id]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.game.title)


    def test_game_json(self):
        # reverse("game_json", args=[self.game.id]) → devuelve URL "/<game_id>.json" de la app
        response = self.client.get(reverse("game_json", args=[self.game.id]))
        self.assertEqual(response.status_code, 200)
        # Ver si un campo de la respuesta de json tiene el nombre correspondiente
        self.assertEqual(response.json()["title"], "Game Of Thrones Winter Is Coming")

    def test_game_xml(self):
        # reverse("game_xml", args=[self.game.id]) → devuelve URL "/<game_id>.xml" de la app
        response = self.client.get(reverse("game_xml", args=[self.game.id]))
        self.assertEqual(response.status_code, 200)
        # Asegurar que es un XML
        self.assertIn(b"<game>", response.content)
        self.assertIn(b"<title>Game Of Thrones Winter Is Coming</title>", response.content)
        self.assertIn(b"</game>", response.content)


    def test_rate_game(self):
        # 1º -> Solo comentario:
        # reverse("game_detail", args=[self.game.id]) → devuelve URL "/<game_id>" de la app
        # pasar en el body el formulario --> {"text": "Good game!!"}
        response = self.client.post(reverse("game_detail", args=[self.game.id]), {"text": "Good game!!"})
        self.assertEqual(response.status_code, 200)

        # 2º -> Solo valoración:
        # reverse("game_detail", args=[self.game.id]) → devuelve URL "/<game_id>" de la app
        # pasar en el body el formulario --> {"rating": 4}
        response = self.client.post(reverse("game_detail", args=[self.game.id]), {"rating": 4})
        self.assertEqual(response.status_code, 200)

        # 3º -> Valoración y comentario:
        # reverse("game_detail", args=[self.game.id]) → devuelve URL "/<game_id>" de la app
        # pasar en el body el formulario --> {"rating": 5, "text": "So great game!!"}
        response = self.client.post(reverse("game_detail", args=[self.game.id]), {"rating": 5, "text": "So great game!!"})
        self.assertEqual(response.status_code, 200)

        # 4º -> Comentario y valoración vacíos:
        response = self.client.post(
            reverse('game_detail', args=[self.game.id]),
            data={'rate_comment': 'true'}           # No se envía campos 'rating' ni 'text'
        )
        self.assertEqual(response.status_code, 401)
        self.assertContains(response, _("Please provide a rating and/or a comment!"), status_code=401)


    def test_follow_game(self):
        # reverse("follow_game", args=[self.game.id]) → devuelve URL "/follow_game/<game_id>" de la app
        response = self.client.get(reverse("follow_game", args=[self.game.id]))
        # Renderiza vista informativa
        self.assertEqual(response.status_code, 200)
        self.assertTrue(
            UserGameFollow.objects.filter(user=self.user, game=self.game).exists()
        )


    def test_unfollow_game(self):
        # Crear relación de seguimiento previamente:
        UserGameFollow.objects.create(user=self.user, game=self.game)
        # reverse("unfollow_game", args=[self.game.id]) → devuelve URL "/unfollow_game/<game_id>" de la app
        response = self.client.get(reverse("unfollow_game", args=[self.game.id]))
        # Renderiza vista informativa
        self.assertEqual(response.status_code, 200)
        self.assertFalse(
            UserGameFollow.objects.filter(user=self.user, game=self.game).exists()
        )


    def test_user_profile_page(self):
        # Crear 4 votaciones del usuario sobre 4 juegos distintos
        for score in [2, 3, 4, 5]:
            Comment.objects.create(game=self.game, user=self.user, rating=score)

        # Calcular media manualmente
        expected_media = round((2 + 3 + 4 + 5) / 4, 1)
        expected_count = 4

        # reverse("user_profile") → devuelve URL "/user_profile" de la app
        response = self.client.get(reverse("user_profile"))
        self.assertEqual(response.status_code, 200)

        # Comprobar que la media y el número de votos están en la respuesta
        self.assertContains(response, str(expected_count))  # Número de votaciones
        self.assertContains(response, str(expected_media))  # Media de puntuaciones


    def test_rated_games_page(self):
        # Crear 3 juegos nuevos y añadirles votaciones con comentarios del usuario
        rated_game_ids = []
        for i, score in enumerate([3, 4, 5]):
            game = Game.objects.create(
                id=f"GAME{i}", title=f"Rated Game {i}", genre="Action",
                platform="PC", publisher="Pub", developer="Dev",
                release_date="2024-01-01", description="Great game",
                freetogame_profile_url="https://x", game_url="https://x", thumbnail="https://x"
            )
            rated_game_ids.append(game.id)
            Comment.objects.create(game=game, user=self.user, rating=score)

        # reverse("rated_games") → devuelve URL "/rated_games" de la app
        response = self.client.get(reverse("rated_games"))
        self.assertEqual(response.status_code, 200)

        # Comprobar que aparecen los IDs de todos los juegos votados
        for gid in rated_game_ids:
            self.assertContains(response, gid)

    def test_followed_games_page(self):
        followed_game_ids = []
        for i in range(3):
            game = Game.objects.create(
                id=f"GAMEF{i}", title=f"Followed Game {i}", genre="Strategy",
                platform="PC", publisher="Pub", developer="Dev",
                release_date="2024-01-01", description="Interesting game",
                freetogame_profile_url="https://x", game_url="https://x", thumbnail="https://x"
            )
            followed_game_ids.append(game.id)
            # Añadir relación de seguimiento en la tabla intermedia
            UserGameFollow.objects.create(user=self.user, game=game)

        # reverse("followed_games") → devuelve URL "/followed_games" de la app
        response = self.client.get(reverse("followed_games"))
        self.assertEqual(response.status_code, 200)

        # Comprobar que aparecen los IDs de todos los juegos seguidos
        for gid in followed_game_ids:
            self.assertContains(response, gid)


    def test_user_settings(self):
        # Crear datos válidos como los espera el formulario
        form_data = {
            "alias": "New_Alias",
            "font_size": "medium",
            "font_type": "Arial"
        }

        # reverse("user_settings") → devuelve URL "/user_settings" de la app
        response = self.client.post(reverse("user_settings"), data=form_data)
        self.assertEqual(response.request['PATH_INFO'], reverse("user_settings"))
        self.assertEqual(response.status_code, 200)


    def test_access_without_login_redirects(self):
        self.client.logout()
        self.client.cookies.clear()  # Quitar cookie global_pass si se usaba

        # reverse("user_profile") → devuelve URL "/user_profile" de la app
        # No va a poder al no estar logado ni con cookie global
        response = self.client.get(reverse("user_profile"))
        self.assertEqual(response.status_code, 302)
        # Verificar redirección a la URL de login_global
        self.assertIn(reverse("global_login"), response.url)

        # Simular login por contraseña global:
        # reverse("global_login") → devuelve URL "/global_login" de la app
        response = self.client.post(reverse("global_login"), {"password": "123"})
        self.assertEqual(response.status_code, 302)
        # Asegurarse de que la cookie esté activa:
        self.client.cookies["global_pass"] = "123"
        self.assertEqual(response.status_code, 302)
        # Verificar redirección a la URL del main después del login global
        self.assertIn(reverse("main"), response.url)

        # Intentar acceder a una página protegida con solo la cookie global
        response = self.client.get(reverse("user_profile"))
        self.assertEqual(response.status_code, 302)
        # Verificar redirección a la URL de login
        self.assertIn(reverse("login"), response.url)

        # Login normal por formulario de Django -> AuthenticationForm() (username, password):
        response = self.client.post(reverse("login"), {
            "username": "testuser",
            "password": "testpass"
        })
        self.assertEqual(response.status_code, 302)
        # Verificar redirección a la URL al perfil
        self.assertIn(reverse("user_profile"), response.url)


    def error404(self):
        # reverse("game_detail") → devuelve URL "/<game_id>" de la app => NO existe
        response = self.client.get(reverse("game_detail", args=["NOT_EXIST"]))
        self.assertEqual(response.status_code, 404)


    def test_help_page_accessible(self):
        # reverse("help") → devuelve URL "/help" de la app
        response = self.client.get(reverse("help"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, _("GameRank Help Page"))


    def test_htmx_comments_dynamic(self):
        # reverse("game_detail") → devuelve URL "/<game_id>" con HTMX de la app
        response = self.client.get(
            reverse("game_detail", args=[self.game.id]),
            HTTP_HX_REQUEST="true"
        )
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "games/comments_section.html")


    def test_invalid_json_and_xml_returns_404(self):
        bad_id = "NOT-A-GAME"
        # reverse("game_json") → devuelve URL "/<game_id>.json" de la app
        response_json = self.client.get(f"/{bad_id}.json")
        # reverse("game_xml") → devuelve URL "/<game_id>.xml" de la app
        response_xml = self.client.get(f"/{bad_id}.xml")
        self.assertEqual(response_json.status_code, 404)
        self.assertEqual(response_xml.status_code, 404)


    def test_comment_with_spaces_only_rejected(self):
        # reverse("game_detail") → devuelve URL "/<game_id>" de la app -> Con comentario vacío
        response = self.client.post(
            reverse("game_detail", args=[self.game.id]),
            {"text": "   ", "rate_comment": True}
        )
        self.assertEqual(response.status_code, 401)


    def test_game_filtering_by_genre(self):
        # reverse("main") → devuelve URL "/?platform=...&genre=...&publisher=..." de la app (en este caso solo genre
        response = self.client.get(reverse("main"), {"genre": "Strategy"})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.game.title)

        response = self.client.get(reverse("main"), {"genre": "Shooter"})
        self.assertNotContains(response, self.game.title)

