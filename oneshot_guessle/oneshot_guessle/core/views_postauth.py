from django.shortcuts import redirect
from django.urls import reverse

def post_auth_redirect(request):
    """Redirect after login/logout based on previous page.

    If the referring URL path starts with the c_cipher prefix ('/cc/'),
    redirect to the c_cipher index. Otherwise send to `game:home`.
    """
    referer = request.META.get("HTTP_REFERER", "")
    # Basic check: if referer contains '/cc/' path, send to c_cipher
    if "/cc/" in referer:
        return redirect(reverse("c_cipher:c_index"))
    return redirect(reverse("game:home"))
