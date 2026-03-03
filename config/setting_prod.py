from config.settings import *

USE_X_FORWARDED_HOST = True
SECURE_SSL_REDIRECT = False
CSRF_TRUSTED_ORIGINS = ["https://dev-dounoh.xyz","https://api.dev-dounoh.xyz"]
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
CI=False
DEBUG=False
CORS_ALLOWED_ORIGINS = [
    "http://localhost:3000",
    "https://dev-dounoh.xyz",
    "https://cash-moov.vercel.app",
]
# CORS_ALLOW_ALL_ORIGINS = True
CORS_ALLOW_CREDENTIALS = True
CORS_ALLOW_METHODS = [
    "GET",
    "POST",
    "PUT",
    "PATCH",
    "DELETE",
    "OPTIONS",
]
