from urllib.parse import parse_qs
from channels.middleware import BaseMiddleware
from django.contrib.auth.models import AnonymousUser
from rest_framework_simplejwt.tokens import UntypedToken
from rest_framework_simplejwt.authentication import JWTAuthentication
from jwt import InvalidTokenError
from django.db import close_old_connections
import jwt
from django.conf import settings

class JWTAuthMiddleware(BaseMiddleware):
    async def __call__(self, scope, receive, send):
        headers = dict(scope['headers'])
        cookies = {}

        if b'cookie' in headers:
            raw_cookie = headers[b'cookie'].decode()
            for part in raw_cookie.split(';'):
                if '=' in part:
                    key, value = part.strip().split('=', 1)
                    cookies[key] = value

        token = cookies.get('access_token')
        if token:
            try:
                validated_token = UntypedToken(token)
                user = JWTAuthentication().get_user(validated_token)
                scope['user'] = user
            except (InvalidTokenError, jwt.ExpiredSignatureError):
                scope['user'] = AnonymousUser()
        else:
            scope['user'] = AnonymousUser()

        close_old_connections()
        return await super().__call__(scope, receive, send)

