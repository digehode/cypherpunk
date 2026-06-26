from django.apps import AppConfig


class CypherpunkConfig(AppConfig):
    name = "cypherpunk"

    def ready(self):
        # This runs AFTER all models.py files in the project are loaded.

        # Get the content of modules so that the models in there are
        # part of the app_name
        from . import modules  # noqa: F401
