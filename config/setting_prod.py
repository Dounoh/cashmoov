from config.settings import *

USE_X_FORWARDED_HOST = True
SECURE_SSL_REDIRECT = False
CSRF_TRUSTED_ORIGINS = ["https://dev-dounoh.xyz"]
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
CI=False
DEBUG=False