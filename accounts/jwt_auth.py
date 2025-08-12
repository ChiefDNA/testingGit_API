from datetime import datetime, timedelta, timezone
from django.conf import settings
from .models import Accounts
import jwt


def generate_jwt(account):
    payload = {
        'id' : account.id,
        'username' : account.username,
        'role' :account.role,
        'exp' : datetime.now(timezone.utc) + timedelta(minutes=120),
        'iat' : datetime.now(timezone.utc),
    }
    token = jwt.encode(payload, settings.SECRET_KEY, algorithm='HS256')
    return token

def decode_jwt(token):
    print(token)
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=['HS256'])
        user = Accounts.objects.get(id=payload['id'])
        return user
    except jwt.ExpiredSignatureError:
        print("JWT expired")
        return None
    except jwt.DecodeError:
        print("JWT decode error")
        return None
    except Accounts.DoesNotExist:
        print("User does not exist with given ID")
        return None