from django.contrib import admin
from django.contrib.auth import admin as auth_admin
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _

from oneshot_guessle.users.forms import UserAdminChangeForm, UserAdminCreationForm

User = get_user_model()


@admin.register(User)
class UserAdmin(auth_admin.UserAdmin):
    form = UserAdminChangeForm
    add_form = UserAdminCreationForm
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'password1', 'password2'),
        }),
    )
    fieldsets = (
        (None, {"fields": ("username", "password")}),
        (_("Personal info"), {"fields": ("name", "email", "image","supporter", "no_ads")}),
        (_("Oneshot Stats"), {"fields": ("dayscorrect","daysincorrect","misseddays","streak","highestStreak","stars")}),
        (_("Tangle Stats"), {"fields": ("totalTanglePointsEver",)}),
        (_("Cows & Bulls Stats"), {"fields": ("cows_bulls_points", "cows_bulls_attempts")}),
        (
            _("Permissions"),
            {
                "fields": (
                    "is_active",
                    "is_staff",
                    "is_superuser",
                    "groups",
                    "user_permissions",
                ),
            },
        ),
        (_("Important dates"), {"fields": ("last_login", "date_joined")}),
    )
    list_display = ["username","name","email","stars", "date_joined", "supporter", "no_ads","is_superuser"]
    actions=['add_supporter','remove_supporter', 'show_ads', 'disable_ads']
    search_fields = ["name"]

    @admin.action(description='Add as supporter')
    def add_supporter(self, request, queryset):
        queryset.update(supporter=True)

    @admin.action(description='Remove as supporter')
    def remove_supporter(self, request, queryset):
        queryset.update(supporter=False)
    
    @admin.action(description='Enable ads')
    def show_ads(self, request, queryset):
        queryset.update(no_ads=False)

    @admin.action(description='disable ads')
    def disable_ads(self, request, queryset):
        queryset.update(no_ads=True)