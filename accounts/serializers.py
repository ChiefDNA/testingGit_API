from rest_framework import serializers
from .models import Accounts

class AccountsSerializers(serializers.ModelSerializer):
    class Meta:
        model = Accounts
        fields = '__all__'