from config.settings import *


CSRF_TRUSTED_ORIGINS = ["https://api.mondomaine.com"]
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
CI=False
DEBUG=False