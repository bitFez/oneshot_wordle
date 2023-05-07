from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class UsersConfig(AppConfig):
    name = "oneshot_guessle.users"
    verbose_name = _("Users")

    def ready(self):
        try:
            import oneshot_guessle.users.signals  # noqa F401
        except ImportError:
            pass
