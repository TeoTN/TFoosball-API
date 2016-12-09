from django.apps import AppConfig


class TFoosballConfig(AppConfig):
    name = 'tfoosball'

    def ready(self):
        import tfoosball.signals
