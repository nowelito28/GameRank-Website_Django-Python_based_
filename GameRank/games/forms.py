from django import forms
from django.utils.translation import gettext_lazy as _
# Gettext_lazy -> Para internacionalización en models y forms
# -> porque al crear los models y los forms -> puede que los .po y .mo no estén creados

# Gestión de formularios de la app:

# Formulario para valorar y comentar un juego:
class RatingCommentForm(forms.Form):        # Se puede enviar formulario con valoración y/o comentario, pero no vacío
    rating = forms.IntegerField(            # Campo de tipo entero del formulario -> valoración
        required=False,         # Campo no obligatorio
        min_value=0,        # Valor mínimo
        max_value=5,        # Valor máximo
        label=_("Rating range (0-5), 0 is the worst and 5 is the best. Only 1 vote per user:"),
        widget=forms.NumberInput(
            attrs={'class': 'form-control'}
        ),
    )
    text = forms.CharField(                 # Campo de tipo cadena del formulario -> comentario
        required=False,         # Campo no obligatorio
        label=_("Comment your opinion about this game, with or whitout rating (optional):"),
        widget=forms.Textarea(attrs={   # Atributos de este campo
            'class': 'form-control',
            'placeholder': _('Write your comment...'),
            'rows': 4
        }),
    )


# Formulario para editar perfil del user:
class UserSettingsForm(forms.Form):
    # Cambio de alias: string
    alias = forms.CharField(max_length=100, required=False, label=_('Alias'))
    # form.ChoiceField() -> Permite elegir un elemento de una lista
    # -> (value -> valor real que se guarda en la BD, label -> texto que se muestra)
    # Cambio de tipo y tamaño de letra:
    font_type = forms.ChoiceField(choices=[('Arial', 'Arial'), ('Times New Roman', 'Times New Roman'),
                                           ('Courier', 'Courier'), ('Verdana', 'Verdana'),
                                           ('Georgia', 'Georgia'), ('Tahoma', 'Tahoma'), ('Helvetica', 'Helvetica'),
                                           ('Comic Sans MS', 'Comic Sans MS')], label=_('Font Type'))
    font_size = forms.ChoiceField(choices=[ ('10px', _('Tiny')),  ('14px', _('Small')), ('18px', _('Medium')),
                                            ('22px', _('Big')), ('26px', _('Gigantic'))],label=_('Font Size'))


# Formulario para login de password global de acceso --> Middleware:
class PasswordAuthForm(forms.Form):
    # Password de acceso -> string
    # widget=forms.PasswordInput -> Oculta la contraseña -> renderiza <input type="password">
    password = forms.CharField(widget=forms.PasswordInput, label=_("Access Password"))
