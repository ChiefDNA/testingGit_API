from rest_framework import serializers
from .models import Company 

class CompanySerializer(serializers.ModelSerializer):
    class Meta:
        model = Company
        fields = ['id', 'name', 'address', 'phone_number', 'email', 'image']

    def validate_email(self, value):
        if not value or '@' not in value:
            raise serializers.ValidationError("Invalid email address.")
        return value

    def validate_phone_number(self, value):
        if not value.isdigit() or len(value) < 7 or len(value) > 15:
            raise serializers.ValidationError("Phone number must be numeric and between 7 to 15 digits long.")
        return value