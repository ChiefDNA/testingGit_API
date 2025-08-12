from rest_framework import serializers
from .models import Accounts
from django.contrib.auth.hashers import make_password

class AccountsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Accounts
        fields = ['id','username','contact','address','dateOfBirth', 'company', 'role','password']

    def validate_password(self, value:str) -> str:
        #store pasword in hash
        return make_password(value)