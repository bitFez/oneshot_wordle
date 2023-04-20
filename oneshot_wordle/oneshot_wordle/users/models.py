from django.contrib.auth.models import AbstractUser
from django.db.models import CharField, IntegerField,ImageField
from django.urls import reverse
from django.utils.translation import gettext_lazy as _


class User(AbstractUser):
    """
    Default custom user model for Oneshot Wordle.
    If adding fields that need to be filled at user signup,
    check forms.SignupForm and forms.SocialSignupForms accordingly.
    """

    #: First and last name do not cover name patterns around the globe
    name = CharField(_("Name of User"), blank=True, max_length=255)
    first_name = None  # type: ignore
    last_name = None  # type: ignore
    dayscorrect = IntegerField(default=0)
    daysincorrect = IntegerField(default=0)
    misseddays = IntegerField(default=0)
    streak = IntegerField(default=0)
    image = ImageField(upload_to='images/profile_pics', null=True, blank=True, default="images/avatar.png", help_text=('Choose your avatar'), verbose_name=('Profile Picture'))


    def get_absolute_url(self):
        """Get url for user's detail view.

        Returns:
            str: URL for user detail.

        """
        return reverse("users:detail", kwargs={"username": self.username})
