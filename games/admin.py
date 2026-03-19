from django.contrib import admin

from .models import Game, Comment, UserGameFollow, Profile, ValidPassword, Like

# Register your models here.
# Registrar todos los modelos para que sea visible en el panel de admin:
admin.site.register(Game)
admin.site.register(Comment)
admin.site.register(UserGameFollow)
admin.site.register(Profile)
admin.site.register(ValidPassword)
admin.site.register(Like)