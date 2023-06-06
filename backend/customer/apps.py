from django.apps import AppConfig


class CustomerConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'backend.customer'

    def ready(self):
        import backend.customer.signals  # noqa