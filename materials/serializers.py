from rest_framework import serializers
from .models import MaterialType, Material, MaterialUsage, Supplier


class MaterialTypeSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = MaterialType
        fields = ['id', 'name']


class SupplierSerializer(serializers.ModelSerializer):

    class meta:
        model = Supplier
        fields = ['id', 'name', 'contact_info']


class MaterialSerializer(serializers.ModelSerializer):

    class Meta:
        model = Material
        fields = ['id', 'name', 'type', 'supplier', 'unit_cost', 'total_quantity', 'date_added', 'added_by']
        read_only_fields = ['added_by', 'date_added']


class MaterialUsageSerializer(serializers.ModelSerializer):

    class Meta:
        model = MaterialUsage
        fields = ['id', 'material', 'date', 'quatity_used']