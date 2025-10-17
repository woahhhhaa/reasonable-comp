import hmac
import time
from hashlib import sha256
from urllib.parse import urlencode


def _sign(message: str, secret: str) -> str:
    mac = hmac.new(secret.encode("utf-8"), message.encode("utf-8"), sha256)
    return mac.hexdigest()


def sign_url(base: str, path: str, ttl_seconds: int, secret: str) -> str:
    """Return a signed URL of the form: {base}{path}?exp=...&sig=...

    The signature covers the path and the expiration timestamp: f"{path}|{exp}"
    """
    now = int(time.time())
    exp = now + max(int(ttl_seconds), 1)
    message = f"{path}|{exp}"
    sig = _sign(message, secret)
    qs = urlencode({"exp": exp, "sig": sig})
    return f"{base}{path}?{qs}"


