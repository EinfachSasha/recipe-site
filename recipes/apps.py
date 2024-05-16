from django.apps import AppConfig


class RecipesConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'recipes'
    
class ProfilesConfig(AppConfig):
    name = 'profiles'

    def ready(self):
        import profiles.signals
