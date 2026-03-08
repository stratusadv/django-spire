import hashlib
import hmac

from django_spire.conf import settings


def hash_string(value: str) -> str:
    return hmac.new(
        settings.SECRET_KEY.encode(),
        value.encode(),
        hashlib.sha256
    ).hexdigest()
