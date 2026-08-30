import base64

from rest_framework import authentication, exceptions
from werkzeug.security import check_password_hash

from .models import User


class ExistingUserBasicAuthentication(authentication.BaseAuthentication):
    """Authenticate against the existing users table used by the Flask app.

    This lets Postman and the future frontend use the same credentials without
    creating a second Django user table during the migration.
    """

    www_authenticate_realm = "api"

    def authenticate(self, request):
        header = request.META.get("HTTP_AUTHORIZATION", "")
        if not header.startswith("Basic "):
            return None

        try:
            decoded = base64.b64decode(header[6:]).decode("utf-8")
            username, password = decoded.split(":", 1)
        except (ValueError, UnicodeDecodeError, base64.binascii.Error) as exc:
            raise exceptions.AuthenticationFailed("Invalid Basic authentication header") from exc

        user = User.objects.filter(username=username).first()
        if user is None:
            user = User.objects.filter(email=username).first()

        if user is None or not check_password_hash(user.password_hash, password):
            raise exceptions.AuthenticationFailed("Invalid username or password")

        return user, None

    def authenticate_header(self, request):
        return f'Basic realm="{self.www_authenticate_realm}"'
