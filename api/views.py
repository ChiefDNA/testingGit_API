from rest_framework import viewsets
from .models import Accounts
from .serializers import AccountsSerializers

# Create your views here.
class AccountsViewSet(viewsets.ModelViewSet):
    queryset = Accounts.objects.all()
    serializer_class = AccountsSerializers