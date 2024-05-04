from django.apps import AppConfig


class CoreConfig(AppConfig):
    name = 'core'
    icon = 'fa fa-home'
    
    def ready(self):
        import core.signals
