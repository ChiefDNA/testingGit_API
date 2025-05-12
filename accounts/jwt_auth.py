from datetime import datetime, timedelta, timezone
from django.conf import settings
from .models import Accounts
import jwt


def generate_jwt(account):
    payload = {
        'id' : account.id,
        'username' : account.username,
        'exp' : datetime.now(timezone.utc) + timedelta(minutes=30),
        'iat' : datetime.now(timezone.utc),
    }
    token = jwt.encode(payload, settings.SECRET_KEY, algorithm='HS256')
    return token

def decode_jwt(token):
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=['HS256'])
        user = Accounts.object.get(id=payload['id'])
        return user
    except (jwt.ExpiredSignatureError, jwt.DecodeError, Accounts.DoesNotExist):
        return None