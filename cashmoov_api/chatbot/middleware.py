import logging
from urllib.parse import parse_qs

from asgiref.sync import sync_to_async
from channels.middleware import BaseMiddleware

logger = logging.getLogger(__name__)


@sync_to_async
def get_user_from_token(token):
    from rest_framework_simplejwt.authentication import JWTAuthentication

    jwt_auth = JWTAuthentication()
    validated_token = jwt_auth.get_validated_token(token)
    return jwt_auth.get_user(validated_token)


class JWTAuthMiddleware(BaseMiddleware):
    async def __call__(self, scope, receive, send):
        from django.contrib.auth.models import AnonymousUser

        scope["user"] = AnonymousUser()

        query_string = scope.get("query_string", b"").decode()
        params = parse_qs(query_string)

        token_list = params.get("token")
        if token_list:
            try:
                scope["user"] = await get_user_from_token(token_list[0])
            except Exception as e:
                logger.error("JWT WebSocket authentication error: %s", e)

        return await super().__call__(scope, receive, send)
