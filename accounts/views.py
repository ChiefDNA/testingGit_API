from rest_framework import viewsets
from .models import Accounts
from rest_framework import response
from rest_framework.views import APIView
from .serializers import AccountsSerializers

# Create your views here.
class AccountsViewSet(viewsets.ModelViewSet):
    queryset = Accounts.objects.all()
    serializer_class = AccountsSerializers


class RegisterView(APIView):
    def post(self, requets):
        return "Succesful"


#   use django data structures
#  use dictionaries and list to store data (objects)