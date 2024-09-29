from django.apps import AppConfig

class loginConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'modulos.login'

    def ready(self):
        import modulos.login.signals