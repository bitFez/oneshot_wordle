from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class UsersConfig(AppConfig):
    name = "oneshot_wordle.users"
    verbose_name = _("Users")

    def ready(self):
        try:
            import oneshot_wordle.users.signals  # noqa F401
        except ImportError:
            pass
